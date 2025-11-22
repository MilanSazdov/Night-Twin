"""
preprocess_nights.py

Offline script to:
1) Read nights_with_venues.csv (output of build_venues.py).
2) Clean and enrich data (times, durations, numeric normalization).
3) Build categorical vocabularies and multi-hot encodings.
4) Optionally call OpenAI embeddings for each night.
5) Save:
    - features_config.json (vocabularies, feature indices)
    - nights_features.jsonl (one line per night with features + embedding)

Run:

    cd backend
    python -m scripts.preprocess_nights
"""

from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import Counter
import json
import math

import numpy as np
import pandas as pd

# If you want to enable embeddings, install openai and set OPENAI_API_KEY in env:
#   pip install openai
#   export OPENAI_API_KEY="..."
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # so script can still run without the library


# -----------------------------
# Configuration
# -----------------------------

BASE_DIR = Path(__file__).resolve().parents[1]  # backend/
DATA_DIR = BASE_DIR / "data"

NIGHTS_WITH_VENUES_PATH = DATA_DIR / "nights_with_venues.csv"
FEATURES_CONFIG_PATH = DATA_DIR / "features_config.json"
NIGHTS_FEATURES_PATH = DATA_DIR / "nights_features.jsonl"

# Toggle this to True when you want to actually call OpenAI embeddings.
USE_OPENAI_EMBEDDINGS = False   # Set to True during hackathon if API key is ready
EMBEDDING_MODEL = "text-embedding-3-small"


# -----------------------------
# Helpers
# -----------------------------

def parse_time_to_minutes(time_str: str) -> int:
    if not isinstance(time_str, str) or ":" not in time_str:
        return 21 * 60
    try:
        h_str, m_str = time_str.strip().split(":")
        h = int(h_str)
        m = int(m_str)
        if not (0 <= h < 24 and 0 <= m < 60):
            raise ValueError()
        return h * 60 + m
    except Exception:
        return 21 * 60


def unwrap_end_time(start_min: int, end_min: int) -> int:
    """Handle nights that go past midnight (end <= start => +24h)."""
    if end_min <= start_min:
        return end_min + 24 * 60
    return end_min


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def is_weekend(day_of_week: str) -> int:
    return 1 if day_of_week in ("Friday", "Saturday") else 0


def parse_vibe_tags(cell: Any) -> List[str]:
    """Parse a vibe_tags cell into a list of lowercase tokens."""
    if not isinstance(cell, str):
        return []
    parts = [p.strip().lower() for p in cell.split(",")]
    return [p for p in parts if p]


def safe_float(series: pd.Series, default: float = math.nan) -> float:
    series = pd.to_numeric(series, errors="coerce")
    if series.notna().sum() == 0:
        return default
    return float(series.mean())


def build_struct_features_config(df: pd.DataFrame, top_n_vibe_tags: int = 30) -> Dict[str, Any]:
    """
    Build vocabularies for categories and vibe tags from the dataset.
    Returns a config dict that describes feature order.
    """
    cities = sorted(df["city"].dropna().unique().tolist())
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    seasons = sorted(df["season"].dropna().unique().tolist())
    location_types = sorted(df["location_type"].dropna().unique().tolist())
    music_types = sorted(df["type_of_music"].dropna().astype(str).unique().tolist())

    # Build global vibe tag vocabulary (top N by frequency)
    tag_counter: Counter = Counter()
    for cell in df["vibe_tags"]:
        tags = parse_vibe_tags(cell)
        tag_counter.update(tags)

    most_common_tags = [tag for tag, _ in tag_counter.most_common(top_n_vibe_tags)]

    numeric_features = [
        "group_size_norm",
        "budget_norm",
        "party_norm",
        "alcohol_norm",
        "crowd_norm",
        "duration_norm",
        "temperature_norm",
        "cost_norm",
        "tip_norm",
        "start_time_norm",
        "is_weekend",
    ]

    config = {
        "cities": cities,
        "days": days,
        "seasons": seasons,
        "location_types": location_types,
        "music_types": music_types,
        "vibe_tags": most_common_tags,
        "numeric_features": numeric_features,
    }
    return config


def one_hot(value: str, vocab: List[str]) -> List[float]:
    return [1.0 if value == v else 0.0 for v in vocab]


def multi_hot(tags: List[str], vocab: List[str]) -> List[float]:
    vocab_index = {tag: idx for idx, tag in enumerate(vocab)}
    vec = [0.0] * len(vocab)
    for t in tags:
        if t in vocab_index:
            vec[vocab_index[t]] = 1.0
    return vec


