import json
import random
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import Counter

# -----------------------------
# Configuration & vocabularies
# -----------------------------

CITIES = ["Belgrade", "Novi Sad", "Nis", "Kragujevac"]

AREAS_BY_CITY = {
    "Belgrade": ["Dorcol", "Savamala", "Vracar", "Zemun", "Novi Beograd"],
    "Novi Sad": ["Centar", "Limani", "Grbavica", "Podbara"],
    "Nis": ["Centar", "Duvanište", "Pantelej"],
    "Kragujevac": ["Centar", "Aerodrom", "Stanovo"],
}

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

VIBE_TAGS = [
    "chill", "techno", "rnb", "rock",
    "student night", "fancy", "date",
    "birthday", "kafana", "pub",
    "live music", "crowded", "quiet"
]

# How many variants to generate per seed night
VARIANTS_PER_NIGHT = 5

# Paths relative to this script
BASE_DIR = Path(__file__).resolve().parents[1]  # backend/
DATA_DIR = BASE_DIR / "data"
SEED_PATH = DATA_DIR / "nights_seed.jsonl"
FINAL_PATH = DATA_DIR / "nights_final.jsonl"


# -----------------------------
# Seed nights (clean, canonical)
# -----------------------------
# These are the 24 archetypal nights we designed earlier.
# You can freely change / extend this list if you want.

