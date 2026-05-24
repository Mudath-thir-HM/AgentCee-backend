# Astra AI — Backend

A FastAPI + async Python backend powering the Astra AI social media management platform. Handles authentication, AI content generation, post scheduling, inbox management, analytics, and keyword/mention tracking — all backed by Supabase (PostgreSQL).

---

## Tech Stack

| Layer       | Library                                       |
| ----------- | --------------------------------------------- |
| Framework   | FastAPI                                       |
| Language    | Python 3.11+                                  |
| Database    | Supabase (PostgreSQL via asyncpg)             |
| Auth        | JWT (python-jose) + bcrypt (passlib)          |
| AI          | OpenRouter API (DeepSeek, Gemma, Llama, Qwen) |
| Validation  | Pydantic v2                                   |
| HTTP client | httpx (async)                                 |
| Config      | pydantic-settings                             |

---

## Prerequisites

- Python 3.11+
- A Supabase project (free tier works)
- An OpenRouter API key (free tier available at openrouter.ai)

---

## Getting Started

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy the example env file and fill in your values
cp .env.example .env

# Run database migrations (in Supabase SQL editor or psql)
# Run supabase/migrations/001_initial.sql first, then 002_scheduler_analytics.sql

# Start the development server
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

---

## Environment Variables

Create a `.env` file in the project root with the following:

```env
# App
PROJECT_NAME=Astra AI
API_VERSION=1.0.0

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-supabase-jwt-secret
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres

# Auth
JWT_SECRET=your-long-random-secret-string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080   # 7 days

# AI
OPENROUTER_API_KEY=sk-or-your-key
DEEPSEEK_MODEL=deepseek/deepseek-chat
GEMMA_MODEL=google/gemma-3-27b-it:free
FLUX_MODEL=black-forest-labs/flux-1-schnell:free

# CORS
FRONTEND_URL=http://localhost:5173
```

---

## Project Structure

```
app/
├── main.py                  # FastAPI app, middleware, route registration
├── core/
│   ├── config.py            # pydantic-settings — all env vars
│   ├── security.py          # JWT creation
│   ├── auth.py              # JWT decoding (legacy)
│   ├── cors.py              # CORS middleware setup
│   └── password.py          # bcrypt hash/verify
├── db/
│   ├── connection.py        # asyncpg connection pool
│   └── sql.py               # fetch_one / fetch_all / execute helpers
├── middlewares/
│   ├── auth.py              # get_current_user dependency (JWT extraction)
│   └── rate_limit.py        # Sliding-window per-IP rate limiter
├── routes/v1/               # HTTP endpoint definitions
│   ├── health.py
│   ├── auth.py
│   ├── profile.py
│   ├── onboarding.py
│   ├── social.py
│   ├── messages.py
│   ├── content.py
│   ├── scheduler.py
│   ├── analytics.py
│   └── tracking.py
├── controllers/             # Request orchestration
├── services/                # Business logic + agent calls
├── repositories/            # Raw SQL — one file per domain
├── schemas/                 # Pydantic request/response models
├── agents/                  # LLM-powered components
│   ├── content_agent.py     # Social media copy generation
│   ├── inbox_agent.py       # Reply suggestions + sentiment
│   ├── response_agent.py    # Auto-reply generation
│   ├── analytics_agent.py   # Performance insights
│   └── tracking_agent.py    # Routes events to tracking rules
├── utils/
│   ├── openrouter.py        # OpenRouter client with model fallback chain
│   ├── prompts.py           # Prompt templates
│   └── logger.py            # Structured logging
└── workers/
    ├── scheduler_worker.py  # Publishes due posts (runs every 60s)
    ├── analytics_worker.py  # Fetches platform metrics (runs every 1h)
    └── tracking_worker.py   # Processes incoming social events
```

---

## Architecture

The backend follows a strict four-layer pattern:

```
Request → Route → Controller → Service → Repository → Database
                                    ↕
                                  Agent
                                    ↕
                               OpenRouter
```

Each layer has a single responsibility:

- **Routes** — Define HTTP methods, paths, and query parameters. Delegate immediately to controllers.
- **Controllers** — Orchestrate calls between services. Handle response formatting.
- **Services** — Implement business logic. Call agents for AI operations. Own error handling.
- **Repositories** — Execute parameterized SQL queries. Return raw asyncpg records.

Agents are called from within services, not from controllers or routes. This means AI calls can be wrapped in try/except with graceful fallbacks without leaking into the HTTP layer.

---

## Authentication

All protected endpoints use the `get_current_user` FastAPI dependency:

```python
@router.get("/me")
async def get_me(user_id: str = Depends(get_current_user)):
    ...
```

The dependency extracts the `Authorization: Bearer <token>` header, decodes the JWT using `JWT_SECRET`, and returns the `sub` claim (user UUID). A missing or invalid token raises `HTTP 401`.

