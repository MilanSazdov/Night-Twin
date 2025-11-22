# backend/app/main.py

from __future__ import annotations

from typing import List
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Fallback: allow direct execution (python backend/app/main.py) by injecting backend dir.
try:
    from app.models import (
        SearchRequest,
        VenueResult,
        PromptSearchRequest,
        PromptSearchResponse,
    )
    from app.services.search_engine import (
        NightTwinSearchEngine,
        SearchQueryParams,
        GuardedSearchResult,
    )
    from app.services.prompt_parser import PromptParser
except ModuleNotFoundError:  # running as a plain script, not with backend on PYTHONPATH
    import sys, pathlib
    _backend_dir_for_path = pathlib.Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(_backend_dir_for_path))
    from app.models import (
        SearchRequest,
        VenueResult,
        PromptSearchRequest,
        PromptSearchResponse,
    )
    from app.services.search_engine import (
        NightTwinSearchEngine,
        SearchQueryParams,
        GuardedSearchResult,
    )
    from app.services.prompt_parser import PromptParser


# Simple .env loader (dependency-free)
def load_dotenv(path: Path) -> None:
    """Load simple KEY=VALUE pairs from a .env file into os.environ."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()
        # strip optional surrounding quotes
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        # don't override already set env vars (explicit wins)
        if key not in os.environ:
            os.environ[key] = val


# Load .env from backend directory
_backend_dir = Path(__file__).resolve().parent.parent
_dotenv_path = _backend_dir / ".env"
if _dotenv_path.exists():
    load_dotenv(_dotenv_path)

app = FastAPI(
    title="NightTwin API",
    version="1.0.0",
    description="AI-powered nightlife twin finder for Serbian venues.",
)

# Allow frontend (for hackathon it's okay to use '*')
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

search_engine: NightTwinSearchEngine | None = None
prompt_parser: PromptParser | None = None


@app.on_event("startup")
def startup_event() -> None:
    """
    Initialize the NightTwinSearchEngine and PromptParser once
    when the FastAPI app starts.
    """
    global search_engine, prompt_parser
    search_engine = NightTwinSearchEngine()
    prompt_parser = PromptParser()


@app.get("/health")
def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}


if __name__ == "__main__":
    # Allow `python backend/app/main.py [PORT]` for quick local testing.
    try:
        import uvicorn  # type: ignore
    except ModuleNotFoundError:
        import sys
        msg = (
            "uvicorn is not installed in this Python.\n"
            "Run the server with your project venv instead, e.g.:\n"
            "  & \"C:\\Users\\milan\\OneDrive\\Desktop\\AI Hakaton\\Night-Twin\\.venv\\Scripts\\python.exe\" backend\\run_server.py\n"
            "or install uvicorn in this Python:  python -m pip install uvicorn[standard]"
        )
        print(msg)
        sys.exit(1)

    import sys as _sys

    # Support overriding port via CLI arg or PORT env var
    _port_str = None
    if len(_sys.argv) > 1:
        _port_str = _sys.argv[1]
    if not _port_str:
        _port_str = os.getenv("PORT")
    try:
        _port = int(_port_str) if _port_str else 8000
    except Exception:
        _port = 8000

    print(f"[main] Running development server at http://127.0.0.1:{_port} (reload OFF)")
    try:
        uvicorn.run("app.main:app", host="127.0.0.1", port=_port, reload=False)
    except OSError as e:
        # Windows: WinError 10048 = address in use; Linux: Errno 98
        winerr = getattr(e, "winerror", None)
        errno = getattr(e, "errno", None)
        if winerr == 10048 or errno == 98:
            print(
                f"Port {_port} is already in use. Try:  python backend\\app\\main.py {_port+1}  \n"
                f"Or stop the other server (Ctrl+C in its terminal), or run run_server.py which uses reload."
            )
        raise


@app.post("/search", response_model=List[VenueResult])
def search_structured(req: SearchRequest):
    """
    Structured search endpoint.
    Frontend sends already structured parameters (city, day, time, etc.),
    we simply map them into SearchQueryParams and call the search engine.
    """
    assert search_engine is not None, "Search engine not initialized"

    q = SearchQueryParams(
        city=req.city,
        day_of_week=req.day_of_week,
        time=req.time,
        group_size=req.group_size,
        budget_level=req.budget_level,
        party_level=req.party_level,
        tags=req.tags,
    )

    results = search_engine.search(q)

    api_results: List[VenueResult] = []
    for r in results:
        api_results.append(
            VenueResult(
                venue_id=r.venue_id,
                name=r.name,
                city=r.city,
                area=r.area,
                venue_type=r.venue_type,
                score=r.score,
                reasons=r.reasons,
            )
        )
    return api_results


@app.post("/prompt-search", response_model=PromptSearchResponse)
def prompt_search(req: PromptSearchRequest):
    """
    Prompt-based search endpoint.

    Flow:
      1. User sends a free-text prompt (natural language).
      2. PromptParser (GPT) extracts structured query (SearchRequest).
      3. NightTwinSearchEngine runs search_with_prompt_guardrail()
         which can decide:
           - "ok"        -> good prompt, we return venues.
           - "no_match"  -> no sufficiently similar nights.
           - "too_broad" -> too many very similar nights.
      4. We return PromptSearchResponse with status, reason, parsed_query and venues.
    """
    assert search_engine is not None, "Search engine not initialized"
    assert prompt_parser is not None, "Prompt parser not initialized"

    # 1) Parse free-text prompt with GPT
    parsed = prompt_parser.parse_prompt(req.prompt)

    if not parsed.valid:
        # Not even a valid nightlife request
        return PromptSearchResponse(
            status="invalid",
            reason="Your prompt does not look like a nightlife request in Serbia.",
            parsed_query=None,
            venues=[],
        )

    # 2) Convert ParsedPrompt -> SearchRequest (with reasonable fallbacks)
    search_req = prompt_parser.to_search_request(parsed)
    if search_req is None:
        return PromptSearchResponse(
            status="invalid",
            reason="Could not extract a meaningful query from your prompt.",
            parsed_query=None,
            venues=[],
        )

    # 3) Map into engine-level query params
    q = SearchQueryParams(
        city=search_req.city,
        day_of_week=search_req.day_of_week,
        time=search_req.time,
        group_size=search_req.group_size,
        budget_level=search_req.budget_level,
        party_level=search_req.party_level,
        tags=search_req.tags,
    )

    # 4) Run guarded search
    guarded: GuardedSearchResult = search_engine.search_with_prompt_guardrail(q)

    # 5) If prompt is bad (too broad or no match) -> return status and explanation
    if guarded.status != "ok":
        return PromptSearchResponse(
            status=guarded.status,
            reason=guarded.reason,
            parsed_query=search_req,
            venues=[],
        )

    # 6) Map internal results to API models
    venue_results: List[VenueResult] = []
    for v in guarded.venues:
        venue_results.append(
            VenueResult(
                venue_id=v.venue_id,
                name=v.name,
                city=v.city,
                area=v.area,
                venue_type=v.venue_type,
                score=v.score,
                reasons=v.reasons,
            )
        )

    return PromptSearchResponse(
        status="ok",
        reason=guarded.reason,
        parsed_query=search_req,
        venues=venue_results,
    )
