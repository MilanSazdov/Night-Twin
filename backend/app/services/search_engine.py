# backend/app/services/search_engine.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Literal, NamedTuple

import json
import math
import os

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field
from openai import OpenAI

# Note: internal API models are in app.models; not required here.


BASE_DIR = Path(__file__).resolve().parents[2]  # backend/
DATA_DIR = BASE_DIR / "data"


# -----------------------------
# Query params used internally by the engine
# -----------------------------

class SearchQueryParams(BaseModel):
    city: str
    day_of_week: str
    time: str             # "HH:MM"
    group_size: int
    budget_level: int     # 1–5
    party_level: int      # 1–5
    tags: List[str] = Field(default_factory=list)


# -----------------------------
# Internal representations
# -----------------------------

@dataclass
class NightRecord:
    night_id: int
    venue_id: int
    city: str
    day_of_week: str
    is_weekend: bool
    struct_features: np.ndarray
    embedding: Optional[np.ndarray]  # None if not computed


@dataclass
class VenueInfo:
    venue_id: int
    name: str
    city: str
    area: str
    venue_type: str
    avg_budget_level: float
    avg_party_level: float
    typical_start_time: str
    typical_end_time: str
    top_vibe_tags: List[str]


@dataclass
class VenueSearchResult:
    venue_id: int
    name: str
    city: str
    area: str
    venue_type: str
    score: float
    reasons: List[str]


class GuardedSearchResult(NamedTuple):
    status: Literal["ok", "too_broad", "no_match"]
    reason: str
    venues: List[VenueSearchResult]


# -----------------------------
# Utility functions
# -----------------------------

def parse_time_to_minutes(time_str: str) -> int:
    """Convert 'HH:MM' to minutes, default to 21:00 if invalid."""
    try:
        h_str, m_str = time_str.strip().split(":")
        h = int(h_str)
        m = int(m_str)
        if not (0 <= h < 24 and 0 <= m < 60):
            raise ValueError()
        return h * 60 + m
    except Exception:
        return 21 * 60


def normalize_numeric(
    value: float,
    min_val: float,
    max_val: float,
    default_fraction: float = 0.5,
) -> float:
    """
    Min-max normalization with clamping.
    If value is NaN, return default_fraction (typically mid-range).
    """
    if math.isnan(value):
        return default_fraction
    if max_val == min_val:
        return default_fraction
    scaled = (value - min_val) / (max_val - min_val)
    return max(0.0, min(1.0, scaled))


def one_hot(value: str, vocab: List[str]) -> List[float]:
    return [1.0 if value == v else 0.0 for v in vocab]


def multi_hot(tags: List[str], vocab: List[str]) -> List[float]:
    vocab_index = {tag: idx for idx, tag in enumerate(vocab)}
    vec = [0.0] * len(vocab)
    for t in tags:
        key = t.lower().strip()
        if key in vocab_index:
            vec[vocab_index[key]] = 1.0
    return vec


def cosine_similarity(a: Optional[np.ndarray], b: Optional[np.ndarray]) -> float:
    if a is None or b is None:
        return 0.0
    if a.shape != b.shape:
        return 0.0
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


# -----------------------------
# Search Engine
# -----------------------------