Passwords are hashed with bcrypt via passlib. The `password_hash` field is stored in the `profiles` table and is never returned in API responses.

**Token lifetime** is controlled by `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 10080 = 7 days). There is no refresh token endpoint — expiry requires re-authentication.

---

## AI Integration

### OpenRouter Client (`app/utils/openrouter.py`)

All LLM calls go through `ask_openrouter()`, which implements a model waterfall:

```
DeepSeek → Gemma → Llama 3.3 70B → Qwen3 32B
```

If a model returns a non-200 response or raises an exception, the next model in the chain is tried. This provides resilience against free-tier rate limits without requiring manual intervention.

### Agents

| Agent            | Endpoint(s)                  | Fallback behavior                                                         |
| ---------------- | ---------------------------- | ------------------------------------------------------------------------- |
| `ContentAgent`   | `POST /content/generate`     | Returns placeholder text if all models fail                               |
| `InboxAgent`     | `POST /messages/ai-suggest`  | Returns 3 generic reply suggestions                                       |
| `ResponseAgent`  | `POST /messages/auto-reply`  | Returns a hardcoded polite acknowledgement                                |
| `AnalyticsAgent` | `GET /analytics/suggestions` | Returns rule-based suggestions (engagement rate thresholds, top platform) |
| `TrackingAgent`  | `POST /tracking/events`      | Always stores the event; rule matching is best-effort                     |

The analytics service also returns mock data when the `post_analytics` table has no records for a user. This ensures the dashboard is populated on first load without requiring a full publishing pipeline to be operational.

---

## API Endpoints

### Auth

| Method | Path                    | Description                 |
| ------ | ----------------------- | --------------------------- |
| POST   | `/api/v1/auth/register` | Create account, returns JWT |
| POST   | `/api/v1/auth/login`    | Authenticate, returns JWT   |

### Profile

| Method | Path         | Description                       |
| ------ | ------------ | --------------------------------- |
| GET    | `/api/v1/me` | Get authenticated user profile    |
| PATCH  | `/api/v1/me` | Update company name or avatar URL |

### Onboarding

| Method | Path                           | Description               |
| ------ | ------------------------------ | ------------------------- |
| POST   | `/api/v1/onboarding/connect`   | Connect a social platform |
| GET    | `/api/v1/onboarding/platforms` | List connected platforms  |

### Social Accounts

| Method | Path                          | Description                         |
| ------ | ----------------------------- | ----------------------------------- |
| POST   | `/api/v1/social/connect`      | Register social account credentials |
| GET    | `/api/v1/social/accounts`     | List connected accounts             |
| DELETE | `/api/v1/social/{account_id}` | Disconnect an account               |

### Messages

| Method | Path                          | Description                          |
| ------ | ----------------------------- | ------------------------------------ |
| GET    | `/api/v1/messages/`           | Fetch all messages                   |
| POST   | `/api/v1/messages/receive`    | Ingest message from webhook          |
| POST   | `/api/v1/messages/reply`      | Mark message as replied              |
| POST   | `/api/v1/messages/ai-suggest` | Get AI reply suggestions + sentiment |
| POST   | `/api/v1/messages/auto-reply` | Generate single auto-reply           |

### Content

| Method | Path                          | Description                   |
| ------ | ----------------------------- | ----------------------------- |
| POST   | `/api/v1/content/generate`    | Generate AI content (60-120s) |
| GET    | `/api/v1/content/history`     | Paginated content history     |
| GET    | `/api/v1/content/{id}`        | Fetch single content item     |
| PATCH  | `/api/v1/content/{id}`        | Edit text, hashtags, CTA      |
| PATCH  | `/api/v1/content/{id}/status` | Update status                 |
| DELETE | `/api/v1/content/{id}`        | Delete content                |

### Scheduler

| Method | Path                     | Description          |
| ------ | ------------------------ | -------------------- |
| POST   | `/api/v1/scheduler/`     | Schedule a post      |
| GET    | `/api/v1/scheduler/`     | List scheduled posts |
| GET    | `/api/v1/scheduler/{id}` | Fetch single post    |
| PATCH  | `/api/v1/scheduler/{id}` | Reschedule or cancel |
| DELETE | `/api/v1/scheduler/{id}` | Delete pending post  |

### Analytics

| Method | Path                                  | Description                    |
| ------ | ------------------------------------- | ------------------------------ |
| POST   | `/api/v1/analytics/record`            | Ingest analytics (webhook)     |
| GET    | `/api/v1/analytics/overview`          | Aggregated stats               |
| GET    | `/api/v1/analytics/weekly-engagement` | Daily engagement (last 7 days) |
| GET    | `/api/v1/analytics/platforms`         | Per-platform breakdown         |
| GET    | `/api/v1/analytics/top-posts`         | Top posts by engagement        |
| GET    | `/api/v1/analytics/suggestions`       | AI-generated insights          |

### Tracking

| Method | Path                                | Description                            |
| ------ | ----------------------------------- | -------------------------------------- |
| POST   | `/api/v1/tracking/rules`            | Create hashtag/mention/keyword rule    |
| GET    | `/api/v1/tracking/rules`            | List rules                             |
| PATCH  | `/api/v1/tracking/rules/{id}`       | Toggle rule active state               |
| DELETE | `/api/v1/tracking/rules/{id}`       | Delete rule                            |
| POST   | `/api/v1/tracking/events`           | Ingest tracked event (webhook)         |
| GET    | `/api/v1/tracking/events`           | List tracked events                    |
| PATCH  | `/api/v1/tracking/events/{id}/read` | Mark event read                        |
| POST   | `/api/v1/tracking/events/read-all`  | Mark all events read                   |
| POST   | `/api/v1/tracking/suggest-reply`    | AI reply suggestions for tracked event |

---

## Database Schema

All tables reference `profiles(id)` as a foreign key with `ON DELETE CASCADE`. Row Level Security is enabled on all tables in Supabase.

### Core Tables

| Table              | Purpose                                                                 |
| ------------------ | ----------------------------------------------------------------------- |
| `profiles`         | User accounts (email, password_hash, company_name, connected_platforms) |
| `social_accounts`  | Connected platform accounts (platform, account_name, account_id)        |
| `messages`         | Incoming DMs and comments from platforms                                |
| `generated_assets` | AI-generated content (generated_text, hashtags, call_to_action, status) |
| `scheduled_posts`  | Posts queued for future publishing                                      |
| `post_analytics`   | Engagement metrics per post                                             |
| `tracking_rules`   | Hashtag/mention/keyword monitoring rules                                |
| `tracked_events`   | Events matching tracking rules                                          |

Run migrations in order:

1. `supabase/migrations/001_initial.sql`
2. `supabase/migrations/002_scheduler_analytics.sql`

---

## Background Workers

Workers are standalone Python scripts that connect to the database and run on a loop. Run them in separate processes or integrate with a task scheduler (APScheduler, Celery, cron).

```bash
# Publishes due scheduled posts every 60 seconds
python -m app.workers.scheduler_worker

