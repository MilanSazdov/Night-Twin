"""
build_venues.py

Offline script to:
1) Read the raw Serbia nightlife dataset (CSV).
2) Build a Venues table (one row per (name, city, area)).
3) Compute stats per venue (avg budget, party, typical time, etc.).
4) Infer a venue_type (kafana, club, pub, rock_bar, cocktail_bar, bar).
5) Attach venue_id back to each night and save nights_with_venues.csv.

Run once (or when dataset changes):

    cd backend
    python -m scripts.build_venues
"""

from pathlib import Path
from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np
from collections import Counter


# -----------------------------
# Paths
# -----------------------------

BASE_DIR = Path(__file__).resolve().parents[1]  # backend/
DATA_DIR = BASE_DIR / "data"

RAW_CSV_PATH = DATA_DIR / "serbia_nightlife_dataset.csv"
VENUES_CSV_PATH = DATA_DIR / "venues.csv"
NIGHTS_WITH_VENUES_PATH = DATA_DIR / "nights_with_venues.csv"


# -----------------------------
# Time helpers
# -----------------------------

def parse_time_to_minutes(time_str: str) -> int:
    """
    Convert 'HH:MM' to minutes since midnight.

    If the input is invalid, default to 21:00 (9pm).
    """
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


def minutes_to_time_str(minutes: float) -> str:
    """
    Convert minutes since midnight (may be > 24h due to wrapping)
    back to 'HH:MM' in 24h format, wrapping around 24h.
    """
    total = int(round(minutes)) % (24 * 60)
    h = total // 60
    m = total % 60
    return f"{h:02d}:{m:02d}"


def unwrap_end_time(start_min: int, end_min: int) -> int:
    """
    Handle nights that go past midnight:
    If end_min <= start_min, assume it's after midnight and add 24h.
    """
    if end_min <= start_min:
        return end_min + 24 * 60
    return end_min


# -----------------------------
# Venue type inference
# -----------------------------

def infer_venue_type(
    names: List[str],
    type_of_music_values: List[str],
    all_vibe_tags: List[str],
) -> str:
    """
    Heuristic to infer venue type from:
    - venue name(s)
    - type_of_music column values
    - vibe_tags text tokens

    Returns one of:
        'kafana', 'club', 'pub', 'rock_bar', 'cocktail_bar', 'bar'
    """
    # Lowercase all inputs for easier checks
    all_names = " ".join(n.lower() for n in names if isinstance(n, str))
    all_music = " ".join(m.lower() for m in type_of_music_values if isinstance(m, str))
    all_tags = " ".join(t.lower() for t in all_vibe_tags if isinstance(t, str))

    text = " ".join([all_names, all_music, all_tags])

    # Kafana
    if "kafana" in text or "starogradska" in text or "turbo folk" in text or "narodna" in text:
        return "kafana"

    # Club / discotheque
    if any(k in text for k in ["club", "discoteca", "discotheque", "techno", "edm", "house", "afterparty"]):
        return "club"

    # Rock bar
    if any(k in text for k in ["rock", "metal", "hard rock", "punk"]):
        return "rock_bar"

    # Pub / beer place
    if any(k in text for k in ["pub", "pivnica", "craft beer"]):
        return "pub"

    # Cocktail / rooftop
    if any(k in text for k in ["cocktail bar", "rooftop", "wine tasting"]):
        return "cocktail_bar"

    # Fallback
    return "bar"


# -----------------------------
# Vibe tags parsing
# -----------------------------

def parse_vibe_tags_column(vibe_str: Any) -> List[str]:
    """
    Parse 'vibe_tags' cell into a list of lowercase tokens.

    Example:
        "loud, crowded, local gem" -> ["loud", "crowded", "local gem"]
    """
    if not isinstance(vibe_str, str):
        return []

    parts = [p.strip().lower() for p in vibe_str.split(",")]
    return [p for p in parts if p]


def get_top_vibe_tags_for_group(series: pd.Series, max_tags: int = 5) -> List[str]:
    """
    Merge all vibe_tags from all nights of a venue and return the
    top max_tags by frequency.
    """
    counter: Counter = Counter()
    for cell in series:
        tags = parse_vibe_tags_column(cell)
        counter.update(tags)

    if not counter:
        return []

    top = [tag for tag, _ in counter.most_common(max_tags)]
    return top


# -----------------------------
# Main build logic
# -----------------------------