class NightTwinSearchEngine:
    """
    NightTwinSearchEngine:
    - loads venues.csv and nights_features.jsonl
    - builds in-memory vectors for each night
    - supports:
        - search()                    basic ranking
        - search_with_prompt_guardrail()  adds "bad prompt" detection
    """

    def __init__(self) -> None:
        # Load config and data once
        self.features_config = self._load_features_config()
        self.numeric_ranges = self.features_config.get("numeric_ranges", {})

        self.venues: Dict[int, VenueInfo] = self._load_venues()
        self.nights: List[NightRecord] = self._load_nights_features()

        # Vocabularies (for query feature construction)
        self.cities_vocab = self.features_config["cities"]
        self.days_vocab = self.features_config["days"]
        self.seasons_vocab = self.features_config["seasons"]
        self.location_types_vocab = self.features_config["location_types"]
        self.music_types_vocab = self.features_config["music_types"]
        self.vibe_vocab = self.features_config["vibe_tags"]

        # Numeric ranges
        self._prepare_numeric_defaults()

        # OpenAI client (for query embeddings)
        api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = OpenAI(api_key=api_key) if api_key else None
        self.embedding_model = "text-embedding-3-small"

    # ---------- Loading ----------

    def _load_features_config(self) -> Dict[str, Any]:
        path = DATA_DIR / "features_config.json"
        if not path.exists():
            raise FileNotFoundError(f"features_config.json not found at {path}")
        raw = path.read_text(encoding="utf-8")
        return json.loads(raw)

    def _load_venues(self) -> Dict[int, VenueInfo]:
        path = DATA_DIR / "venues.csv"
        if not path.exists():
            raise FileNotFoundError(f"venues.csv not found at {path}")
        df = pd.read_csv(path)

        venues: Dict[int, VenueInfo] = {}
        for _, row in df.iterrows():
            vid = int(row["venue_id"])
            top_tags_str = str(row.get("top_vibe_tags", "") or "")
            top_tags = [t.strip() for t in top_tags_str.split(",") if t.strip()]

            venues[vid] = VenueInfo(
                venue_id=vid,
                name=str(row["name"]),
                city=str(row["city"]),
                area=str(row["area"]),
                venue_type=str(row["venue_type"]),
                avg_budget_level=float(row.get("avg_budget_level", float("nan"))),
                avg_party_level=float(row.get("avg_party_level", float("nan"))),
                typical_start_time=str(row.get("typical_start_time", "")),
                typical_end_time=str(row.get("typical_end_time", "")),
                top_vibe_tags=top_tags,
            )
        return venues

    def _load_nights_features(self) -> List[NightRecord]:
        path = DATA_DIR / "nights_features.jsonl"
        if not path.exists():
            raise FileNotFoundError(f"nights_features.jsonl not found at {path}")

        nights: List[NightRecord] = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)

                night_id = int(rec["night_id"])
                venue_id = int(rec["venue_id"])
                city = str(rec.get("city", ""))
                day_of_week = str(rec.get("day_of_week", ""))
                is_weekend = day_of_week in ("Friday", "Saturday")

                struct_features = np.array(rec["struct_features"], dtype=np.float32)

                emb_list = rec.get("embedding", [])
                if emb_list:
                    embedding = np.array(emb_list, dtype=np.float32)
                else:
                    embedding = None

                nights.append(
                    NightRecord(
                        night_id=night_id,
                        venue_id=venue_id,
                        city=city,
                        day_of_week=day_of_week,
                        is_weekend=is_weekend,
                        struct_features=struct_features,
                        embedding=embedding,
                    )
                )
        return nights

    def _prepare_numeric_defaults(self) -> None:
        nr = self.numeric_ranges

        def get_range(key: str, fallback_min: float, fallback_max: float) -> Tuple[float, float]:
            vals = nr.get(key)
            if not vals or len(vals) != 2:
                return fallback_min, fallback_max
            return float(vals[0]), float(vals[1])

        self.group_min, self.group_max = get_range("group_size", 1.0, 20.0)
        self.budget_min, self.budget_max = get_range("budget_level", 1.0, 5.0)
        self.party_min, self.party_max = get_range("party_level", 1.0, 5.0)
        self.start_min, self.start_max = get_range("start_time_minutes", 17 * 60, 3 * 60 + 24 * 60)

    # ---------- Query feature construction ----------

    def _build_query_struct_features(self, q: SearchQueryParams) -> np.ndarray:
        """
        Build struct_features vector for query, aligned with the same layout
        as nights' struct_features.
        """
        # 1) City one-hot
        city_oh = one_hot(q.city, self.cities_vocab)

        # 2) Day one-hot
        day_oh = one_hot(q.day_of_week, self.days_vocab)

        # 3) Season one-hot – unknown from query -> all zeros
        season_oh = [0.0] * len(self.seasons_vocab)

        # 4) Location_type one-hot – unknown from query -> all zeros
        loc_type_oh = [0.0] * len(self.location_types_vocab)

        # 5) Music type one-hot – unknown from query -> all zeros
        music_oh = [0.0] * len(self.music_types_vocab)

        # 6) Vibe multi-hot from tags
        tags_lower = [t.lower().strip() for t in q.tags]
        vibe_mh = multi_hot(tags_lower, self.vibe_vocab)

        # 7) Numeric features
        group_size_norm = normalize_numeric(
            float(q.group_size),
            self.group_min,
            self.group_max,
            default_fraction=0.5,
        )
        budget_norm = normalize_numeric(
            float(q.budget_level),
            self.budget_min,
            self.budget_max,
            default_fraction=(q.budget_level - 1) / 4.0 if 1 <= q.budget_level <= 5 else 0.5,
        )
        party_norm = normalize_numeric(
            float(q.party_level),
            self.party_min,
            self.party_max,
            default_fraction=(q.party_level - 1) / 4.0 if 1 <= q.party_level <= 5 else 0.5,
        )

        time_minutes = parse_time_to_minutes(q.time)
        start_time_norm = normalize_numeric(
            float(time_minutes),
            self.start_min,
            self.start_max,
            default_fraction=0.5,
        )

        # Unknown numeric dimensions -> neutral
        alcohol_norm = 0.5
        crowd_norm = 0.5
        duration_norm = 0.5
        temperature_norm = 0.5
        cost_norm = 0.5
        tip_norm = 0.0  # not critical
        is_weekend = 1.0 if q.day_of_week in ("Friday", "Saturday") else 0.0

        numeric_vec = [
            group_size_norm,
            budget_norm,
            party_norm,
            alcohol_norm,
            crowd_norm,
            duration_norm,
            temperature_norm,
            cost_norm,
            tip_norm,
            start_time_norm,
            is_weekend,
        ]

        struct_features = np.array(
            city_oh
            + day_oh
            + season_oh
            + loc_type_oh
            + music_oh
            + vibe_mh
            + numeric_vec,
            dtype=np.float32,
        )
        return struct_features

    def _build_query_embedding(self, q: SearchQueryParams) -> Optional[np.ndarray]:
        """
        Build text for query embedding and call OpenAI.
        If OpenAI client is not available, return None and use only structural similarity.
        """
        if self.openai_client is None:
            return None

        tags_part = ", ".join(q.tags) if q.tags else "no specific tags"

        text = (
            f"We are a group of {q.group_size} friends going out in {q.city} "
            f"on {q.day_of_week} around {q.time}. "
            f"We want a party level around {q.party_level} and budget level {q.budget_level}. "
            f"We are looking for places with vibe: {tags_part}."
        )

        resp = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=text,
        )
        emb = np.array(resp.data[0].embedding, dtype=np.float32)
        return emb

    # ---------- Filtering by city and weekend/weekday ----------

    def _filter_nights_by_query(self, q: SearchQueryParams) -> List[NightRecord]:
        """
        Filter nights to those that are most relevant:
        1) Prefer same city as query.
        2) Within that, prefer same weekend/weekday group.
        If filters become too strict and produce 0 candidates, we fall back.
        """
        # 1) Filter by city
        by_city = [n for n in self.nights if n.city == q.city]
        if not by_city:
            # If no nights found for this city in data, fallback to all nights
            by_city = self.nights

        # 2) Filter by weekend vs weekday
        q_is_weekend = q.day_of_week in ("Friday", "Saturday")
        by_week_group = [n for n in by_city if n.is_weekend == q_is_weekend]
        if by_week_group:
            return by_week_group

        # Fallback if no nights for same weekend/weekday group
        return by_city

    # ---------- Core search (no guardrails) ----------

    def search(
        self,
        q: SearchQueryParams,
        top_n_nights: int = 50,
        top_k_venues: int = 5,
        lambda_struct: float = 0.5,
    ) -> List[VenueSearchResult]:
        """
        Basic search:
        - filter nights by city and weekend/weekday
        - compute query struct & embedding
        - compute combined similarity vs filtered nights
        - aggregate to venues
        - return top_k venues
        """
        query_struct = self._build_query_struct_features(q)
        query_emb = self._build_query_embedding(q)
        query_struct_vec = query_struct

        candidate_nights = self._filter_nights_by_query(q)

        night_scores: List[Tuple[float, NightRecord]] = []

        for night in candidate_nights:
            struct_sim = float(np.dot(query_struct_vec, night.struct_features))

            if query_emb is not None and night.embedding is not None:
                sem_sim = cosine_similarity(query_emb, night.embedding)
            else:
                sem_sim = 0.0

            score = sem_sim + lambda_struct * struct_sim
            night_scores.append((score, night))

        night_scores.sort(key=lambda x: x[0], reverse=True)
        top_n = night_scores[:top_n_nights]

        venue_scores: Dict[int, List[float]] = {}
        for score, night in top_n:
            venue_scores.setdefault(night.venue_id, []).append(score)

        aggregated: List[Tuple[float, int]] = []
        for vid, scores in venue_scores.items():
            if not scores:
                continue
            aggregated.append((sum(scores) / len(scores), vid))

        aggregated.sort(key=lambda x: x[0], reverse=True)
        top_venues = aggregated[:top_k_venues]

        results: List[VenueSearchResult] = []
        for score, vid in top_venues:
            venue = self.venues.get(vid)
            if not venue:
                continue
            reasons = self._build_reasons_for_venue(venue, q)
            results.append(
                VenueSearchResult(
                    venue_id=vid,
                    name=venue.name,
                    city=venue.city,
                    area=venue.area,
                    venue_type=venue.venue_type,
                    score=score,
                    reasons=reasons,
                )
            )
        return results

    # ---------- Search with prompt guardrails ----------

    def search_with_prompt_guardrail(
        self,
        q: SearchQueryParams,
        top_n_nights: int = 200,
        top_k_venues: int = 5,
        lambda_struct: float = 0.5,
    ) -> GuardedSearchResult:
        """
        Same as search(), but:
        - filters nights by city and weekend/weekday first
        - checks semantic similarity distribution to detect bad prompts:
          - "no_match"   -> best semantic similarity < 0.6
          - "too_broad"  -> too many very high semantic matches (>= 0.8)
        """
        query_struct = self._build_query_struct_features(q)
        query_emb = self._build_query_embedding(q)
        query_struct_vec = query_struct

        candidate_nights = self._filter_nights_by_query(q)

        night_scores: List[Tuple[float, NightRecord, float]] = []  # (score, night, sem_sim)
        semantic_sims: List[float] = []

        for night in candidate_nights:
            struct_sim = float(np.dot(query_struct_vec, night.struct_features))

            if query_emb is not None and night.embedding is not None:
                sem_sim = cosine_similarity(query_emb, night.embedding)
            else:
                sem_sim = 0.0

            total_score = sem_sim + lambda_struct * struct_sim
            night_scores.append((total_score, night, sem_sim))
            semantic_sims.append(sem_sim)

        # Guardrails only make sense if we actually used semantic similarity
        if semantic_sims and query_emb is not None:
            max_sem = max(semantic_sims)

            # 1) No good match
            if max_sem < 0.6:
                return GuardedSearchResult(
                    status="no_match",
                    reason=(
                        "Your request does not closely match any nights in our data "
                        "(best similarity < 60%). Try being more specific or changing constraints."
                    ),
                    venues=[],
                )

            # 2) Too broad: many very strong matches
            high_matches = sum(1 for s in semantic_sims if s >= 0.8)
            total_nights = len(semantic_sims)
            if total_nights > 0 and high_matches > 0.2 * total_nights:
                return GuardedSearchResult(
                    status="too_broad",
                    reason=(
                        "Your request matches too many nights very strongly. "
                        "Please narrow it down (specify city, vibe, time, or budget more precisely)."
                    ),
                    venues=[],
                )

        # If we are here -> prompt is OK, do normal ranking
        night_scores.sort(key=lambda x: x[0], reverse=True)
        top_n = night_scores[:top_n_nights]

        venue_scores: Dict[int, List[float]] = {}
        for score, night, _ in top_n:
            venue_scores.setdefault(night.venue_id, []).append(score)

        aggregated: List[Tuple[float, int]] = []
        for vid, scores in venue_scores.items():
            if not scores:
                continue
            aggregated.append((sum(scores) / len(scores), vid))

        aggregated.sort(key=lambda x: x[0], reverse=True)
        top_venues = aggregated[:top_k_venues]

        results: List[VenueSearchResult] = []
        for score, vid in top_venues:
            venue = self.venues.get(vid)
            if not venue:
                continue
            reasons = self._build_reasons_for_venue(venue, q)
            results.append(
                VenueSearchResult(
                    venue_id=vid,
                    name=venue.name,
                    city=venue.city,
                    area=venue.area,
                    venue_type=venue.venue_type,
                    score=score,
                    reasons=reasons,
                )
            )

        return GuardedSearchResult(
            status="ok",
            reason="Query matched a reasonable number of nights.",
            venues=results,
        )

    # ---------- Explanations ----------

    def _build_reasons_for_venue(
        self,
        venue: VenueInfo,
        q: SearchQueryParams,
    ) -> List[str]:
        """
        Simple, human-readable explanations for why this venue matches the query.
        """
        reasons: List[str] = []

        reasons.append(
            f"This venue is in {venue.area}, {venue.city}, matching your city selection."
        )

        if not math.isnan(venue.avg_party_level):
            if q.party_level >= 4 and venue.avg_party_level >= 4:
                reasons.append(
                    "Average party level here is high, matching your request for a crazy night."
                )
            elif q.party_level <= 2 and venue.avg_party_level <= 2:
                reasons.append(
                    "This place is usually more chill, matching your request for a relaxed night."
                )

        if venue.top_vibe_tags:
            intersect = set(t.lower() for t in venue.top_vibe_tags) & set(
                t.lower() for t in q.tags
            )
            if intersect:
                reasons.append(
                    "Guests often describe this place with similar vibe tags you requested: "
                    + ", ".join(sorted(intersect))
                )
            else:
                reasons.append(
                    "Typical vibe tags here are: " + ", ".join(venue.top_vibe_tags)
                )

        reasons.append(
            f"Typical opening hours from {venue.typical_start_time} to {venue.typical_end_time}, "
            f"which fits late-night outings."
        )

        return reasons
