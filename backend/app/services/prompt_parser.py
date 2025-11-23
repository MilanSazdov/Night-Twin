# backend/app/services/prompt_parser.py

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ValidationError, Field
from openai import OpenAI
import os

from app.models import SearchRequest


SYSTEM_PROMPT = """
You are a structured query extractor for a nightlife recommendation engine in Serbia.

The user describes how they want to go out:
- city (e.g. Belgrade, Novi Sad, Nis, Kragujevac, Subotica, Sombor, Zlatibor, Kraljevo)
- day of week or something like "tomorrow", "this Friday" (convert to a day name)
- time (e.g. "2am", "23:30", "around midnight") -> convert to HH:MM 24h format
- group size (how many people)
- budget (map to level 1-5: 1=very cheap, 5=very expensive)
- party level (map to level 1-5: 1=very chill, 5=very crazy)
- tags: short vibe descriptors like ["kafana","techno","date","live music","crowded","chill","rakija","students"].

You MUST output a single JSON object with fields:

{
  "valid": boolean,
  "city": string | null,
  "day_of_week": string | null,
  "time": string | null,
  "group_size": integer | null,
  "budget_level": integer | null,
  "party_level": integer | null,
  "tags": string[]
}

Rules:
- If the prompt clearly describes a night out in Serbia, set valid = true.
- If the prompt is not about nightlife/going out at all, set valid = false and leave other fields null or empty.
- city: pick from ["Belgrade","Novi Sad","Nis","Kragujevac","Subotica","Sombor","Zlatibor","Kraljevo"] if possible.
- If day_of_week is not explicit, guess a reasonable one (e.g. "Saturday").
- time: convert to "HH:MM" 24h format (e.g. "2am" -> "02:00", "11pm" -> "23:00").
- group_size: if user says "alone" use 1, if "with two friends" -> 3, etc. If unclear, pick 2 or 3.
- budget_level: 1 (very cheap), 3 (medium), 5 (very expensive).
- party_level: 1 (very chill), 3 (normal), 5 (very crazy).
- tags: infer from context (e.g. "rakija", "kafana", "techno", "live music", "crowded", "chill", "date", "rooftop").
"""


class ParsedPrompt(BaseModel):
    """
    Intermediate model for the GPT output.
    """
    valid: bool
    city: Optional[str] = None
    day_of_week: Optional[str] = None
    time: Optional[str] = None
    group_size: Optional[int] = None
    budget_level: Optional[int] = None
    party_level: Optional[int] = None
    tags: List[str] = Field(default_factory=list)


class PromptParser:
    """
    Uses OpenAI GPT model to convert a free-text prompt into a structured SearchRequest.
    """

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set in the environment.")

        # If you run on Yandex Cloud with HTTP(S) proxy, set:
        #   HTTPS_PROXY, HTTP_PROXY environment variables outside this code.
        self.client = OpenAI(api_key=api_key)
        # Mini model is cheap and fast, enough for extraction:
        self.model = "gpt-4.1-mini"

    def parse_prompt(self, prompt: str) -> ParsedPrompt:
        """
        Calls GPT and parses the JSON output into ParsedPrompt.
        """
        resp = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        # The responses API returns a JSON string as text in the first output item.
        raw_json = resp.output[0].content[0].text

        try:
            parsed = ParsedPrompt.model_validate_json(raw_json)
        except ValidationError:
            # In case of a weird model output, fall back to invalid prompt.
            parsed = ParsedPrompt(
                valid=False,
                city=None,
                day_of_week=None,
                time=None,
                group_size=None,
                budget_level=None,
                party_level=None,
                tags=[],
            )

        return parsed

    def to_search_request(self, parsed: ParsedPrompt) -> Optional[SearchRequest]:
        """
        Convert ParsedPrompt into SearchRequest with reasonable fallbacks.
        Return None if parsed.valid is False.
        """
        if not parsed.valid:
            return None

        city = parsed.city or "Belgrade"
        day = parsed.day_of_week or "Saturday"
        time = parsed.time or "22:00"
        group_size = parsed.group_size or 2
        budget_level = parsed.budget_level or 3
        party_level = parsed.party_level or 3
        tags = parsed.tags or []

        return SearchRequest(
            city=city,
            day_of_week=day,
            time=time,
            group_size=group_size,
            budget_level=budget_level,
            party_level=party_level,
            tags=tags,
        )
