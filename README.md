# Content Moderation Platform

A full-stack content moderation system that accepts user text, classifies it as toxic or safe, explains why toxic content was flagged, and sends flagged content to a human review queue.

## Features

- Text moderation API with toxicity score, labels, severity, and explanation
- Human review queue for flagged content
- Approve/reject workflow for moderators
- Moderation statistics dashboard
- React frontend, FastAPI backend, FastAPI AI service, and MongoDB
- Docker Compose setup for local evaluation

## Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | React, Vite |
| Backend API | FastAPI, Motor, MongoDB |
| AI Service | FastAPI, PyTorch Lightning, Transformers, Captum |
| Model | RoBERTa-based toxic comment classifier |
| Database | MongoDB |
| Containerization | Docker, Docker Compose |

## Dataset

The model was trained and tested using toxic-comment data from the Jigsaw Toxic Comment Classification dataset:

https://www.kaggle.com/datasets/julian3833/jigsaw-toxic-comment-classification-challenge

For assignment evaluation, use 5000 samples for testing. The current implementation uses a RoBERTa-based classifier with these labels:

- toxic
- severe_toxic
- obscene
- threat
- insult
- identity_attack

## Project Structure

```text
content-moderation-platform/
  ai-service/       FastAPI ML inference and explainability service
  backend/          FastAPI API, MongoDB persistence, review queue
  frontend/         React + Vite moderation console
  docker-compose.yml
  start-services.ps1
  README.md
```

## Environment Setup

No secrets are committed. Copy the example environment files before running locally:

```powershell
Copy-Item backend\.env.example backend\.env
Copy-Item ai-service\.env.example ai-service\.env
```

Backend example:

```env
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=content_moderation_db
AI_SERVICE_URL=http://127.0.0.1:8000
PORT=8001
```

AI service example:

```env
MODEL_PATH=app/models/best_model_v2.ckpt
MODEL_NAME=roberta-base
MAX_LEN=128
```

## Run With Docker

Use one command from the repository root:

```powershell
docker-compose up --build
```

Services:

| Service | URL |
| --- | --- |
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8001 |
| AI Service | http://localhost:8000 |
| MongoDB | Internal Docker network as `mongo:27017` |

The first AI service startup can take a few minutes because Python ML dependencies are installed and the RoBERTa checkpoint is loaded.

## Run Manually

Start MongoDB locally first.

AI service:

```powershell
cd ai-service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

There is also a local PowerShell launcher:

```powershell
.\start-services.ps1
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/moderate` | Creates a moderation request, stores it as `PROCESSING`, then runs AI analysis in the background |
| POST | `/api/moderate/sync` | Runs moderation synchronously and returns the completed result |
| GET | `/api/moderate/{id}` | Gets one moderation record by id |
| GET | `/api/queue` | Lists items waiting for human review |
| POST | `/api/queue/{id}/decide` | Submits a human decision: `APPROVED` or `REJECTED` |
| GET | `/api/stats` | Returns moderation statistics |

Example request:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8001/api/moderate `
  -ContentType "application/json" `
  -Body '{"text":"You are awful and I hate you"}'
```

Example decision:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8001/api/queue/<moderation_id>/decide `
  -ContentType "application/json" `
  -Body '{"decision":"APPROVED"}'
```

## Demo Sample Inputs

Use these examples in the frontend to show the full flow:

| Text | Expected Flow |
| --- | --- |
| `Thanks for helping me today, I appreciate it.` | Safe, approved automatically |
| `You are disgusting and useless.` | Toxic, sent to review queue |
| `I will find you and hurt you.` | Toxic threat, sent to review queue |
| `This quoted message says "you are awful", but I am reporting it.` | Ambiguous; should be reviewed carefully |

## Architecture Diagram

```mermaid
flowchart TB

    %% ===== USER FLOW =====

    User["👤 User / Moderator"]

    Frontend["🎨 React + Vite Frontend"]

    Backend["⚙️ FastAPI Backend"]

    Mongo[("🗄️ MongoDB")]

    AI["🧠 FastAPI AI Service"]

    Model["🤖 RoBERTa Toxic Classifier"]

    Explain["📊 Captum Explainability"]

    Queue["🛡️ Human Review Queue"]

    %% ===== FLOW =====

    User -->|Submit Text| Frontend

    Frontend -->|API Request| Backend

    Backend -->|Store Data| Mongo

    Backend -->|Moderation Request| AI

    AI -->|Toxicity Detection| Model

    AI -->|Generate Explanation| Explain

    AI -->|Moderation Result| Backend

    Backend -->|Send Response| Frontend

    Backend -. "Flagged Content" .-> Queue

    Queue -->|Display Review Items| Frontend

    Frontend -. "Approve / Reject" .-> Backend

    %% ===== COLORS =====

    classDef frontend fill:#E8F5E9,stroke:#43A047,color:#000;
    classDef backend fill:#FFF3E0,stroke:#FB8C00,color:#000;
    classDef ai fill:#F3E5F5,stroke:#8E24AA,color:#000;
    classDef db fill:#ECEFF1,stroke:#546E7A,color:#000;
    classDef queue fill:#FFEBEE,stroke:#E53935,color:#000;
    classDef user fill:#E3F2FD,stroke:#1E88E5,color:#000;

    class User user;
    class Frontend frontend;
    class Backend backend;
    class AI ai;
    class Mongo db;
    class Queue queue;