def normalize_numeric(value: float, min_val: float, max_val: float) -> float:
    """Simple min-max normalization with clamping."""
    if math.isnan(value):
        return 0.0
    if max_val == min_val:
        return 0.0
    scaled = (value - min_val) / (max_val - min_val)
    return clamp(scaled, 0.0, 1.0)


def build_text_for_embedding(row: pd.Series, clean_tags: List[str]) -> str:
    """
    Build a descriptive text that summarises the night.
    This text will be fed into the embedding model.
    """
    name = row["name"]
    city = row["city"]
    area = row["area"]
    day = row["day_of_week"]
    music = row["type_of_music"]
    group_size = int(row["group_size"])
    budget_level = int(row["budget_level"])
    party_level = int(row["party_level"])
    location_type = row["location_type"]
    weather = row.get("weather", "")
    temperature = row.get("temperature", "")

    desc = str(row["description"]) if isinstance(row["description"], str) else ""

    tags_part = ", ".join(clean_tags) if clean_tags else "no specific tags"

    text = (
        f"Night out at {name} in {area}, {city} on {day}. "
        f"Music: {music}. Vibe tags: {tags_part}. "
        f"There were {group_size} people, with budget level {budget_level} "
        f"and party level {party_level}. "
        f"The place is mostly {location_type}. "
        f"Weather: {weather}, temperature around {temperature} degrees. "
        f"User description: {desc}"
    )
    return text


def get_openai_client() -> Any:
    if not USE_OPENAI_EMBEDDINGS:
        return None
    if OpenAI is None:
        raise RuntimeError(
            "openai library is not installed. Install with 'pip install openai'."
        )
    client = OpenAI()
    return client


def compute_embedding(client: Any, text: str) -> List[float]:
    """
    Call OpenAI embedding API. If USE_OPENAI_EMBEDDINGS is False,
    this will never be called.
    """
    resp = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return resp.data[0].embedding


# -----------------------------
# Main preprocessing logic
# -----------------------------

