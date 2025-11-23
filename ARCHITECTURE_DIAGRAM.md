# Night-Twin Architecture Diagram

## System Overview

Night-Twin is an AI-powered nightlife recommendation system for Serbian venues that uses semantic search and OpenAI embeddings to match users with their ideal night out experiences.

```
┌──────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE (Frontend)                    │
│                    React + TypeScript + Vite                         │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │
│  │   Landing    │  │    Option    │  │    Gallery   │                │
│  │     Page     │  │     Page     │  │     Page     │                │
│  └──────────────┘  └──────────────┘  └──────────────┘                │
│         │                 │                  │                       │
│         └─────────────────┴──────────────────┘                       │
│                           │                                          │
└───────────────────────────┼──────────────────────────────────────────┘
                            │
                            │ HTTP/REST API
                            │ (CORS enabled)
                            ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      API LAYER (FastAPI)                             │
│                   backend/app/main.py                                │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │
│  │   GET /health    │  │  POST /search    │  │ POST /prompt-    │    │
│  │                  │  │   (structured)   │  │    search        │    │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘    │
│                                │                       │             │
└────────────────────────────────┼───────────────────────┼─────────────┘
                                 │                       │
                                 ▼                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       BUSINESS LOGIC LAYER                           │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │              NightTwinSearchEngine                             │  │
│  │          (app/services/search_engine.py)                       │  │
│  │                                                                │  │
│  │  • Load venues & nights data                                   │  │
│  │  • Build feature vectors (struct + embeddings)                 │  │
│  │  • Compute similarity scores                                   │  │
│  │  • Filter by city/day/weekend                                  │  │
│  │  • Aggregate venues + generate reasons                         │  │
│  │  • Guardrails (no_match, too_broad detection)                  │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                 │                                    │
│                                 │                                    │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    PromptParser                                │  │
│  │            (app/services/prompt_parser.py)                     │  │
│  │                                                                │  │
│  │  • Parse natural language prompts                              │  │
│  │  • Extract structured parameters (city, time, budget, etc.)    │  │
│  │  • Uses OpenAI GPT-4.1-mini for extraction                     │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
└───────────────────────────────────┬──────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                 │
│                                                                     │
│  ┌─────────────────────┐  ┌─────────────────────┐                   │
│  │   venues.csv        │  │ nights_features.    │                   │
│  │                     │  │      jsonl          │                   │
│  │ • venue_id          │  │                     │                   │
│  │ • name, city, area  │  │ • night_id          │                   │
│  │ • venue_type        │  │ • venue_id          │                   │
│  │ • avg stats         │  │ • struct_features   │                   │
│  │ • top_vibe_tags     │  │ • embedding (768d)  │                   │
│  └─────────────────────┘  └─────────────────────┘                   │
│                                                                     │
│  ┌─────────────────────┐  ┌─────────────────────┐                   │
│  │ features_config.    │  │  nights_with_       │                   │
│  │      json           │  │    venues.csv       │                   │
│  │                     │  │                     │                   │
│  │ • vocabularies      │  │ • raw nights data   │                   │
│  │ • feature indices   │  │ • joined with       │                   │
│  │ • numeric ranges    │  │   venue_id          │                   │
│  └─────────────────────┘  └─────────────────────┘                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │
                                    │ (Generated offline)
                                    │
┌─────────────────────────────────────────────────────────────────────┐
│                    PREPROCESSING PIPELINE                           │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              build_venues.py                                  │  │
│  │  (scripts/build_venues.py)                                    │  │
│  │                                                               │  │
│  │  1. Read serbia_nightlife_dataset.csv                         │  │
│  │  2. Group by (name, city, area)                               │  │
│  │  3. Compute venue stats & infer venue_type                    │  │
│  │  4. Generate venues.csv                                       │  │
│  │  5. Attach venue_id → nights_with_venues.csv                  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                            ▼                                        │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │            preprocess_nights.py                               │  │
│  │  (scripts/preprocess_nights.py)                               │  │
│  │                                                               │  │
│  │  1. Read nights_with_venues.csv                               │  │
│  │  2. Build vocabularies & normalize features                   │  │
│  │  3. Generate struct_features vector per night                 │  │
│  │  4. Call OpenAI embeddings API                                │  │
│  │  5. Save features_config.json + nights_features.jsonl         │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │
                                    │
┌─────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                              │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    OpenAI API                                 │  │
│  │                                                               │  │
│  │  • Model: text-embedding-3-small                              │  │
│  │  • Used for: night descriptions → 768d vectors                │  │
│  │  • Used for: query text → 768d vectors                        │  │
│  │  • Model: gpt-4.1-mini (for prompt parsing)                   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### Frontend (React + TypeScript)

**Location:** `/front`

**Key Components:**
- `App.tsx` - Main application router and state
- `Navbar.tsx` - Navigation component
- `LoginForm.tsx` / `RegisterForm.tsx` - Authentication UI
- `OptionPage.tsx` - User input form for search parameters
- `Gallery.tsx` - Display search results
- `PartyGoer.tsx` - User profile/preferences
- `CursorLight.tsx` / `Fog.tsx` - Visual effects

**Tech Stack:**
- React 18+
- TypeScript
- Vite (build tool)
- CSS Modules

---

### Backend API (FastAPI)

**Location:** `/backend/app`

#### Core Endpoints

1. **`GET /health`**
   - Health check endpoint
   - Returns: `{"status": "ok"}`

2. **`POST /search`**
   - Structured search with explicit parameters
   - Input: `SearchRequest` (city, day_of_week, time, group_size, budget_level, party_level, tags)
   - Output: `List[VenueResult]`
   - Flow:
     1. Map to `SearchQueryParams`
     2. Call `search_engine.search()`
     3. Return ranked venues with scores & reasons

3. **`POST /prompt-search`**
   - Natural language search
   - Input: `PromptSearchRequest` (free-text prompt)
   - Output: `PromptSearchResponse` (status, parsed_query, venues)
   - Flow:
     1. `PromptParser.parse_prompt()` → extract structured query via GPT
     2. Validate prompt (valid/invalid)
     3. `search_engine.search_with_prompt_guardrail()` → check for bad prompts
     4. Return venues or status (ok/no_match/too_broad/invalid)

#### Data Models (`app/models.py`)

```python
SearchRequest:
  - city: str
  - day_of_week: str
  - time: str (HH:MM)
  - group_size: int
  - budget_level: int (1-5)
  - party_level: int (1-5)
  - tags: List[str]