SEED_NIGHTS_RAW: List[Dict[str, Any]] = [
    {
        "city": "Belgrade",
        "area": "Dorcol",
        "day_of_week": "Friday",
        "start_time": "22:30",
        "end_time": "03:00",
        "group_size": 5,
        "budget_level": 2,
        "party_level": 4,
        "vibe_tags": ["techno", "student night", "crowded"],
        "description": "We met in a small bar in Dorcol (Belgrade) around 10:30pm, then moved to a small underground techno club and stayed on the dance floor until about 3am. There were 5 of us and the whole night lasted around 4.5 hours, with a techno, student night, crowded vibe."
    },
    {
        "city": "Belgrade",
        "area": "Savamala",
        "day_of_week": "Saturday",
        "start_time": "23:00",
        "end_time": "04:00",
        "group_size": 6,
        "budget_level": 3,
        "party_level": 5,
        "vibe_tags": ["techno", "crowded", "fancy"],
        "description": "We started the night in Savamala (Belgrade) with cocktails near the river, then went to a big techno club with an international DJ and stayed until 4am. There were 6 of us and the whole night lasted around 5.0 hours, with a techno, crowded, fancy vibe."
    },
    {
        "city": "Novi Sad",
        "area": "Limani",
        "day_of_week": "Thursday",
        "start_time": "22:00",
        "end_time": "02:00",
        "group_size": 4,
        "budget_level": 2,
        "party_level": 4,
        "vibe_tags": ["techno", "student night"],
        "description": "We met in a student bar in Limani (Novi Sad) a bit after 10pm and then moved to a small techno club popular with students, staying until around 2am. There were 4 of us and the whole night lasted about 4.0 hours, with a techno, student night vibe."
    },
    {
        "city": "Nis",
        "area": "Centar",
        "day_of_week": "Saturday",
        "start_time": "22:30",
        "end_time": "03:30",
        "group_size": 3,
        "budget_level": 2,
        "party_level": 5,
        "vibe_tags": ["techno", "crowded"],
        "description": "We started with a quick drink in the center of Nis and then went to the main techno club where a local DJ was playing until late. There were 3 of us and the night lasted around 5.0 hours, with a techno, crowded vibe."
    },
    {
        "city": "Belgrade",
        "area": "Vracar",
        "day_of_week": "Friday",
        "start_time": "20:30",
        "end_time": "01:30",
        "group_size": 8,
        "budget_level": 2,
        "party_level": 4,
        "vibe_tags": ["kafana", "live music", "crowded"],
        "description": "Our group booked a table in a traditional kafana in Vracar (Belgrade), with live folk music, lots of singing and heavy food until after 1am. There were 8 of us and the night lasted around 5.0 hours, with a kafana, live music, crowded vibe."
    },
    {
        "city": "Belgrade",
        "area": "Zemun",
        "day_of_week": "Saturday",
        "start_time": "21:00",
        "end_time": "02:00",
        "group_size": 10,
        "budget_level": 3,
        "party_level": 5,
        "vibe_tags": ["kafana", "live music", "birthday"],
        "description": "We celebrated a friend's birthday in a kafana in Zemun (Belgrade), with a live band, rakija and dancing on chairs until 2am. There were 10 of us and the night lasted about 5.0 hours, with a kafana, live music, birthday vibe."
    },
    {
        "city": "Novi Sad",
        "area": "Podbara",
        "day_of_week": "Thursday",
        "start_time": "20:00",
        "end_time": "00:30",
        "group_size": 6,
        "budget_level": 1,
        "party_level": 3,
        "vibe_tags": ["kafana", "live music"],
        "description": "We went to a small kafana in Podbara (Novi Sad) with affordable drinks and a local band playing folk songs until shortly after midnight. There were 6 of us and the night lasted around 4.5 hours, with a kafana, live music vibe."
    },
    {
        "city": "Nis",
        "area": "Duvanište",
        "day_of_week": "Friday",
        "start_time": "20:30",
        "end_time": "01:00",
        "group_size": 9,
        "budget_level": 2,
        "party_level": 4,
        "vibe_tags": ["kafana", "crowded", "birthday"],
        "description": "We spent the evening in a busy kafana in Duvanište (Nis) celebrating a birthday, with loud music and lots of food until after 1am. There were 9 of us and the night lasted around 4.5 hours, with a kafana, crowded, birthday vibe."
    },
    {
        "city": "Belgrade",
        "area": "Dorcol",
        "day_of_week": "Wednesday",
        "start_time": "19:30",
        "end_time": "23:00",
        "group_size": 3,
        "budget_level": 1,
        "party_level": 2,
        "vibe_tags": ["chill", "pub", "quiet"],
        "description": "We went to a small craft beer pub in Dorcol (Belgrade) after work, sat outside, tried a few local beers and talked until around 11pm. There were 3 of us and the night lasted about 3.5 hours, with a chill, pub, quiet vibe."
    },
    {
        "city": "Belgrade",
        "area": "Novi Beograd",
        "day_of_week": "Sunday",
        "start_time": "20:00",
        "end_time": "23:30",
        "group_size": 4,
        "budget_level": 2,
        "party_level": 2,
        "vibe_tags": ["chill", "pub"],
        "description": "We met in a modern pub in Novi Beograd (Belgrade) for a relaxed Sunday night with burgers, beer and board games until about 11:30pm. There were 4 of us and the night lasted around 3.5 hours, with a chill, pub vibe."
    },
    {
        "city": "Novi Sad",
        "area": "Centar",
        "day_of_week": "Friday",
        "start_time": "20:30",
        "end_time": "00:30",
        "group_size": 5,
        "budget_level": 2,
        "party_level": 3,
        "vibe_tags": ["chill", "pub", "crowded"],
        "description": "We went to a busy downtown pub in the center of Novi Sad for drinks and snacks, standing at the bar and chatting in a loud but friendly atmosphere until half past midnight. There were 5 of us and the night lasted around 4.0 hours, with a chill, pub, crowded vibe."
    },
    {
        "city": "Kragujevac",
        "area": "Centar",
        "day_of_week": "Thursday",
        "start_time": "19:30",
        "end_time": "22:30",
        "group_size": 2,
        "budget_level": 1,
        "party_level": 1,
        "vibe_tags": ["chill", "quiet"],
        "description": "We met in a quiet bar in the center of Kragujevac for a few drinks, soft music and a long conversation, leaving around 10:30pm. There were 2 of us and the night lasted about 3.0 hours, with a chill, quiet vibe."
    },
    {
        "city": "Belgrade",
        "area": "Vracar",
        "day_of_week": "Saturday",
        "start_time": "19:30",
        "end_time": "23:00",
        "group_size": 2,
        "budget_level": 3,
        "party_level": 1,
        "vibe_tags": ["date", "chill", "fancy"],
        "description": "It was a quiet date in Vracar (Belgrade), starting with dinner at a small bistro and then a couple of cocktails at a stylish bar before heading home around 11pm. There were 2 of us and the night lasted about 3.5 hours, with a date, chill, fancy vibe."
    },
    {
        "city": "Belgrade",
        "area": "Dorcol",
        "day_of_week": "Thursday",
        "start_time": "20:00",
        "end_time": "23:30",
        "group_size": 2,
        "budget_level": 2,
        "party_level": 1,
        "vibe_tags": ["date", "chill", "quiet"],
        "description": "It was a low-key date in Dorcol (Belgrade), with wine and small plates in a cozy bar, followed by a short walk by the river before going home. There were 2 of us and the night lasted around 3.5 hours, with a date, chill, quiet vibe."
    },
    {
        "city": "Novi Sad",
        "area": "Grbavica",
        "day_of_week": "Sunday",
        "start_time": "19:00",
        "end_time": "22:00",
        "group_size": 2,
        "budget_level": 2,
        "party_level": 1,
        "vibe_tags": ["date", "chill"],
        "description": "We had a simple Sunday date in Grbavica (Novi Sad), with pizza, beer and an easy walk back home, keeping everything relaxed and early. There were 2 of us and the night lasted about 3.0 hours, with a date, chill vibe."
    },
    {
        "city": "Nis",
        "area": "Centar",
        "day_of_week": "Friday",
        "start_time": "20:30",
        "end_time": "00:00",
        "group_size": 2,
        "budget_level": 3,
        "party_level": 2,
        "vibe_tags": ["date", "fancy", "quiet"],
        "description": "We went on a date in the center of Nis, starting with a fancy dinner and then dessert and wine in a quiet bar, leaving around midnight. There were 2 of us and the night lasted about 3.5 hours, with a date, fancy, quiet vibe."
    },
    {
        "city": "Belgrade",
        "area": "Dorcol",
        "day_of_week": "Friday",
        "start_time": "20:00",
        "end_time": "02:00",
        "group_size": 6,
        "budget_level": 2,
        "party_level": 4,
        "vibe_tags": ["pub", "crowded", "student night"],
        "description": "We started the night in a pub in Dorcol (Belgrade) with beers and shots, then moved to two more bars in the same area as the night got louder and more crowded. There were 6 of us and the night lasted about 6.0 hours, with a pub, crowded, student night vibe."
    },
    {
        "city": "Belgrade",
        "area": "Savamala",
        "day_of_week": "Saturday",
        "start_time": "21:00",
        "end_time": "03:00",
        "group_size": 7,
        "budget_level": 3,
        "party_level": 5,
        "vibe_tags": ["pub", "crowded", "birthday"],
        "description": "We celebrated a birthday with a pub crawl in Savamala (Belgrade), starting at a riverside bar and then visiting several crowded places until 3am. There were 7 of us and the night lasted about 6.0 hours, with a pub, crowded, birthday vibe."
    },
    {
        "city": "Novi Sad",
        "area": "Centar",
        "day_of_week": "Friday",
        "start_time": "20:30",
        "end_time": "01:30",
        "group_size": 5,
        "budget_level": 2,
        "party_level": 4,
        "vibe_tags": ["pub", "student night"],
        "description": "We did a small pub crawl in the center of Novi Sad, starting with a quiet bar and ending in a crowded student pub with cheap beer until around 1:30am. There were 5 of us and the night lasted around 5.0 hours, with a pub, student night vibe."
    },
    {
        "city": "Nis",
        "area": "Pantelej",
        "day_of_week": "Saturday",
        "start_time": "21:00",
        "end_time": "02:30",
        "group_size": 4,
        "budget_level": 2,
        "party_level": 4,
        "vibe_tags": ["pub", "crowded"],
        "description": "We moved between three different pubs in Pantelej (Nis), meeting new people and trying different beers, before heading home after 2:30am. There were 4 of us and the night lasted about 5.5 hours, with a pub, crowded vibe."
    },
    {
        "city": "Belgrade",
        "area": "Zemun",
        "day_of_week": "Friday",
        "start_time": "21:00",
        "end_time": "01:30",
        "group_size": 4,
        "budget_level": 2,
        "party_level": 3,
        "vibe_tags": ["rock", "live music"],
        "description": "We went to a rock bar in Zemun (Belgrade) to listen to a local band playing covers from the 80s and 90s until after 1am. There were 4 of us and the night lasted around 4.5 hours, with a rock, live music vibe."
    },
    {
        "city": "Belgrade",
        "area": "Dorcol",
        "day_of_week": "Saturday",
        "start_time": "21:30",
        "end_time": "02:00",
        "group_size": 5,
        "budget_level": 2,
        "party_level": 4,
        "vibe_tags": ["rock", "live music", "crowded"],
        "description": "We spent the night in a packed rock bar in Dorcol (Belgrade), singing along with a live band and squeezing through the crowd to get to the bar. There were 5 of us and the night lasted about 4.5 hours, with a rock, live music, crowded vibe."
    },
    {
        "city": "Novi Sad",
        "area": "Limani",
        "day_of_week": "Friday",
        "start_time": "20:30",
        "end_time": "00:30",
        "group_size": 3,
        "budget_level": 2,
        "party_level": 2,
        "vibe_tags": ["rock", "live music", "chill"],
        "description": "We went to a smaller rock bar in Limani (Novi Sad) with a laid-back band playing, sitting at a table and listening to music until around 12:30am. There were 3 of us and the night lasted around 4.0 hours, with a rock, live music, chill vibe."
    },
    {
        "city": "Nis",
        "area": "Centar",
        "day_of_week": "Thursday",
        "start_time": "20:30",
        "end_time": "23:30",
        "group_size": 2,
        "budget_level": 2,
        "party_level": 2,
        "vibe_tags": ["rock", "chill"],
        "description": "We spent a relaxed Thursday evening in a rock bar in the center of Nis, mostly sitting and talking while a quieter band played in the background. There were 2 of us and the night lasted about 3.0 hours, with a rock, chill vibe."
    },
]


