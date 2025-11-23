# 🌃 NightTwin: AI Doppelgängers for Your Night Out

![NightTwin Banner](./assets/banner.png)

<div align="center">

**Describe your perfect night out in one sentence.  
We’ll find its nightlife twin.**

Turn messy reviews and past nights out into **AI-powered “doppelgänger” venues** that match your vibe, budget, city, and chaos level.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
![Backend: FastAPI](https://img.shields.io/badge/Backend-FastAPI-blue)
![AI Stack: OpenAI](https://img.shields.io/badge/AI-OpenAI%20API-purple)
![Status: Hackathon Prototype](https://img.shields.io/badge/Status-Hackathon_Prototype-orange)

</div>

---

## 📖 Table of Contents

- [💥 The Problem](#-the-problem)
- [💡 The Solution](#-the-solution)
- [✨ Key Features](#-key-features)
- [🧠 AI & Modeling](#-ai--modeling)
  - [📊 Dataset & Preprocessing](#-dataset--preprocessing)
  - [🧬 Model Experiments & Final Choice](#-model-experiments--final-choice)
  - [🧬 Where Is the “Doppelgänger”?](#-where-is-the-doppelgänger)
- [🏗 Architecture & Tech Stack](#-architecture--tech-stack)
- [🔥 How It Works (End-to-End Flow)](#-how-it-works-end-to-end-flow)
- [🛠 Getting Started](#-getting-started)
  - [Backend (FastAPI)](#backend-fastapi)
  - [Frontend (React)](#frontend-react)
- [🚀 Example Prompts to Try](#-example-prompts-to-try)
- [👥 Authors](#-authors)
- [📄 License](#-license)

---

## 💥 The Problem

Going out in a new city (or even your own) is still mostly trial-and-error:

- You ask friends, scroll TikTok, or read random reviews.
- Reviews are **unstructured, noisy, and biased** (“nice place”, “good music”, “5 stars” – but you still don’t know if it fits *your* vibe).
- Apps show ratings, photos, maybe “popular now” – but **not**:
  - “Is this place similar to *that* legendary night we had last month?”
  - “Is this bar a **doppelgänger** of that kafana where I drank rakija until 3am?”

Existing platforms optimize for **average rating**, not for **your ideal night**.

---

## 💡 The Solution

**NightTwin** is an AI system that finds **doppelgängers of your ideal night out**, not just “4.6-star bars”.

You write a natural language prompt like:

> “I want to drink rakija with 2 friends in Dorćol around 2am, loud Balkan music, budget up to 100€.”

NightTwin:

1. Uses an LLM to extract **structured intent** (city, time, budget level, party level, vibe tags).
2. Embeds your request in a **semantic space** together with tens of thousands of past “nights out”.
3. Finds historical **nights that are most similar to your request**.
4. Aggregates them into venues whose past nights are the **closest doppelgängers to your desired night**.
5. Returns top venues with human-readable explanations:  
   > “We recommend this place because previous nights here had high party level, strong rakija + kafana vibes, and similar group size & budget.”

---

## ✨ Key Features

### 1. 🧠 Prompt-to-Intent Extraction (LLM as a Parser)

- User can type **anything**: casual Serbian/English mix, vague description, even slang.
- A GPT-based “Prompt Parser” converts this into:
  - `city`
  - `day_of_week`
  - `time`
  - `group_size` (1–10+)
  - `budget_level` (1–5)
  - `party_level` (1–5)
  - `tags` (e.g. `["kafana", "rakija", "live music", "crowded"]`)
- This turns **fuzzy text** into a structured query the engine can reason about.

### 2. 🧬 Doppelgänger Search Engine (Semantic + Structured)

- Each historical night is represented by:
  - A **structured feature vector** (city, day, weekend flag, music type, vibe tags, normalized budget/party/crowd/etc.).
  - A **semantic embedding** of its description.
- For each user request we compute:
  - Semantic similarity (cosine in embedding space).
  - Structural match (dot product over normalized features).
- Final score = **semantic similarity + λ × structural similarity**.

This creates a **“night twin” similarity notion** – not just text similarity, but full behavioral/context match.

### 3. 🚦 Prompt Quality Guardrails

To avoid misleading results, we explicitly judge the **quality of the user’s prompt**:

- If **best similarity < 60%** →  
  `status = "no_match"` → we **don’t** show venues, but ask user to adjust the request.
- If **too many nights are extremely similar** (prompt is too generic) →  
  `status = "too_broad"` → we ask user to narrow down (e.g. specify city or vibe).
- Only **“healthy” prompts** (`status = "ok"`) return venue recommendations.

This gives the jury a clear **trust & safety story** for the AI component.

### 4. 🧭 Transparent Explanations (“Why this place?”)

For each recommended venue we generate bullet-point explanations based on data:

- City & area match (e.g. **Dorćol, Belgrade**).
- Typical party level vs requested party level.
- Intersection between venue’s top vibe tags and user’s requested tags.
- Typical hours vs requested time (“fits late-night outings”).

You don’t just get “4.7★ bar” – you get **“nightlife twins” with reasons**.

---

## 🧠 AI & Modeling

### 📊 Dataset & Preprocessing

We designed the pipeline to make judges happy on:

- dataset quality,
- preprocessing,
- explainability.

**Data source (conceptual):**

- We scraped **Google Maps reviews and metadata** for nightlife venues in Serbian cities  
  (e.g. Belgrade, Novi Sad, Niš, Kragujevac, Subotica, Sombor, Zlatibor, Kraljevo) using a local Python script.
- For each venue we collected:
  - Name, location (city, area),
  - Category (bar, club, kafana, lounge),
  - Rating & review count,
  - Free-text reviews.

> ⚠️ The scraping + raw data scripts are **kept local** and are **not in this repo**, to respect Terms of Service.  
> This repository only contains **processed, aggregated data**.

**From raw reviews to structured “nights out”:**

We used local preprocessing scripts:

- `backend/data/serbia_nightlife_dataset.csv` – base events/visits per venue.
- `backend/scripts/build_venues.py` – aggregates venue-level stats:
  - average budget / party level,
  - typical start/end time,
  - top vibe tags.
- `backend/scripts/preprocess_nights.py` – builds final training/serving dataset:
  - normalizes and encodes:
    - city, day_of_week, season,
    - venue_type, music_type, vibe tags,
    - group_size, budget_level, party_level, crowd_level, alcohol_level, etc.
  - produces:
    - `features_config.json` – vocabularies + numeric ranges.
    - `nights_features.jsonl` – one row per “night out”, with:
      ```jsonc
      {
        "night_id": ...,
        "venue_id": ...,
        "city": "...",
        "day_of_week": "...",
        "struct_features": [ ... floats ... ],
        "text_for_embedding": "Night out at ...",
        "embedding": [ ... floats ... ]
      }
      ```

**Why this preprocessing matters:**

- **City / day / weekend** help us separate very different behavior patterns (e.g. Monday vs Saturday).
- **Normalized numeric features** (0–1) allow us to combine structural and semantic similarity in a stable way.
- **Vibe tags & music type** capture what users actually care about (kafana vs techno vs chill rooftop).
- This makes our similarity metric not just “textual,” but **behavioral & contextual**.

### 🧬 Model Experiments & Final Choice

We tested multiple models from the **OpenAI API** for two distinct tasks:

#### 1. Prompt Parsing (LLM → Structured Query)

We tried:

- `gpt-4.1-mini`
- `gpt-4.1`

**Why these models:**

- `gpt-4.1-mini`:
  - Very fast and cheap → ideal for interactive, per-request parsing.
  - Already good enough at extracting fields (city, time, budget, tags) with **JSON output**.
- `gpt-4.1`:
  - Higher quality, but slower and more expensive.
  - We used it in early experiments to validate prompt design and edge cases.

**Final choice for hackathon:**  
We use **`gpt-4.1-mini`** in production (`PromptParser`) because:

- It hits the sweet spot between **speed, cost, and accuracy** for structured extraction.
- The JSON schema is small and fixed → errors are easy to catch and validate.

#### 2. Semantic Similarity (Embeddings for Nights & Queries)

We experimented with:

- `text-embedding-3-small`
- `text-embedding-3-large` (and conceptually compared to older `text-embedding-ada-002`)

**Why `text-embedding-3-small`:**

- Extremely cheap: optimized for high-volume applications.
- Embedding quality is more than sufficient for:
  - short “night out” descriptions,
  - ranking of similar nights.
- With our preprocessing (features + tags), we **don’t need** the extra cost of `-large`.

**Final choice for hackathon:**  
We use **`text-embedding-3-small`** for:

- all historical nights (`preprocess_nights.py`), and
- each incoming query (inside `NightTwinSearchEngine`).

### 🧬 Where Is the “Doppelgänger”?

The “doppelgänger” concept appears in two layers:

1. **Night-level doppelgängers**  
   - For each user query we find the **most similar historical nights**:
     - same city and weekend/weekday type,
     - similar time, budget, party level, vibes,
     - high semantic similarity of descriptions.
   - These are the **“night twins”** of your requested experience.

2. **Venue-level doppelgängers**  
   - We then aggregate top nights by venue and compute an average score per venue.
   - A recommended venue is essentially:
     > “The place where past nights look the most like the night you just described.”

So NightTwin is literally a **“Find the night’s doppelgänger” engine**, not just a generic recommender.

---

## 🏗 Architecture & Tech Stack

### 🧰 Tech Stack

- **Backend:**
  - Python 3
  - FastAPI (REST API)
  - Uvicorn (ASGI server)
  - NumPy, Pandas (data & vector operations)
  - OpenAI Python SDK (LLM + embeddings)

- **Frontend:**
  - React (or Next.js) + TypeScript
  - Vite or Next dev server
  - TailwindCSS for quick styling

- **Infra (Hackathon):**
  - Yandex Cloud Compute (for hosting backend + preprocessing)
  - (Optionally) Yandex Object Storage / Managed DB for persistence

---

### 🧱 System Architecture

```mermaid
graph LR
    U[User] --> FE["Frontend Web App"]
    FE -->|free-text prompt| PS["POST /prompt-search"]

    subgraph Backend_FastAPI
        PP["PromptParser (GPT-4.1-mini)"]
        SE[NightTwinSearchEngine]
        NS[(Night Dataset)]
        RES["Ranked Venues + Reasons"]

        PS --> PP
        PP --> SE
        SE --> NS
        NS --> SE
        SE --> RES
    end

    RES --> FE
```

---

## 🔥 How It Works (End-to-End Flow)

### 1. User Prompt

User types something like:
> “I want a crazy kafana in Belgrade with rakija, 3 friends, around 2am, budget up to 100€ for all of us.”

Frontend sends:

``` text
POST /prompt-search
Content-Type: application/json

{
  "prompt": "I want a crazy kafana in Belgrade with rakija, 3 friends, around 2am, budget up to 100€..."
}
```

### 2. Prompt Parsing (LLM)

PromptParser calls gpt-4.1-mini with a strict JSON schema and gets something like:

```jsonc
{
  "valid": true,
  "city": "Belgrade",
  "day_of_week": "Saturday",
  "time": "02:00",
  "group_size": 4,
  "budget_level": 3,
  "party_level": 5,
  "tags": ["kafana", "rakija", "live music", "crowded"]
}
```

This is converted into a SearchRequest / SearchQueryParams.

### 3. Guardrails: Is the Prompt Good?

`NightTwinSearchEngine.search_with_prompt_guardrail()`:

- Computes embeddings for the query using `text-embedding-3-small`.
- Filters historical nights by:
  - same **city**,
  - same **weekend vs weekday** type.
- Computes **semantic + structured similarity** for all candidate nights.
- Analyzes the semantic similarity distribution:
  - If **max similarity < 0.6** → `status = "no_match"`.
  - If **too many nights ≥ 0.8 similarity** → `status = "too_broad"`.
  - Otherwise → `status = "ok"`.

If `status != "ok"`, the backend returns **no venues**, but a human-readable message explaining the issue.

---

### 4. Doppelgänger Search & Ranking

If the prompt is good (`status = "ok"`):

1. We pick **top-N most similar nights**.
2. Aggregate similarity scores per venue.
3. Rank venues by their **average score**.

For each top venue, we also generate explanations based on:

- matching **city & area**,
- **party level** alignment,
- overlapping **vibe tags**,
- typical **opening hours** vs requested time.


### 5. Frontend Display

Frontend receives:

```jsonc
{
  "status": "ok",
  "reason": "Query matched a reasonable number of nights.",
  "parsed_query": {
    "city": "Belgrade",
    "day_of_week": "Saturday",
    "time": "02:00",
    "group_size": 4,
    "budget_level": 3,
    "party_level": 5,
    "tags": ["kafana", "rakija", "live music", "crowded"]
  },
  "venues": [
    {
      "venue_id": 42,
      "name": "Kafana NightTwin Example",
      "city": "Belgrade",
      "area": "Dorćol",
      "venue_type": "kafana",
      "score": 0.91,
      "reasons": [
        "This venue is in Dorćol, Belgrade, matching your city selection.",
        "Average party level here is high, matching your request for a crazy night.",
        "Guests often describe this place with similar vibe tags you requested: kafana, rakija, live music.",
        "Typical opening hours from 22:00 to 04:00, which fits late-night outings."
      ]
    }
  ]
}
```

Frontend renders these as cards.

---

## 🛠 Getting Started

### Prerequisites

- **Python** 3.10+
- **Node.js** 18+
- **OpenAI API key**
- (Optional) **Docker** if you want containerized deployment.

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/nighttwin.git
cd nighttwin
```

### 2. Backend Setup (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a .env file in backend/:

```bash
OPENAI_API_KEY=your_openai_key_here
VECTOR_DB_URL=postgresql://user:pass@host:5432/nighttwin  # or your vector DB
ENV=dev
```

Run the backend:

```bash
uvicorn app.main:app --reload
```

By default it will run on http://localhost:8000

---

## 🧪 Example Queries

Try prompts like:

- “I love **Bar Botticelli** in Novi Sad – find me a similar bar in Belgrade for a Friday night date.”
- “Show me the twin of **Drugstore** in Belgrade in Berlin, but for a smaller, more intimate techno venue.”
- “Find a doppelgänger of a **cheap student bar with Balkan music** in another city, no tourists, smoking allowed.”

These are great for live demos because they clearly show:

- Understanding of **context** (city transfer).
- Understanding of **vibe**, not just rating.
- The **doppelgänger** concept in action.

---

## 🚀 Future Work

Some directions we’d like to explore:

### Richer behavioral signals

- Incorporate visit times, local peak hours, and maybe ticket / event data.

### Cold-start for new venues

- Use owners’ descriptions + early reviews to bootstrap embeddings.

### User profiling

- Learn a personal **“taste vector”** across multiple liked venues.

### Multi-city trip planning

- Build a full **nightlife itinerary** across several cities based on your taste.

---

## 👥 Authors

Team **Lucky 3**:

- **Milan Sazdov** – [LinkedIn](https://www.linkedin.com/in/milansazdov)
- **Lazar Sazdov** – [LinkedIn](https://www.linkedin.com/in/lazarsazdov)
- **Vedran Bajić** – [LinkedIn](https://www.linkedin.com/in/vedran-bajic-53a231222/?originalSubdomain=rs)
- **Nikola Nikolić** – [LinkedIn](https://www.linkedin.com/in/nikola-nikoli%C4%87-856786279/)

---

## 📄 License

This project is licensed under the **MIT License**.  
See the [LICENSE](./LICENSE) file for details.