def build_venues_and_nights() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not RAW_CSV_PATH.exists():
        raise FileNotFoundError(f"Raw dataset not found at {RAW_CSV_PATH}")

    print(f"Loading raw dataset from {RAW_CSV_PATH}...")
    df = pd.read_csv(RAW_CSV_PATH)

    # Basic checks
    expected_cols = {
        "id", "name", "city", "area", "location", "day_of_week", "date",
        "season", "start_time", "end_time", "group_size",
        "number_of_males", "number_of_females", "budget_level", "party_level",
        "cost", "tip", "type_of_music", "vibe_tags", "weather",
        "temperature", "location_type", "alcohol_level", "crowd_density",
        "description",
    }
    missing = expected_cols - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing columns: {missing}")

    # -------------------------
    # Build venues table
    # -------------------------

    # Group by (name, city, area) to define a venue
    group_cols = ["name", "city", "area"]
    grouped = df.groupby(group_cols, dropna=False)

    venues_rows: List[Dict[str, Any]] = []

    print(f"Building venues from {len(grouped)} unique (name, city, area) combinations...")

    for venue_idx, ((name, city, area), group) in enumerate(grouped, start=1):
        # Collect raw columns
        type_of_music_values = group["type_of_music"].dropna().astype(str).tolist()
        vibe_series = group["vibe_tags"]
        location_types = group["location_type"].dropna().astype(str).tolist()
        days = group["day_of_week"].dropna().astype(str).tolist()

        # Infer venue type
        all_vibe_as_text = [str(v) for v in vibe_series.dropna().tolist()]
        venue_type = infer_venue_type(
            names=[str(name)],
            type_of_music_values=type_of_music_values,
            all_vibe_tags=all_vibe_as_text,
        )

        # Typical start/end time:
        start_minutes = group["start_time"].apply(parse_time_to_minutes)
        end_minutes_raw = group["end_time"].apply(parse_time_to_minutes)
        end_minutes_unwrapped = [
            unwrap_end_time(s, e) for s, e in zip(start_minutes, end_minutes_raw)
        ]

        if len(start_minutes) > 0:
            typical_start_min = float(np.median(start_minutes))
        else:
            typical_start_min = 21 * 60  # fallback 21:00

        if len(end_minutes_unwrapped) > 0:
            typical_end_min = float(np.median(end_minutes_unwrapped))
        else:
            typical_end_min = typical_start_min + 3 * 60  # fallback +3h

        typical_start_str = minutes_to_time_str(typical_start_min)
        typical_end_str = minutes_to_time_str(typical_end_min)

        # Aggregated numeric stats
        def safe_mean(series: pd.Series) -> float:
            series = pd.to_numeric(series, errors="coerce")
            if series.notna().sum() == 0:
                return float("nan")
            return float(series.mean())

        avg_budget = safe_mean(group["budget_level"])
        avg_party = safe_mean(group["party_level"])
        avg_cost = safe_mean(group["cost"])
        avg_tip = safe_mean(group["tip"])
        avg_alcohol = safe_mean(group["alcohol_level"])
        avg_crowd = safe_mean(group["crowd_density"])
        avg_temp = safe_mean(group["temperature"])

        # Dominant (most frequent) day, location type, type_of_music
        def mode_or_none(values: List[str]) -> str:
            if not values:
                return ""
            c = Counter(values)
            return c.most_common(1)[0][0]

        dominant_day = mode_or_none(days)
        dominant_location_type = mode_or_none(location_types)
        dominant_music = mode_or_none(type_of_music_values)

        # Top vibe tags
        top_vibe_tags = get_top_vibe_tags_for_group(vibe_series, max_tags=5)
        top_vibe_tags_str = ",".join(top_vibe_tags) if top_vibe_tags else ""

        venues_rows.append(
            {
                "venue_id": venue_idx,
                "name": name,
                "city": city,
                "area": area,
                "venue_type": venue_type,
                "avg_budget_level": avg_budget,
                "avg_party_level": avg_party,
                "avg_cost": avg_cost,
                "avg_tip": avg_tip,
                "avg_alcohol_level": avg_alcohol,
                "avg_crowd_density": avg_crowd,
                "avg_temperature": avg_temp,
                "typical_start_time": typical_start_str,
                "typical_end_time": typical_end_str,
                "dominant_day_of_week": dominant_day,
                "dominant_location_type": dominant_location_type,
                "dominant_type_of_music": dominant_music,
                "top_vibe_tags": top_vibe_tags_str,
            }
        )

    venues_df = pd.DataFrame(venues_rows)

    # Save venues table
    VENUES_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    venues_df.to_csv(VENUES_CSV_PATH, index=False)
    print(f"Saved {len(venues_df)} venues to {VENUES_CSV_PATH}")

    # -------------------------
    # Attach venue_id to nights
    # -------------------------

    # Merge back on (name, city, area)
    df_with_venues = df.merge(
        venues_df[["venue_id", "name", "city", "area"]],
        on=["name", "city", "area"],
        how="left",
        validate="many_to_one",
    )

    if df_with_venues["venue_id"].isna().any():
        raise RuntimeError("Some nights could not be matched to a venue_id. Check merge logic.")

    df_with_venues.to_csv(NIGHTS_WITH_VENUES_PATH, index=False)
    print(f"Saved nights_with_venues with venue_id to {NIGHTS_WITH_VENUES_PATH}")


def main() -> None:
    build_venues_and_nights()


if __name__ == "__main__":
    main()