def preprocess_nights() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not NIGHTS_WITH_VENUES_PATH.exists():
        raise FileNotFoundError(
            f"nights_with_venues.csv not found at {NIGHTS_WITH_VENUES_PATH}. "
            f"Run build_venues.py first."
        )

    print(f"Loading nights_with_venues from {NIGHTS_WITH_VENUES_PATH}...")
    df = pd.read_csv(NIGHTS_WITH_VENUES_PATH)

    # Basic cleaning of numeric columns (ensure numeric type)
    numeric_cols = [
        "group_size", "budget_level", "party_level",
        "alcohol_level", "crowd_density",
        "cost", "tip", "temperature",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Time features
    start_min = df["start_time"].apply(parse_time_to_minutes)
    end_min_raw = df["end_time"].apply(parse_time_to_minutes)
    end_min_unwrapped = [
        unwrap_end_time(s, e) for s, e in zip(start_min, end_min_raw)
    ]
    df["start_time_minutes"] = start_min
    df["end_time_minutes"] = end_min_unwrapped

    df["duration_minutes"] = df["end_time_minutes"] - df["start_time_minutes"]
    df["duration_hours"] = df["duration_minutes"] / 60.0

    # Weekend flag
    df["is_weekend"] = df["day_of_week"].apply(is_weekend)

    # Build global vocabularies and config
    print("Building feature configuration (vocabularies)...")
    config = build_struct_features_config(df, top_n_vibe_tags=30)

    # Precompute min/max for numeric normalization
    def col_min_max(col: str, default_min: float, default_max: float) -> Tuple[float, float]:
        series = pd.to_numeric(df[col], errors="coerce")
        valid = series.dropna()
        if len(valid) == 0:
            return default_min, default_max
        return float(valid.min()), float(valid.max())

    group_min, group_max = col_min_max("group_size", 1.0, 20.0)
    budget_min, budget_max = col_min_max("budget_level", 1.0, 5.0)
    party_min, party_max = col_min_max("party_level", 1.0, 5.0)
    alcohol_min, alcohol_max = col_min_max("alcohol_level", 0.0, 10.0)
    crowd_min, crowd_max = col_min_max("crowd_density", 0.0, 10.0)
    duration_min, duration_max = col_min_max("duration_hours", 0.5, 10.0)
    temp_min, temp_max = col_min_max("temperature", -10.0, 40.0)
    cost_min, cost_max = col_min_max("cost", 0.0, 300.0)
    tip_min, tip_max = col_min_max("tip", 0.0, 100.0)
    start_min_val, start_max_val = col_min_max("start_time_minutes", 17 * 60, 3 * 60 + 24 * 60)

    # Add numeric ranges to config for transparency
    config["numeric_ranges"] = {
        "group_size": [group_min, group_max],
        "budget_level": [budget_min, budget_max],
        "party_level": [party_min, party_max],
        "alcohol_level": [alcohol_min, alcohol_max],
        "crowd_density": [crowd_min, crowd_max],
        "duration_hours": [duration_min, duration_max],
        "temperature": [temp_min, temp_max],
        "cost": [cost_min, cost_max],
        "tip": [tip_min, tip_max],
        "start_time_minutes": [start_min_val, start_max_val],
    }

    # Save features_config.json so the API / frontend can use the same mapping
    FEATURES_CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"Saved feature configuration to {FEATURES_CONFIG_PATH}")

    # Prepare OpenAI client (if enabled)
    client = get_openai_client()

    # Process each night into features + embedding
    cities_vocab = config["cities"]
    days_vocab = config["days"]
    seasons_vocab = config["seasons"]
    location_types_vocab = config["location_types"]
    music_types_vocab = config["music_types"]
    vibe_vocab = config["vibe_tags"]

    print("Building features and (optionally) embeddings for each night...")
    with NIGHTS_FEATURES_PATH.open("w", encoding="utf-8") as out_f:
        for _, row in df.iterrows():
            night_id = int(row["id"])
            venue_id = int(row["venue_id"])

            # Clean tags
            raw_tags = row["vibe_tags"]
            clean_tags = parse_vibe_tags(raw_tags)

            # --- Numeric normalization ---
            group_size_norm = normalize_numeric(row["group_size"], group_min, group_max)
            budget_norm = normalize_numeric(row["budget_level"], budget_min, budget_max)
            party_norm = normalize_numeric(row["party_level"], party_min, party_max)
            alcohol_norm = normalize_numeric(row["alcohol_level"], alcohol_min, alcohol_max)
            crowd_norm = normalize_numeric(row["crowd_density"], crowd_min, crowd_max)
            duration_norm = normalize_numeric(row["duration_hours"], duration_min, duration_max)
            temp_norm = normalize_numeric(row["temperature"], temp_min, temp_max)
            cost_norm = normalize_numeric(row["cost"], cost_min, cost_max)
            tip_norm = normalize_numeric(row["tip"], tip_min, tip_max)
            start_time_norm = normalize_numeric(row["start_time_minutes"], start_min_val, start_max_val)
            is_weekend_norm = float(row["is_weekend"])

            # --- Categorical encodings ---
            city_oh = one_hot(row["city"], cities_vocab)
            day_oh = one_hot(row["day_of_week"], days_vocab)
            season_oh = one_hot(row["season"], seasons_vocab)
            loc_type_oh = one_hot(row["location_type"], location_types_vocab)
            music_oh = one_hot(str(row["type_of_music"]), music_types_vocab)
            vibe_mh = multi_hot(clean_tags, vibe_vocab)

            numeric_vec = [
                group_size_norm,
                budget_norm,
                party_norm,
                alcohol_norm,
                crowd_norm,
                duration_norm,
                temp_norm,
                cost_norm,
                tip_norm,
                start_time_norm,
                is_weekend_norm,
            ]

            struct_features = (
                city_oh
                + day_oh
                + season_oh
                + loc_type_oh
                + music_oh
                + vibe_mh
                + numeric_vec
            )

            # --- Text for embedding ---
            text_for_embedding = build_text_for_embedding(row, clean_tags)

            # --- Embedding (optional) ---
            if USE_OPENAI_EMBEDDINGS:
                embedding = compute_embedding(client, text_for_embedding)
            else:
                embedding = []  # will be filled later or computed at query-time

            record = {
                "night_id": night_id,
                "venue_id": venue_id,
                "city": row["city"],
                "area": row["area"],
                "day_of_week": row["day_of_week"],
                "season": row["season"],
                "struct_features": struct_features,
                "text_for_embedding": text_for_embedding,
                "embedding": embedding,
            }

            out_f.write(json.dumps(record, ensure_ascii=False))
            out_f.write("\n")

    print(f"Saved processed nights with features to {NIGHTS_FEATURES_PATH}")


def main() -> None:
    preprocess_nights()


if __name__ == "__main__":
    main()