VenueResult:
  - venue_id: int
  - name, city, area: str
  - venue_type: str
  - score: float
  - reasons: List[str]

PromptSearchResponse:
  - status: "ok" | "no_match" | "too_broad" | "invalid"
  - reason: str
  - parsed_query: SearchRequest | None
  - venues: List[VenueResult]
```

---

### Search Engine (`app/services/search_engine.py`)

**Core Responsibilities:**

1. **Data Loading**
   - Load `venues.csv` → `Dict[int, VenueInfo]`
   - Load `nights_features.jsonl` → `List[NightRecord]`
   - Load `features_config.json` → vocabularies & ranges

2. **Query Feature Construction**
   - Build struct_features vector (one-hot + multi-hot + normalized numerics)
   - Build query embedding via OpenAI (if available)

3. **Similarity Scoring**
   - **Structural similarity:** dot product of struct_features
   - **Semantic similarity:** cosine similarity of embeddings
   - **Combined score:** `sem_sim + λ * struct_sim` (default λ=0.5)

4. **Filtering & Ranking**
   - Filter nights by city & weekend/weekday
   - Rank nights by combined score
   - Aggregate to venues (average scores)
   - Return top-k venues

5. **Guardrails** (`search_with_prompt_guardrail()`)
   - **no_match:** best semantic similarity < 0.6
   - **too_broad:** >20% of nights have semantic similarity ≥ 0.8
   - **ok:** normal query, return venues

6. **Explanation Generation**
   - Reasons why each venue matches the query
   - Based on: location, party level, vibe tags, typical hours

**Feature Vector Structure:**

```
struct_features = [
  city_one_hot (len=8),
  day_one_hot (len=7),
  season_one_hot (len=4),
  location_type_one_hot (len=N),
  music_type_one_hot (len=M),
  vibe_tags_multi_hot (len=30),
  numeric_features (len=11):
    - group_size_norm
    - budget_norm
    - party_norm
    - alcohol_norm
    - crowd_norm
    - duration_norm
    - temperature_norm
    - cost_norm
    - tip_norm
    - start_time_norm
    - is_weekend
]
```

---

### Prompt Parser (`app/services/prompt_parser.py`)

**Purpose:** Convert natural language prompts to structured queries

**Flow:**
1. User prompt → OpenAI GPT-4.1-mini (JSON mode)
2. Extract fields: city, day_of_week, time, group_size, budget_level, party_level, tags
3. Validate: is it a nightlife request?
4. Apply fallbacks: default city=Belgrade, day=Saturday, etc.
5. Return `ParsedPrompt` → convert to `SearchRequest`

**Supported Cities:**
- Belgrade, Novi Sad, Nis, Kragujevac, Subotica, Sombor, Zlatibor, Kraljevo

**Example:**
```
Input: "Want to go out in Belgrade tomorrow night with 3 friends, 
        looking for techno club, medium budget"