# -----------------------------
# Utility functions
# -----------------------------

def parse_time_to_minutes(time_str: str) -> int:
    """Convert 'HH:MM' to minutes since midnight."""
    h, m = time_str.strip().split(":")
    return int(h) * 60 + int(m)


def minutes_to_time_str(minutes: int) -> str:
    """Convert minutes since midnight back to 'HH:MM', wrapping 24h."""
    minutes = minutes % (24 * 60)
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"


def clamp(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(max_value, value))


# -----------------------------
# Normalization & variants
# -----------------------------

def normalize_seed_night(raw: Dict[str, Any], id_: int) -> Dict[str, Any]:
    """
    Normalize a seed night and assign an ID.
    Here seeds are already clean, but we still enforce boundaries and compute duration.
    """
    city = raw.get("city", "Belgrade")
    if city not in CITIES:
        # fallback if user changes seeds
        city = "Belgrade"

    area = raw.get("area") or random.choice(AREAS_BY_CITY.get(city, ["Centar"]))
    day = raw.get("day_of_week", "Friday")
    if day not in DAYS:
        day = "Friday"

    start_str = raw.get("start_time", "21:00")
    end_str = raw.get("end_time", "01:00")
    start_min = parse_time_to_minutes(start_str)
    end_min = parse_time_to_minutes(end_str)

    if end_min <= start_min:
        end_min += 4 * 60  # assume up to +4h after midnight

    duration_hours = max(1.0, (end_min - start_min) / 60.0)

    group_size = int(raw.get("group_size", 4))
    group_size = clamp(group_size, 1, 12)

    budget_level = int(raw.get("budget_level", 2))
    budget_level = clamp(budget_level, 1, 3)

    party_level = int(raw.get("party_level", 3))
    party_level = clamp(party_level, 1, 5)

    raw_tags = raw.get("vibe_tags") or []
    vibe_tags = [t for t in raw_tags if t in VIBE_TAGS]
    if len(vibe_tags) < 2:
        # Ensure at least 2 tags
        extra = [t for t in VIBE_TAGS if t not in vibe_tags]
        vibe_tags.extend(random.sample(extra, k=(2 - len(vibe_tags))))

    description = (raw.get("description") or "").strip()
    if len(description) < 20:
        description = (
            f"We went out in {area} ({city}) on {day.lower()} with {group_size} people, "
            f"had a {duration_hours:.1f} hour night with a {', '.join(vibe_tags)} vibe."
        )

    normalized = {
        "id": id_,
        "city": city,
        "area": area,
        "day_of_week": day,
        "start_time": minutes_to_time_str(start_min),
        "end_time": minutes_to_time_str(end_min),
        "group_size": group_size,
        "budget_level": budget_level,
        "party_level": party_level,
        "vibe_tags": vibe_tags,
        "description": description,
    }
    return normalized