# Fetches platform analytics every hour
python -m app.workers.analytics_worker

# Processes incoming social events
python -m app.workers.tracking_worker
```

**Scheduler worker** — Queries `scheduled_posts` for rows where `status = 'pending'` and `scheduled_for <= NOW()`. Calls the platform publishing stubs (currently mock), then marks posts as `published` or `failed`.

**Analytics worker** — Queries recently published posts and calls platform analytics stubs (currently returning randomized mock data). Records results in `post_analytics`.

**Tracking worker** — Maintains an asyncio queue and consumer. Platform polling stubs are ready to be replaced with real webhook handlers or streaming API clients.

---

## Rate Limiting

`RateLimitMiddleware` applies a sliding-window rate limit of 60 requests per 60 seconds per IP address. Requests exceeding the limit receive a `429 Too Many Requests` response.

The limiter uses an in-process dictionary (`collections.defaultdict`). For multi-worker deployments (Gunicorn with multiple workers), replace this with a Redis-backed implementation so limits are shared across processes.

---

## Error Handling

A global `exception_handler` catches any unhandled exceptions and returns a generic `500 Internal Server Error` JSON response, preventing stack traces from leaking to clients.

Service-layer errors raise `HTTPException` with specific status codes:

- `400` — Business logic violation (e.g. platform already connected)
- `401` — Authentication failure
- `404` — Resource not found or ownership check failed
- `409` — State conflict (e.g. attempting to edit a published post)
- `422` — Schema validation failure (handled automatically by Pydantic)
- `429` — Rate limit exceeded

---

## Adding a New Endpoint

1. **Schema** — Add a Pydantic model to `app/schemas/`.
2. **Repository** — Add SQL query methods to the relevant repository in `app/repositories/`.
3. **Service** — Add business logic to `app/services/`. Call the repository. Wrap any agent calls in try/except.
4. **Controller** — Add a method to `app/controllers/` that calls the service.
5. **Route** — Add the endpoint to `app/routes/v1/` with the appropriate HTTP method, path, and `Depends(get_current_user)`.

---

## Known Limitations

- **No OAuth for platform publishing.** The scheduler worker has stubs for Instagram, Facebook, X, LinkedIn, and TikTok publishing. Real publishing requires OAuth 2.0 access tokens stored per `social_accounts` row.
- **In-process rate limiting.** The rate limiter does not survive process restarts and is not shared across multiple workers. Use Redis for production deployments.
- **No token refresh.** There is a single access token with a configurable expiry. A refresh token endpoint would prevent unnecessary re-authentication.
- **Synchronous OpenRouter calls.** Content generation blocks the request for the duration of the LLM call (up to 120s). For better throughput under load, move generation to a background task and poll for results.