Output:
  city: Belgrade
  day_of_week: Saturday (inferred)
  time: 23:00
  group_size: 4
  budget_level: 3
  party_level: 4
  tags: ["techno", "club"]
```

---

### Preprocessing Pipeline

#### 1. `build_venues.py`

**Input:** `serbia_nightlife_dataset.csv` (raw nights data)

**Process:**
1. Group nights by `(name, city, area)` → define venues
2. Compute venue statistics:
   - avg_budget_level, avg_party_level, avg_cost, avg_tip
   - avg_alcohol_level, avg_crowd_density
   - typical_start_time, typical_end_time (median)
   - dominant_day_of_week, dominant_location_type, dominant_music_type
   - top_vibe_tags (top 5 by frequency)
3. Infer `venue_type` (kafana, club, pub, rock_bar, cocktail_bar, bar)
4. Assign `venue_id` (sequential)

**Outputs:**
- `venues.csv` - one row per venue
- `nights_with_venues.csv` - raw nights + venue_id

#### 2. `preprocess_nights.py`

**Input:** `nights_with_venues.csv`

**Process:**
1. Parse time features (start_time, end_time → minutes, duration)
2. Compute is_weekend flag
3. Build global vocabularies (cities, days, seasons, location_types, music_types, top 30 vibe_tags)
4. Normalize numeric features (min-max)
5. For each night:
   - Build struct_features vector (one-hot + multi-hot + numeric)
   - Build text description
   - Call OpenAI `text-embedding-3-small` → 768d embedding
6. Save features_config.json (vocabularies + numeric_ranges)
7. Save nights_features.jsonl (one JSON line per night)

**Outputs:**
- `features_config.json` - vocabularies & feature layout
- `nights_features.jsonl` - night_id, venue_id, struct_features, embedding

---

## Data Flow Diagrams

### Search Flow (Structured)

```
User → Frontend Form
  ↓ (fill city, day, time, group_size, budget, party, tags)
  ↓ POST /search
Backend API
  ↓ SearchRequest
SearchEngine.search()
  ↓ build query features
  ↓ filter nights by city/weekend
  ↓ compute similarities
  ↓ aggregate to venues
  ↓ generate reasons
  ↓ List[VenueResult]
Frontend Gallery
  ↓ display results
User sees recommendations
```

### Prompt Search Flow

```
User → Frontend (free-text input)
  ↓ "I want a chill kafana in Belgrade on Friday"
  ↓ POST /prompt-search
Backend API
  ↓ PromptSearchRequest
PromptParser.parse_prompt()
  ↓ call OpenAI GPT-4.1-mini
  ↓ extract structured fields
  ↓ ParsedPrompt
  ↓ validate & apply fallbacks
  ↓ SearchRequest
SearchEngine.search_with_prompt_guardrail()
  ↓ build query features
  ↓ filter nights
  ↓ compute semantic similarities
  ↓ check guardrails (no_match? too_broad?)
  ↓ if ok: rank & aggregate venues
  ↓ GuardedSearchResult
Backend API
  ↓ map to PromptSearchResponse
  ↓ {status, reason, parsed_query, venues}
Frontend Gallery
  ↓ display results or show status message
User sees recommendations or refinement suggestion
```

---

## Technology Stack

### Backend
- **Language:** Python 3.13
- **Framework:** FastAPI 0.121+
- **Server:** Uvicorn (ASGI)
- **Data Processing:** Pandas, NumPy
- **Embeddings:** OpenAI API (`text-embedding-3-small`, 768d)
- **Prompt Parsing:** OpenAI GPT-4.1-mini
- **Environment:** `.env` file for `OPENAI_API_KEY`

### Frontend
- **Language:** TypeScript
- **Framework:** React 18+
- **Build Tool:** Vite
- **Styling:** CSS Modules
- **HTTP Client:** Fetch API / Axios (likely)

### Development
- **Virtual Environment:** Python venv (`.venv/`)
- **Package Management:** pip, npm
- **Version Control:** Git
- **API Documentation:** FastAPI auto-generated docs at `/docs`

---

## Deployment Architecture

### Local Development

```
Terminal 1: Backend Server
  cd backend
  & ..\.venv\Scripts\python.exe run_server.py
  → http://127.0.0.1:8000 (reload ON)

