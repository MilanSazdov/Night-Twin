# backend/app/models.py

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """
    Structured search request used by the /search endpoint.
    Typically built either directly from the frontend form
    or via the prompt parser (/prompt-search).
    """
    city: str
    day_of_week: str      # e.g. "Friday"
    time: str             # "HH:MM" 24h format
    group_size: int
    budget_level: int     # 1–5
    party_level: int      # 1–5
    tags: List[str] = Field(default_factory=list)  # e.g. ["kafana", "live music"]


class VenueResult(BaseModel):
    """
    One recommended venue returned by the search engine.
    """
    venue_id: int
    name: str
    city: str
    area: str
    venue_type: str
    score: float
    reasons: List[str]


class PromptSearchRequest(BaseModel):
    """
    Request body for /prompt-search endpoint.
    The user provides a free-text prompt describing the night out.
    """
    prompt: str


class PromptSearchResponse(BaseModel):
    """
    Response for /prompt-search endpoint.

    status:
      - "ok":           prompt is good, venues contain recommendations
      - "too_broad":    prompt matches too many nights, user should narrow it
      - "no_match":     no sufficiently similar nights, user should change request
      - "invalid":      prompt is not a valid nightlife request
    """
    status: str                    # "ok" | "too_broad" | "no_match" | "invalid"
    reason: Optional[str] = None   # human-readable explanation
    parsed_query: Optional[SearchRequest] = None
    venues: List[VenueResult] = Field(default_factory=list)