def tweak_time_range(start_min: int, end_min: int) -> Tuple[int, int]:
    """
    Slightly shift the time window:
    - start ±30min
    - duration ±30min (at least 1h)
    """
    shift_start = random.randint(-30, 30)
    new_start = start_min + shift_start

    duration = end_min - start_min
    shift_duration = random.randint(-30, 30)
    new_duration = max(60, duration + shift_duration)
    new_end = new_start + new_duration

    return new_start, new_end


def tweak_vibe_tags(vibe_tags: List[str]) -> List[str]:
    """
    Slightly modify vibe tags: maybe drop one, maybe add another.
    """
    tags = list(vibe_tags)

    # Maybe drop one tag
    if len(tags) > 2 and random.random() < 0.4:
        drop_idx = random.randrange(len(tags))
        tags.pop(drop_idx)

    # Maybe add a tag
    if len(tags) < 5 and random.random() < 0.6:
        candidates = [t for t in VIBE_TAGS if t not in tags]
        if candidates:
            tags.append(random.choice(candidates))

    # Deduplicate and clamp length
    tags = list(dict.fromkeys(tags))
    if len(tags) < 2:
        candidates = [t for t in VIBE_TAGS if t not in tags]
        if candidates:
            tags.append(random.choice(candidates))
    if len(tags) > 5:
        tags = tags[:5]

    return tags


