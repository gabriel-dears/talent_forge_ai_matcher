# Talent Forge AI Matcher

Talent Forge AI Matcher is a FastAPI-based microservice that uses AI to intelligently match candidates to job opportunities. It leverages natural language embeddings to analyze candidate skills, experience, and resume content, then compares them against job descriptions using semantic similarity and experience scoring.

This service is designed to be part of the [Talent Forge](https://github.com/gabriel-dears/talent_forge) platform and integrates seamlessly with its Spring Boot backend API.

---

## 🔍 Features

- ✅ Match a candidate to the most relevant jobs
- ✅ Match a job to the most relevant candidates
- ✅ AI-powered semantic scoring using `sentence-transformers`
- ✅ Scikit-learn-based cosine similarity
- ✅ RESTful FastAPI interface
- ✅ Containerized with Docker for easy deployment

---

## 📦 Requirements

- Python 3.9+
- Docker (optional, for containerized runs)

Install dependencies (if running locally):

```bash
pip install -r requirements.txt
```

## 🚀 Running the App

### Option 1: Docker (Recommended)

Make sure the Spring Boot backend is running and accessible (or use docker-compose to start both services together).

```bash
docker build -t talent-forge-ai-matcher .
docker run -p 8000:8000 \
  -e SPRING_API_URL=http://host.docker.internal:8080/api/v1 \
  talent-forge-ai-matcher
```
Replace host.docker.internal with app if you're using Docker Compose and the backend is a service named app.

### Option 2: Locally with uvicorn

Start the app locally (requires Python environment):

```bash
export SPRING_API_URL=http://localhost:8080/api/v1
uvicorn main:app --reload
```

---

## 🔗 API Endpoints

| Method | Endpoint                          | Description                                  |
| ------ | --------------------------------- | -------------------------------------------- |
| `GET`  | `/match/candidate/{candidate_id}` | Returns a ranked list of matching jobs       |
| `GET`  | `/match/job/{job_id}`             | Returns a ranked list of matching candidates |

### 📘 Example
```bash
curl http://localhost:8000/match/candidate/123
```

Response:

```json
[
  {
    "jobId": "job-456",
    "jobTitle": "Senior Java Developer",
    "matchScore": 0.8721
  }
]
```

---

## 🧠 How It Works

The matching algorithm uses:

Semantic Embeddings: via all-MiniLM-L6-v2 model from sentence-transformers

Cosine Similarity: to compute textual similarity

Experience Adjustment: penalizes or boosts candidates based on whether they meet job experience requirements

Score formula:

```bash
final_score = 0.8 * semantic_similarity + 0.2 * experience_factor
```

---

## 📁 Project Structure

```bash
.
├── main.py             # FastAPI endpoints
├── matcher.py          # Matching logic and AI scoring
├── models.py           # Pydantic data models
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 🐳 Docker Support

Build image

```bash
docker build -t talent-forge-ai-matcher .
Run with environment variable
bash
Copy
Edit
docker run -p 8000:8000 \
  -e SPRING_API_URL=http://app:8080/api/v1 \
  talent-forge-ai-matcher
```

---

## 🧪 Development

Start with debug support (if needed):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
Use debugpy for attaching a debugger.
```
---

## 🔒 Environment Variables

Variable	Default	Description
SPRING_API_URL	http://localhost:8080/api/v1	URL of the Spring Boot Talent Forge backend

---

## ✨ Contributors

Gabriel Soares – @gabriel-dears

---

## 🤝 Integration with Talent Forge

This service is intended to be deployed alongside:

talent_forge – the core Spring Boot API

Use docker-compose in the parent repo to spin up the full system.

---

## 🤝 Integration with Talent Forge

This service is intended to be deployed alongside:

talent_forge – the core Spring Boot API

Use docker-compose in the parent repo to spin up the full system.

