#!/usr/bin/env python
"""Convenience launcher for the NightTwin FastAPI server.

Instead of typing the uvicorn command manually you can just run:

    python run_server.py

Features:
  * Auto-load .env (OPENAI_API_KEY etc.) if present.
  * Graceful shutdown (suppresses the long KeyboardInterrupt traceback).
  * Reload enabled for dev by default.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
import uvicorn


def load_dotenv(path: Path) -> None:
    """Minimal .env loader (KEY=VALUE per line)."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key not in os.environ:
            os.environ[key] = val


def main() -> None:
    backend_dir = Path(__file__).parent
    dotenv_path = backend_dir / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
    # Allow overriding port via CLI arg or PORT env var
    port_env = os.getenv("PORT")
    port_arg = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        port = int(port_arg or port_env or 8000)
    except Exception:
        port = 8000

    print(f"[run_server] Starting NightTwin API on http://127.0.0.1:{port} (reload ON)")
    try:
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=port,
            reload=True,
            reload_dirs=[str(backend_dir)],
            log_level="info",
        )
    except OSError as e:
        winerr = getattr(e, "winerror", None)
        errno = getattr(e, "errno", None)
        if winerr == 10048 or errno == 98:
            print(
                f"[run_server] Port {port} is already in use. Try another port, e.g.:\n"
                f"  & \"..\\.venv\\Scripts\\python.exe\" run_server.py {port+1} \n"
                f"or set $env:PORT={port+1} and rerun."
            )
        raise
    except KeyboardInterrupt:
        print("\n[run_server] Server stopped (KeyboardInterrupt). Bye!")


if __name__ == "__main__":
    main()