def generate_variants_for_night(
    night: Dict[str, Any], next_id_start: int, n_variants: int
) -> List[Dict[str, Any]]:
    """
    Generate n_variants new nights from a base night by tweaking:
    - area within same city
    - group size, budget, party level
    - time range
    - vibe tags
    - description slightly extended
    """
    variants: List[Dict[str, Any]] = []
    current_id = next_id_start

    base_start = parse_time_to_minutes(night["start_time"])
    base_end = parse_time_to_minutes(night["end_time"])

    for _ in range(n_variants):
        new_night = dict(night)
        new_night["id"] = current_id

        city = new_night["city"]
        possible_areas = AREAS_BY_CITY.get(city, [new_night["area"]])
        if possible_areas and random.random() < 0.5:
            new_night["area"] = random.choice(possible_areas)

        gs = new_night["group_size"]
        gs += random.choice([-1, 0, 1])
        new_night["group_size"] = clamp(gs, 1, 12)

        bl = new_night["budget_level"]
        if random.random() < 0.5:
            bl += random.choice([-1, 1])
        new_night["budget_level"] = clamp(bl, 1, 3)

        pl = new_night["party_level"]
        if random.random() < 0.7:
            pl += random.choice([-1, 0, 1])
        new_night["party_level"] = clamp(pl, 1, 5)

        new_start_min, new_end_min = tweak_time_range(base_start, base_end)
        new_night["start_time"] = minutes_to_time_str(new_start_min)
        new_night["end_time"] = minutes_to_time_str(new_end_min)

        new_tags = tweak_vibe_tags(new_night["vibe_tags"])
        new_night["vibe_tags"] = new_tags

        desc = new_night["description"]
        extra_bits = []
        if new_night["area"] != night["area"]:
            extra_bits.append(f"this time we went to {new_night['area']} instead of {night['area']}")
        if new_night["group_size"] != night["group_size"]:
            extra_bits.append(f"the group size changed from {night['group_size']} to {new_night['group_size']}")
        if new_night["budget_level"] != night["budget_level"]:
            extra_bits.append(
                "we spent a bit more"
                if new_night["budget_level"] > night["budget_level"]
                else "we kept it more on a budget"
            )
        if new_night["party_level"] != night["party_level"]:
            extra_bits.append(
                "the party felt more intense"
                if new_night["party_level"] > night["party_level"]
                else "the night felt slightly more relaxed"
            )

        if extra_bits:
            extra_sentence = " In this variant, " + ", and ".join(extra_bits) + "."
            new_night["description"] = desc.rstrip() + extra_sentence

        variants.append(new_night)
        current_id += 1

    return variants


