# 🌙 NightTwin: Find Your Nightlife Doppelgänger

![NightTwin Banner](./assets/banner.png)
<div align="center">

**Your favorite bar has a twin in every city.** NightTwin finds venues that *feel* like your go-to spot – same vibe, different location.

[![Hackathon](https://img.shields.io/badge/Reputeo%20x%20Yandex-AI%20Hackathon-blue)]()
[![Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20React%20%7C%20OpenAI-brightgreen)]()
[![Search](https://img.shields.io/badge/Search-Embeddings%20%7C%20LLM%20Ranking-purple)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

[**🎥 WATCH THE DEMO**](#) · [**🚀 OPEN NIGHTTWIN**](#)

</div>

---

## 📖 Table of Contents

- [💥 The Problem](#-the-problem)
- [💡 The Solution](#-the-solution)
- [🧬 Where Is the “Doppelgänger”?](#-where-is-the-doppelgänger)
- [📊 Dataset & Collection](#-dataset--collection)
- [🧹 Preprocessing Pipeline](#-preprocessing-pipeline)
- [🧠 Models & Why We Chose Them](#-models--why-we-chose-them)
- [🏗 Architecture & Tech Stack](#-architecture--tech-stack)
- [🔥 How It Works (The Flow)](#-how-it-works-the-flow)
- [🛠 Getting Started](#-getting-started)
- [🧪 Example Queries](#-example-queries)
- [🚀 Future Work](#-future-work)
- [👥 Authors](#-authors)
- [📄 License](#-license)

---

## 💥 The Problem

Discovering nightlife in a **new city** is still mostly:

- Top-10 lists of **touristy places**.
- Generic filters like *“4.5★, near city center, $$$”*.
- Zero understanding of **your personal vibe**:  
  *“chill jazz bar with dim lights”* vs *“sweaty techno bunker”* vs *“loud Balkan kafana with live music”*.

Existing platforms:
- Optimize for **popularity**, not **personal similarity**.
- Don’t transfer your taste: if you love one bar at home, there’s no way to say  
  > “Show me the **same kind of place** in another city.”

---

## 💡 The Solution

**NightTwin** is a vibe-based venue recommender.

Instead of searching *“bars in Belgrade”*, you say:

> “I love **[Your Favorite Place]** in **[Your City]** —  
> find me its **nightlife doppelgänger** in **[Target City]**.”

NightTwin then:

- Understands the **vibe, crowd, mood, music, and use case** of your favorite venue.
- Searches across thousands of venues in the target city.
- Returns places that **feel like your original**, not just “also 4.6★”.

**For users:** frictionless way to feel at home in a new city.  
**For venues:** fair discovery based on *fit*, not just ads and raw rating.

---

## 🧬 Where Is the “Doppelgänger”?

We define a **nightlife doppelgänger** as:

> > A venue in another city whose **semantic “vibe embedding”** is closest  
> > to your favorite place, under constraints like price level, noise, and crowd.

Concretely:

1. Every venue is represented as a **high-dimensional vector** built from:
   - Google Maps reviews (text)
   - Ratings & volume of reviews
   - LLM-extracted attributes (e.g. *“loud”, “romantic”, “groups”, “live music”*).
2. When you pick a favorite place, we:
   - Build / fetch its embedding.
   - Find **nearest neighbors** in the target city using vector search.
3. We then re-rank candidates with an LLM so the final list matches:
   - **Vibe** (music, crowd, mood).
   - **Context** (date night vs pre-drink vs afterparty).
   - **Practical filters** (budget, location, smoking, etc).

The “twin” is therefore not a clone of the menu or address —  
it’s a clone of the **experience**.

---

## 📊 Dataset & Collection

We built our dataset around **Google Maps reviews**:

- We **scraped Google Maps** for nightlife venues (bars, clubs, lounges, pubs, kafanas…) in selected cities.
- For each venue we collected:
  - Name, address, category
  - Overall rating + number of reviews
  - Raw review texts (top-N recent & most relevant)
- Using the **OpenAI API**, we converted unstructured reviews into **structured attributes** per venue:
  - Primary & secondary **vibes** (e.g. *“cozy jazz”, “underground techno”, “student bar”*)
  - Typical **crowd** (locals vs tourists, age range)
  - **Use cases** (date night, pre-drink, groups, solo, etc.)
  - **Noise level**, **dress code**, **price level**
  - Safety / “sketchiness” hints if reviewers mentioned them.

All of this was processed in a **local Python script**, then exported to a clean dataset consumed by our backend.

---

## 🧹 Preprocessing Pipeline

Our preprocessing focused on making noisy review data usable for retrieval:

1. **Scraping & Normalization**
   - Scrape venue metadata + reviews.
   - Normalize city & country names, categories, and addresses.
   - Deduplicate venues across small changes in names or typos.

2. **Review Cleaning**
   - Remove:
     - Very short reviews (e.g. “Nice 👍”).
     - Non-informative texts (emoji-only, pure ratings).
   - Basic text normalization: lowercasing, stripping HTML / markup.

3. **Language & Quality Filtering**
   - Detect review language and keep only languages we can reliably process.
   - Filter out spammy reviews (e.g. repeated patterns, copied texts).

4. **LLM-Based Structuring (OpenAI)**
   - Batch reviews per venue into concise context.
   - Use OpenAI models to extract:
     - Categorical tags (vibe, music type, crowd).
     - Continuous attributes (noise level, price band etc.).
   - Store results as a structured JSON per venue.

5. **Final Venue Object**
   - Each venue becomes a `Venue` document with:
     - Raw fields: name, rating, location.
     - LLM-derived fields: vibe tags, crowd, use cases.
     - Precomputed **embedding vector** for fast similarity search.

This pipeline runs **offline**, so the online experience is fast and responsive.

---

## 🧠 Models & Why We Chose Them

We use OpenAI models in two main places:

1. **Understanding & tagging venues (LLM)**
2. **Building vector representations (embeddings)**

### 1. LLMs for Structuring & Re-ranking

We experimented with several OpenAI chat models for tagging venues from reviews:

- `gpt-4.1-mini`
- `gpt-4o`
- `o3-mini` (for reasoning-heavy classification on a small subset)

**Why we ended up with `gpt-4.1-mini` for tagging:**

- **Quality:** Captured nuanced concepts like *“good for pre-drink”* vs *“end-of-night place”* reliably.
- **Latency:** Fast enough for batch processing hundreds of venues.
- **Cost:** Much cheaper than full `gpt-4o` while keeping almost the same tagging quality for our task.

For **re-ranking candidates online**, we use a **lightweight LLM call**:

- Input: user’s favorite venue description + candidate venues + user filters.
- Output: sorted list with natural-language justification (“why this is your twin”).
- Here we prioritize **quality over cost**, so we can optionally switch to a stronger model (e.g. `gpt-4o`) when needed.

### 2. Embedding Models for Similarity

For semantic search, we evaluated:

- `text-embedding-3-small`
- `text-embedding-3-large`

We ended up using **`text-embedding-3-small`** as the default because:

- It provides **excellent semantic clustering** for reviews & tags.
- It is **significantly cheaper** per vector than the large model.
- In our manual evaluation (checking top-k “twins” for a sample of venues), the difference vs `3-large` was not big enough to justify the cost at hackathon scale.

**Workflow:**

- Build embeddings for:
  - Venue descriptions (raw + LLM-compressed)
  - LLM-generated tags and attributes
- At query time:
  - Embed the **favorite venue**.
  - Search nearest neighbors in the target city.
  - Feed candidates + user constraints to the LLM to get the final ranked list.

---

## 🏗 Architecture & Tech Stack

### Tech Stack

- **Frontend:** React / Next.js, TypeScript, TailwindCSS
- **Backend:** FastAPI (Python), Uvicorn
- **AI & Search:**
  - OpenAI Chat & Embeddings API
  - Vector store (e.g. PostgreSQL + pgvector / Qdrant / Chroma)
- **Data & Tooling:** Python, Pandas, local scraping & preprocessing scripts
- **Infra:** Docker, (Vercel / Railway / similar) for deployment

### System Architecture

```mermaid
graph LR
    User((User)) --> UI[Web App (NightTwin Frontend)]
    UI --> API[FastAPI Backend]

    subgraph "Offline Pipeline"
        Scrape[Google Maps Scraper] --> Clean[Cleaning & Normalization]
        Clean --> LLMTag[OpenAI LLM Tagger]
        LLMTag --> Embed[Embedding Builder]
        Embed --> VecDB[(Vector DB)]
    end

    API --> VecDB
    API --> OpenAI[OpenAI API]

    VecDB --> API
    OpenAI --> API

    API --> UI
```

## 🔥 How It Works (The Flow)

### 1. Offline: Build the Nightlife Graph

- Scrape venues + reviews from Google Maps.
- Clean, filter, and normalize entries.
- Use OpenAI to:
  - Summarize reviews.
  - Extract structured tags (vibe, crowd, use cases, noise, etc.).
- Compute embeddings for each venue.
- Store everything in a vector database.

### 2. Online: Find Your Night Twin

#### User Input

- User selects:
  - Home city + favorite venue  
    **or**
  - Describes their ideal place in natural language.
- Optionally adds filters: “no tourists”, “cheap drinks”, “live music”, “smoking allowed”…

#### Candidate Retrieval

- Backend fetches / embeds the favorite venue (or the text description).
- Performs a **k-NN search** in the vector DB, restricted to the target city.
- Returns top-N candidate venues.

#### LLM Re-Ranking

An LLM receives:

- User preferences.
- Favorite venue description.
- Candidate venues with tags & metadata.

It reorders candidates and explains **why** each is a good “twin”.

#### Response to User

The frontend shows:

- Top 3–5 doppelgängers with:
  - Short *vibe description*
  - Key tags (music, crowd, price, noise)
  - Maps link.

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

Team **NightTwin**:

- **Milan Sazdov** – [LinkedIn](https://www.linkedin.com/in/milansazdov)
- **Lazar Sazdov** – [LinkedIn](https://www.linkedin.com/in/lazarsazdov)
- **Vedran Bajić** – [LinkedIn](https://www.linkedin.com/in/vedran-bajic-53a231222/?originalSubdomain=rs)
- **Nikola Nikolić** – [LinkedIn](https://www.linkedin.com/in/nikola-nikoli%C4%87-856786279/)

---

## 📄 License

This project is licensed under the **MIT License**.  
See the [LICENSE](./LICENSE) file for details.