Terminal 2: Frontend Dev Server
  cd front
  npm run dev
  → http://localhost:5173 (default Vite port)

Browser
  → Frontend makes API calls to http://127.0.0.1:8000
```

### Production (Recommended)

```
┌─────────────────────────────────────────────┐
│         Load Balancer / Reverse Proxy       │
│              (Nginx / Traefik)              │
└──────────────┬─────────────────┬────────────┘
               │                 │
               ▼                 ▼
      ┌────────────────┐  ┌─────────────────┐
      │    Frontend    │  │    Backend      │
      │   (Static)     │  │   (FastAPI)     │
      │  Nginx/CDN     │  │  Gunicorn +     │
      │                │  │   Uvicorn       │
      └────────────────┘  └────────┬────────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │   Data Files     │
                          │  (Read-only or   │
                          │   Object Store)  │
                          └──────────────────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │   OpenAI API     │
                          │  (External)      │
                          └──────────────────┘
```

**Key Considerations:**
- Frontend: Static files served by CDN or Nginx
- Backend: Multiple Uvicorn workers behind Gunicorn or directly with Uvicorn
- Data: Mount data folder as read-only volume or use object storage (S3/Azure Blob)
- Secrets: `OPENAI_API_KEY` via environment variables or secret manager
- CORS: Configure allowed origins for production domain

---

## File Structure

```
Night-Twin/
├── backend/
│   ├── .env                    # Secrets (OPENAI_API_KEY)
│   ├── run_server.py           # Dev server launcher
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app + endpoints
│   │   ├── models.py           # Pydantic models
│   │   ├── repositories/       # (future: DB access)
│   │   │   ├── nights_repository.py
│   │   │   └── venues_repository.py
│   │   └── services/
│   │       ├── embedding_client.py
│   │       ├── prompt_parser.py
│   │       └── search_engine.py
│   ├── data/                   # Generated data (gitignored)
│   │   ├── serbia_nightlife_dataset.csv
│   │   ├── venues.csv
│   │   ├── nights_with_venues.csv
│   │   ├── features_config.json
│   │   └── nights_features.jsonl
│   └── scripts/
│       ├── build_venues.py     # Step 1: venue aggregation
│       └── preprocess_nights.py # Step 2: feature generation
│
├── front/
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx            # Entry point
│   │   ├── App.tsx             # Main app component
│   │   ├── components/
│   │   │   ├── Navbar.tsx
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   ├── OptionPage.tsx
│   │   │   ├── Gallery.tsx
│   │   │   └── PartyGoer.tsx
│   │   └── assets/
│   └── public/
│
├── .gitignore
├── readme.md
└── ARCHITECTURE_DIAGRAM.md     # This file
```

---

## Key Design Decisions

### 1. Hybrid Search (Structural + Semantic)

**Why:**
- Structural features (city, day, budget, party level) provide hard constraints
- Semantic embeddings capture nuanced similarity in vibes and descriptions
- Combining both gives better results than either alone

**Trade-offs:**
- Requires OpenAI API calls (cost + latency)
- Can fall back to structural-only if embeddings unavailable

### 2. Offline Preprocessing

**Why:**
- Embedding generation is expensive (time + API cost)
- Precompute once, use many times
- Enables fast query response (<100ms structural, <200ms with embeddings)

**Trade-offs:**
- New nights require re-running preprocessing
- Data freshness depends on pipeline schedule

### 3. Prompt Guardrails

**Why:**
- Prevent poor UX from overly broad or irrelevant prompts
- Guide users to refine queries instead of showing bad results
- Transparent feedback (status + reason)

**Guardrail Thresholds:**
- `no_match`: max semantic similarity < 0.6
- `too_broad`: >20% of nights have semantic similarity ≥ 0.8

### 4. Venue Aggregation

**Why:**
- Users care about venues (places), not individual nights
- Multiple nights at same venue reinforce recommendations
- Venue stats provide stable, reliable averages

**Aggregation:**
- Average similarity scores across all matching nights per venue
- Top-5 venues by average score

### 5. Stateless API

**Why:**
- Simplifies deployment (no session storage)
- Horizontal scaling (any instance can handle any request)
- Frontend manages user state (React)

**Trade-offs:**
- No saved searches or history (could add DB later)
- Each request re-computes everything

---

## Performance Characteristics

### Query Latency (approximate)

| Operation | Time | Notes |
|-----------|------|-------|
| Load data on startup | 2-5s | One-time cost |
| Structural similarity | 10-30ms | Pure NumPy |
| OpenAI embedding call | 100-300ms | Network + API |
| Total /search | 150-350ms | Dominated by embedding |
| Total /prompt-search | 300-600ms | +GPT prompt parsing |

### Data Size

| File | Rows | Size | Notes |
|------|------|------|-------|
| `serbia_nightlife_dataset.csv` | ~5000 | ~2MB | Raw nights |
| `venues.csv` | ~500 | ~100KB | Aggregated |
| `nights_features.jsonl` | ~5000 | ~200MB | With 768d embeddings |

### Scaling Considerations

- **Current:** In-memory data loading → supports ~10K nights comfortably
- **Future (100K+ nights):**
  - Use vector database (Pinecone, Weaviate, Qdrant)
  - Store embeddings in DB, load on-demand
  - Cache frequent queries (Redis)

---

## Security & Privacy

### API Keys
- `OPENAI_API_KEY` stored in `.env` (gitignored)
- Loaded via `load_dotenv()` on startup
- Never exposed to frontend

### CORS
- Currently: `allow_origins=["*"]` (hackathon mode)
- Production: Restrict to specific frontend domain

### Rate Limiting
- Not implemented (add with FastAPI middleware for production)
- OpenAI API has its own rate limits

### Data Privacy
- No PII collected in current design
- Future: user accounts would need proper auth (JWT, OAuth)

---

## Future Enhancements

### Backend
1. **Database Integration**
   - PostgreSQL for venues/nights
   - Vector DB for embeddings
   - User accounts & saved searches

2. **Advanced Features**
   - Collaborative filtering (user similarity)
   - Time-aware recommendations (real-time events)
   - Weather integration
   - Live crowd data (API from venues)

3. **Performance**
   - Redis caching for popular queries
   - Background workers for preprocessing
   - Async batch embedding generation

### Frontend
1. **Enhanced UX**
   - Map view of recommended venues
   - Calendar integration
   - Social sharing
   - Reviews & ratings

2. **Personalization**
   - User profiles & preferences
   - Search history
   - Favorite venues

### DevOps
1. **CI/CD**
   - Automated testing (pytest, Jest)
   - Docker containerization
   - GitHub Actions pipeline

2. **Monitoring**
   - Logging (structured logs)
   - Metrics (Prometheus + Grafana)
   - Error tracking (Sentry)

3. **Deployment**
   - Kubernetes orchestration
   - Auto-scaling
   - Blue-green deployments

---

## Development Workflow

### Setup
```bash
# Backend
cd backend
python -m venv ../.venv
& ..\.venv\Scripts\python.exe -m pip install -r requirements.txt
cp .env.example .env  # Add your OPENAI_API_KEY

