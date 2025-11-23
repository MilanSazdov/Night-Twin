# **🌃 Night-Twin: Find the Doppelgänger of Nightlife Events** 🎯

## **📚 Table of Contents**

1. [Hackathon Challenge](#hackathon-challenge) 🏆
2. [Key Features](#key-features) ✨
3. [Project Overview](#project-overview) 📝
4. [Folder Structure](#folder-structure) 📂
5. [Features](#features) 🔑
6. [Getting Started](#getting-started) 🚀
    - [Prerequisites](#prerequisites) ⚡
    - [Clone Repository](#1-clone-repository) 📥
    - [Setup Backend (FastAPI + Embeddings)](#2-setup-backend-fastapi--embeddings) ⚙️
    - [Run Backend Server](#3-run-backend-server) 🖥️
    - [Run Frontend](#4-run-frontend) 🌐
7. [Technologies Used](#technologies-used) 🛠️
8. [Future Improvements](#future-improvements) 🚧
9. [Hackathon Context](#hackathon-context) 💡
10. [Authors](#authors) 👥

## **🏆 Hackathon Challenge:** Find the Doppelgänger - Open-ended AI Hunt  

This project was built for the “Find the Doppelgänger” hackathon. The goal is to design an AI system that can identify “doppelgängers” - highly similar items - in a domain of your choice. For our project, we focus on **nightlife hangouts in Serbia**, finding nights out that are most similar based on parameters like day, location, number of people, crowd density, alcohol level, weather, etc...  

---

## **✨ Key Features**

- **AI-Powered Similarity Search** 🔍  
  The system compares a user’s query (description, filters, or night-out context) with all nights in the dataset using vector embeddings. It returns the **most similar nights** based on embedding distance.

- **Post New Night-Outs** ➕  
  Users can submit new hangout entries from the frontend.  
  Each new night-out is processed, embedded, and appended to the dataset, allowing the system to continuously improve and grow.

- **Embeddings Generation** 🧠  
  Uses **OpenAI’s `text-embedding-3-small`** model to convert nights into numerical vectors for efficient similarity comparison.

---

## **📝 Project Overview**

The project consists of:

1. **Backend (Python + FastAPI)** 🖥️  
   - Loads and preprocesses nightlife data.  
   - Generates embeddings for nights using OpenAI’s `text-embedding-3-small` model.  
   - Computes similarity between a user query and the dataset.  
   - Exposes a **REST API** endpoint for frontend queries.

2. **Frontend (HTML/JS / React)** 🌐  
   - Simple form interface for users to input night descriptions.  
   - Sends query to backend via POST request.  
   - Displays the top **most similar nights** with venue info.

---

## **📂 Folder Structure**
```text
backend/
├── app/
│   ├── main.py              # FastAPI entrypoint
│   ├── search_engine.py     # OpenAI embeddings + similarity search
│   ├── database.py          # Loads dataset and precomputed embeddings
│   ├── models.py            # Pydantic models for API
│   └── .env                 # API keys and credentials
├── data/
│   ├── serbia_nightlife_dataset.csv
│   ├── venues.csv
│   ├── nights_with_venues.csv
│   ├── nights_features.jsonl
│   └── embeddings.pkl       # precomputed embeddings
├── scripts/
│   ├── preprocess_nights.py # Compute embeddings for dataset
│   └── build_venues.py      # Prepare venue and night data
└── README.md
frontend/
├── index.html
├── app.js
└── styles.css

```



---

## **🔑Features**

- **Similarity Search🔍**: Finds the top-K most similar nights by comparing query embeddings with precomputed night embeddings.  
- **Embeddings Generation🧠**: Uses **OpenAI embeddings** to represent nights as vectors.  
- **Frontend Integration**: Users interact with a simple form to query the AI system.  
- **Venue Info**: Returns venue details for each night.  
- **Configurable**: API keys, username, and password stored securely in `.env`.
---

## **🚀Getting started**

### **⚡Prerequisites**

 - Python 3.13 recommended

 - pip / virtualenv (or use poetry)

 - OpenAI API key (for embeddings)


### **📥1. Clone repository**
```bash
git clone "https://github.com/MilanSazdov/Night-Twin.git"
cd Night-Twin/backend
```

### **⚙️2. Setup backend (FastAPI + embeddings)**
Create and activate a Python virtual environment
```
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
# or
.venv\Scripts\activate      # Windows PowerShell
```

Install dependencies:
```
  pip install openai numpy pandas scikit-learn python-dotenv uvicorn

```

### **🖥️3. Run Backend Server**

Start the FastAPI server:

```
uvicorn app.main:app --reload
```

### **4. Run Frontend**

Navigate to the frontend folder:

```
cd ../frontend
```

Open index.html in your browser.

---

## **🛠️Technologies Used**

- **Python 3.13**  
- **FastAPI** for backend API  
- **OpenAI API** (`text-embedding-3-small` for embeddings, `gpt-4.1-mini` for text generation)  
- **Pandas & NumPy** for data processing  
- **Frontend**: HTML + JavaScript (React optional)  
- **.env** for secure environment variables  

---

## **🚧Future Improvements**

- Add **weighted features** to fine-tune similarity scoring.  
- Implement **real-time venue filtering** in frontend.  
- Expand dataset with **more cities, venues, and events**.  
- Improve **frontend UI** with sorting, visualization, and interactive maps.  
- Allow users to **save favorite nights** and track their own nightlife patterns.  

---

## **💡Hackathon Context**

This project is designed for the **“Find the Doppelgänger”** challenge.  
The system demonstrates:  

1. How AI can **represent complex real-world events as embeddings**.  
2. How a query can **retrieve the most similar items** (doppelgängers) from a dataset.  
3. How to **explain matches** to users by returning metadata like venue, people, alcohol, crowd density, and similarity score.  


## **👥Authors**

- **Nikola Nikolic**
- **Vedran Bajic**
- **Milan Sazdov**
- **Lazar Sazdov**

*Special thanks to the hackathon mentors and organizers for guidance and support.*