```

## Data Flow

1. The user enters text in the frontend.
2. The frontend sends `POST /api/moderate` to the backend.
3. The backend stores the request in MongoDB with status `PROCESSING`.
4. The backend calls the AI service in the background.
5. The AI service tokenizes the text, runs the RoBERTa classifier, computes label scores, and uses Captum Integrated Gradients for explanations when content is toxic.
6. The backend updates MongoDB with the final result.
7. Safe content becomes `APPROVED`; toxic content becomes `PENDING_REVIEW`.
8. The review queue lets a human approve or reject flagged content.

## Part 2: Understanding Questions

### 1. How does the system decide if content is toxic?

The AI service uses a RoBERTa-based multi-label classifier. It tokenizes the submitted text, runs it through the model, applies sigmoid probabilities for each toxicity label, and treats the main `toxic` score as the primary decision score. If the toxic score is greater than `0.5`, the content is marked toxic. The service also returns per-label scores, triggered labels, severity, top contributing words, toxic phrases, and a plain-English reason.

### 2. Which is worse: flagging safe content or missing toxic content?

For a moderation system, missing toxic content is usually worse because harmful content can reach users and damage trust, safety, and legal compliance. However, false positives are also serious because they can unfairly silence users. This project handles that tradeoff by sending flagged items to human review instead of permanently rejecting them automatically.

### 3. How do you handle sarcasm, quoted content, and non-English?

Sarcasm is difficult because the literal words can be safe while the intent is harmful, or the reverse. The model score should be treated as a signal, not a final judgment, especially for ambiguous cases.

Quoted content should be handled with context. A user reporting abuse may quote toxic language without endorsing it. The safest product behavior is to keep the item explainable and route uncertain or high-risk content to human review.

Non-English content requires either a multilingual moderation model, language detection plus language-specific models, or translation before moderation. A model trained mainly on English should not be trusted as the only decision-maker for non-English text.

### 4. How might bad actors evade detection?

Bad actors may use misspellings, spacing, symbols, homoglyphs, coded language, emojis, screenshots of text, sarcasm, indirect threats, or language switching. They may also test the system repeatedly to learn the threshold. Defenses include text normalization, multilingual models, image OCR for screenshots, rate limiting, adversarial test sets, human review, and regular retraining with newly observed abuse patterns.

### 5. Give 2 examples where AI-generated code had security issues.

One example is AI-generated backend code that builds database queries directly from user input, causing SQL injection or NoSQL injection risk. The fix is to use parameterized queries, validation, and least-privilege database users.

Another example is AI-generated authentication code that disables JWT verification, hard-codes secrets, logs tokens, or accepts unsigned tokens for convenience during testing. The fix is to require verified signatures, use environment-managed secrets, avoid logging sensitive values, and add authentication tests.

## Explainability

For toxic content, the AI service uses Captum Integrated Gradients to identify influential tokens. The response includes:

- `labels`: probability for each toxicity category
- `triggered_labels`: labels above the threshold
- `top_words`: words that contributed most to the toxic prediction
- `toxic_phrases`: short phrases built from high-impact words
- `reason`: human-readable explanation
- `severity`: `SAFE`, `LOW`, `MEDIUM`, or `HIGH`

Safe content skips the slower Captum step and returns `Safe content detected.`

## How It Works

1. The AI service tokenizes the submitted text with the RoBERTa tokenizer.
2. The classifier returns sigmoid probabilities for the toxicity labels.
3. If the text is safe, the service skips attribution and returns `Safe content detected.`
4. If the text is toxic, Captum `LayerIntegratedGradients` computes token-level attributions against the RoBERTa embedding layer.
5. RoBERTa subword tokens are merged back into readable words.
6. Stopwords and very short tokens are filtered out.
7. The highest-attribution words become `top_words`.
8. Short phrase pairs are built from important words and returned as `toxic_phrases`.
9. A human-readable `reason` is generated from triggered labels such as `threat`, `insult`, `obscene`, and `identity_attack`.

## Why This Helps

The explanation lets a human reviewer see which words or phrases most influenced the toxic decision. This is useful for:

- Debugging false positives
- Reviewing ambiguous moderation decisions
- Explaining why content entered the human review queue
- Checking whether the model focused on actually harmful words instead of harmless sentence structure

## Bug Fix Documentation

### Bug 1: `/api/moderate/sync` used `now` before assignment

Why it was wrong:

The synchronous moderation path created `created_at` and `updated_at` fields with a `now` variable that did not exist in that function. Calling `POST /api/moderate/sync` would raise a `NameError` after the AI service returned.

Corrected code:

```python
async def moderate_sync(self, text: str):
    # Create timestamps inside this function before using them in the document.
    now = datetime.utcnow()

    ai_result = await ai_service.moderate_text(text)

    moderation_data = {
        "text": ai_result["text"],
        "is_toxic": ai_result["is_toxic"],
        "confidence": ai_result["confidence"],
        "labels": ai_result["labels"],
        "triggered_labels": ai_result["triggered_labels"],
        "reason": ai_result["reason"],
        "severity": ai_result["severity"],
        "status": "PENDING_REVIEW" if ai_result["is_toxic"] else "APPROVED",
        "created_at": now,
        "updated_at": now,
        "error": None,
    }