# -----------------------------
# Summary / statistics
# -----------------------------

def summarize_dataset(nights: List[Dict[str, Any]]) -> None:
    print("\n=== NightTwin Dataset Summary ===")
    print(f"Total nights: {len(nights)}")

    cities = Counter(n["city"] for n in nights)
    print("\nCities:")
    for city, count in cities.most_common():
        print(f"  {city}: {count}")

    days = Counter(n["day_of_week"] for n in nights)
    print("\nDays of week:")
    for day, count in days.most_common():
        print(f"  {day}: {count}")

    all_tags = []
    for n in nights:
        all_tags.extend(n.get("vibe_tags", []))
    tag_counts = Counter(all_tags)
    print("\nVibe tags:")
    for tag, count in tag_counts.most_common():
        print(f"  {tag}: {count}")

    group_sizes = [n["group_size"] for n in nights]
    budgets = [n["budget_level"] for n in nights]
    parties = [n["party_level"] for n in nights]

    print("\nGroup size range:", min(group_sizes), "to", max(group_sizes))
    print("Budget level range:", min(budgets), "to", max(budgets))
    print("Party level range:", min(parties), "to", max(parties))


# -----------------------------
# Main pipeline
# -----------------------------

def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    normalized_nights: List[Dict[str, Any]] = []
    next_id = 1

    # 1) Normalize seeds and assign IDs
    for raw in SEED_NIGHTS_RAW:
        normalized = normalize_seed_night(raw, id_=next_id)
        normalized_nights.append(normalized)
        next_id += 1

    # 2) Write normalized seeds to nights_seed.jsonl
    with SEED_PATH.open("w", encoding="utf-8") as f:
        for night in normalized_nights:
            f.write(json.dumps(night, ensure_ascii=False))
            f.write("\n")
    print(f"Wrote {len(normalized_nights)} normalized seed nights to {SEED_PATH}")

    # 3) Generate variants and build final dataset
    all_nights: List[Dict[str, Any]] = []
    for night in normalized_nights:
        all_nights.append(night)
        variants = generate_variants_for_night(
            night, next_id_start=next_id, n_variants=VARIANTS_PER_NIGHT
        )
        all_nights.extend(variants)
        next_id += len(variants)

    random.shuffle(all_nights)

    with FINAL_PATH.open("w", encoding="utf-8") as f:
        for night in all_nights:
            f.write(json.dumps(night, ensure_ascii=False))
            f.write("\n")
    print(f"Wrote {len(all_nights)} total nights (seeds + variants) to {FINAL_PATH}")

    summarize_dataset(all_nights)


if __name__ == "__main__":
    main()