# Frontend
cd front
npm install
```

### Data Pipeline
```bash
# Run once to generate data
cd backend
& ..\.venv\Scripts\python.exe scripts\build_venues.py
& ..\.venv\Scripts\python.exe scripts\preprocess_nights.py
```

### Run Development Servers
```bash
# Backend (Terminal 1)
cd backend
& ..\.venv\Scripts\python.exe run_server.py

# Frontend (Terminal 2)
cd front
npm run dev
```

### Testing
```bash
# Backend
& ..\.venv\Scripts\python.exe -m pytest tests/

# Frontend
npm test
```

---

## API Documentation

FastAPI provides auto-generated interactive docs:
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

---

## Conclusion

Night-Twin combines classical information retrieval (structured features, filtering) with modern AI (embeddings, LLM prompt parsing) to deliver an intelligent nightlife recommendation system. The architecture is designed for:

- **Developer Experience:** Fast local iteration, clear separation of concerns
- **User Experience:** Fast queries, transparent explanations, flexible input (structured or natural language)
- **Scalability:** Modular design ready for DB integration and horizontal scaling
- **Maintainability:** Clean code, type hints, comprehensive documentation

The hybrid search approach ensures robustness: even if OpenAI API is unavailable, the system falls back to structural similarity. The preprocessing pipeline keeps query latency low by doing expensive computations offline.

---

**Generated:** November 23, 2025  
**Version:** 1.0  
**Project:** Night-Twin - AI Nightlife Recommendation System