```

Additional test case:

- Send `POST /api/moderate/sync` with safe text and verify the response has `created_at`, `updated_at`, and no server error.
- Send `POST /api/moderate/sync` with toxic text and verify the status becomes `PENDING_REVIEW`.

### Bug 2: Frontend default API URL pointed to the wrong backend port

Why it was wrong:

The backend Dockerfile and Docker Compose expose the backend on `8001`, but the frontend default URL used `http://127.0.0.1:5000`. A fresh frontend load would fail API calls unless the evaluator manually changed the backend URL.

Corrected code:

```javascript
// Match the backend port used by Docker Compose and the local launcher.
const DEFAULT_API_BASE = "http://127.0.0.1:8001";
```

Additional test case:

- Start with `docker-compose up --build`, open `http://127.0.0.1:5173`, submit text, and verify the frontend reaches the backend without manual URL changes.


### Bug 3: V1 model falsely flagged safe compliments as toxic

Why it was wrong:

The first model version fine-tuned `roberta-base` on 5,000 Jigsaw Toxic Comment samples with a balanced split of 2,500 toxic and 2,500 clean examples. It achieved a strong validation AUC of `0.956`, but testing revealed a serious real-world failure: safe compliment sentences such as `you are a pure gentleman` and `you are a nice guy` were being classified as toxic.

The root cause was dataset and pattern overfitting. In the V1 training data, the phrase shape `you are a ___` appeared mostly in toxic examples, so the model learned that sentence structure as a shortcut instead of learning the actual meaning of the compliment word. This made the model look good on aggregate metrics while failing important edge cases.

Corrected approach:

```python
# V2 training changes
training_samples = 15000              # 5k toxic + 10k clean
synthetic_compliments = 80            # "you are a [compliment]" safe examples
frozen_roberta_layers = 6             # reduce catastrophic forgetting
label_smoothing = True                # reduce overconfident predictions
threshold = best_f1_threshold         # selected using validation sweep

# Final score uses the fine-tuned model with Detoxify as a stability anchor.
final_toxicity_score = (
    0.40 * finetuned_roberta_score
    + 0.60 * detoxify_score
)
```

What changed in V2:

- Increased training data from 5,000 to 15,000 samples.
- Used a more realistic `1:2` toxic-to-clean ratio with 5k toxic and 10k clean examples.
- Added 80 synthetic compliment examples so the model learns that `you are a [compliment]` can be safe.
- Froze the bottom 6 RoBERTa layers to reduce catastrophic forgetting.
- Added label smoothing to avoid overconfident decisions.
- Replaced the fixed `0.5` cutoff with a validation-swept threshold optimized for F1.
- Used an ensemble: 40% fine-tuned RoBERTa and 60% pretrained Detoxify.

```

Infrastructure note:

- Training ran on Google Colab with a T4 GPU, taking about 25 minutes per run.
- Data was loaded through Kaggle API secrets, so no manual dataset upload was required.
- The model checkpoint was downloaded to the laptop at about 500 MB.
- The V2 model is ready to connect to FastAPI through the `ContentModeratorV2` class.

Additional test cases:

- Verify `you are a pure gentleman` is classified as safe.
- Verify `you are a nice guy` is classified as safe.
- Verify direct insults such as `you are an idiot` remain toxic.
- Verify the explanation highlights actually harmful words instead of harmless sentence structure.




