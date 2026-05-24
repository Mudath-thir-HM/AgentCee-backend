# Backend Architecture & Data Flow Documentation

**Target Audience:** Senior Backend Developers  
**Framework:** FastAPI + Async Python  
**Database:** Supabase (PostgreSQL)  
**Last Updated:** May 24, 2026

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Request/Response Flow](#requestresponse-flow)
3. [Layered Architecture](#layered-architecture)
4. [Database Schema](#database-schema)
5. [Authentication & Authorization](#authentication--authorization)
6. [AI Integration Points](#ai-integration-points)
7. [Async/Concurrency Patterns](#asyncconcurrency-patterns)
8. [Error Handling](#error-handling)
9. [Deployment & Configuration](#deployment--configuration)

---

## Architecture Overview

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React + Redux)                  │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Auth UI    │  │  Content UI  │  │ Analytics UI │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                    HTTP/REST (RTK Query)
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                        FastAPI Application                       │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Routes Layer (v1/*)                                     │   │
│  │ - /auth, /profile, /messages, /content, etc.           │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                            │                                     │
│  ┌─────────────────────────▼───────────────────────────────┐   │
│  │ Controllers Layer                                        │   │
│  │ - Orchestrates request validation & service calls       │   │
│  │ - Handles business logic coordination                   │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                            │                                     │
│  ┌─────────────────────────▼───────────────────────────────┐   │
│  │ Services Layer                                           │   │
│  │ - ContentService, AuthService, MessageService, etc.     │   │
│  │ - Core business logic                                   │   │
│  │ - Calls repositories for data access                    │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                            │                                     │
│  ┌─────────────────────────▼───────────────────────────────┐   │
│  │ Repositories Layer                                       │   │
│  │ - Data access abstraction                               │   │
│  │ - Raw SQL queries via asyncpg                           │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                            │                                     │
└───────────────────────────┼─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌──────────────┐  ┌──────────────┐
│   Supabase    │  │  OpenRouter  │  │  Webhooks    │
│  (PostgreSQL) │  │  (LLM APIs)  │  │  (Platforms) │
└───────────────┘  └──────────────┘  └──────────────┘

                    ▲                   ▲
                    │                   │
                    └───────────────────┘
                  External Integrations
```

---

## Request/Response Flow

### Example: POST `/api/v1/content/generate`

```
1. CLIENT REQUEST
   ┌────────────────────────────────────────┐
   │ POST /api/v1/content/generate          │
   │ Authorization: Bearer {jwt_token}      │
   │ Content-Type: application/json         │
   │                                        │
   │ Body: {                                │
   │   platform: "instagram",               │
   │   content_type: "post",                │
   │   prompt: "Write about AI marketing",  │
   │   tone: "professional"                 │
   │ }                                      │
   └────────────────────────────────────────┘
                    │
                    ▼

2. ROUTE HANDLER (app/routes/v1/content.py)
   ┌────────────────────────────────────────┐
   │ @router.post("/generate")              │
   │ async def generate_content(            │
   │   body: GenerateContentSchema,         │
   │   user_id: str = Depends(...)          │
   │ ):                                     │
   │   return await controller.generate()   │
   └────────────────────────────────────────┘

   Steps:
   • Pydantic validates request body against schema
   • Middleware extracts and validates JWT token
   • Dependency injection provides authenticated user_id
                    │
                    ▼

3. CONTROLLER (app/controllers/content_controller.py)
   ┌────────────────────────────────────────┐
   │ async def generate_content(            │
   │   user_id: str,                        │
   │   body: GenerateContentSchema          │
   │ ):                                     │
   │   return await content_service.        │
   │     generate(user_id, body)            │
   └────────────────────────────────────────┘

   Responsibilities:
   • Request validation (already done by Pydantic)
   • Coordinate between services
   • Format response for HTTP client
                    │
                    ▼

4. SERVICE LAYER (app/services/content_service.py)
   ┌────────────────────────────────────────┐
   │ async def generate(user_id, body):     │
   │   # Check rate limits                  │
   │   await check_rate_limit(user_id)      │
   │                                        │
   │   # Call AI service (OpenRouter)       │
   │   content = await openrouter.generate( │
   │     prompt=body.prompt,                │
   │     tone=body.tone                     │
   │   )                                    │
   │                                        │
   │   # Store in database                  │
   │   result = await repo.create_content({ │
   │     user_id: user_id,                  │
   │     platform: body.platform,           │
   │     generated_text: content,           │
   │     status: 'draft'                    │
   │   })                                   │
   │                                        │
   │   return result                        │
   └────────────────────────────────────────┘

   Key Logic:
   • Business rules enforcement
   • AI service orchestration
   • Data enrichment (hashtag extraction, CTA)
   • Error handling & retries
                    │
                    ▼

5. REPOSITORY LAYER (app/repositories/content_repository.py)
   ┌────────────────────────────────────────┐
   │ async def create_content(data):        │
   │   query = """                          │
   │     INSERT INTO content (              │
   │       user_id, platform, generated_text│
   │     ) VALUES ($1, $2, $3)              │
   │     RETURNING *                        │
   │   """                                  │
   │                                        │
   │   async with db.pool.acquire() as conn:│
   │     row = await conn.fetchrow(         │
   │       query,                           │
   │       data['user_id'],                 │
   │       data['platform'],                │
   │       data['generated_text']           │
   │     )                                  │
   │   return dict(row)                     │
   └────────────────────────────────────────┘

   Abstraction:
   • Raw SQL execution (asyncpg)
   • Connection pooling
   • Row-to-dict conversion
   • Transactional semantics
                    │
                    ▼

6. DATABASE (Supabase PostgreSQL)
   ┌────────────────────────────────────────┐
   │ INSERT into content table              │
   │                                        │
   │ Table Structure:                       │
   │ - id: UUID PRIMARY KEY                 │
   │ - user_id: UUID FOREIGN KEY            │
   │ - platform: VARCHAR                    │
   │ - generated_text: TEXT                 │
   │ - created_at: TIMESTAMP DEFAULT NOW() │
   └────────────────────────────────────────┘
                    │
                    ▼

7. RESPONSE (200 Created)
   ┌────────────────────────────────────────┐
   │ {                                      │
   │   "id": "550e8400-e29b-41d4-a716...", │
   │   "user_id": "00d47cb7-3692-44fa...", │
   │   "platform": "instagram",             │
   │   "generated_text": "...",             │
   │   "hashtags": ["#marketing", ...],     │
   │   "call_to_action": "Subscribe now",   │
   │   "status": "draft",                   │
   │   "created_at": "2026-05-24T23:30..." │
   │ }                                      │
   └────────────────────────────────────────┘
```

---

## Layered Architecture

### 1. Route Layer (`app/routes/v1/`)

**Purpose:** HTTP endpoint definition and request routing

**Files:**

- `health.py` - Service health checks
- `auth.py` - Authentication endpoints
- `profile.py` - User profile management
- `messages.py` - Messaging endpoints
- `content.py` - Content generation
- `scheduler.py` - Post scheduling
- `analytics.py` - Analytics querying
- `tracking.py` - Keyword/mention tracking
- `onboarding.py` - Platform connection setup
- `social.py` - Social account management

**Key Patterns:**

```python
from fastapi import APIRouter, Depends
from app.schemas.content_schema import GenerateContentSchema
from app.middlewares.auth import get_current_user
from app.controllers.content_controller import content_controller

router = APIRouter(prefix="/content", tags=["Content"])

@router.post("/generate")
async def generate_content(
    body: GenerateContentSchema,
    user_id: str = Depends(get_current_user)  # Dependency injection
):
    """
    Pydantic automatically validates request body.
    JWT middleware validates token before this executes.
    """
    return await content_controller.generate_content(user_id, body)
```

**Responsibilities:**

- Define HTTP methods and paths
- Apply route-level middleware
- Extract path/query parameters
- Delegate to controllers

---

### 2. Controller Layer (`app/controllers/`)

**Purpose:** Orchestrate request processing and coordinate services

**Key Files:**

- `auth_controller.py`
- `content_controller.py`
- `message_controller.py`
- `profile_controller.py`
- `analytics_controller.py`
- `scheduler_controller.py`
- `tracking_controller.py`
- `social_controller.py`

**Example Controller:**

```python
class ContentController:

    async def generate_content(self, user_id: str, body: GenerateContentSchema):
        """
        Orchestrate content generation workflow:
        1. Validate user permissions
        2. Call content service
        3. Format response
        """
        # Service orchestration
        content = await content_service.generate(user_id, body)

        # Response formatting (already handled by service)
        return content

    async def get_history(
        self,
        user_id: str,
        platform: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0
    ):
        """Fetch paginated content history with filters."""
        items = await content_service.get_history(
            user_id, platform, status, limit, offset
        )
        total = await content_repository.count_by_user(user_id)

        return {
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset
        }

content_controller = ContentController()
```

**Responsibilities:**

- Validate request parameters
- Coordinate between multiple services
- Handle response formatting
- Transaction management
- Error handling and logging

---

### 3. Service Layer (`app/services/`)

**Purpose:** Core business logic and external service orchestration

**Key Files:**

- `auth_service.py` - JWT generation, password hashing
- `content_service.py` - AI content generation workflow
- `message_service.py` - Message ingestion & AI replies
- `analytics_service.py` - Metrics aggregation
- `scheduler_service.py` - Post publishing automation
- `tracking_service.py` - Keyword/mention tracking

**Example Service:**

```python
class ContentService:

    async def generate(
        self,
        user_id: str,
        request: GenerateContentSchema
    ) -> dict:
        """
        Generate social media content using AI.

        Flow:
        1. Check rate limits
        2. Call OpenRouter LLM API
        3. Extract metadata (hashtags, CTA)
        4. Persist to database
        5. Return created content
        """
        # Rate limiting check
        is_allowed = await self._check_rate_limit(user_id)
        if not is_allowed:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        # Call OpenRouter (external AI service)
        try:
            ai_response = await openrouter.generate_content(
                prompt=request.prompt,
                tone=request.tone,
                platform=request.platform
            )
        except openrouter.APIError as e:
            # Per requirements: ignore agent errors
            logger.warning(f"OpenRouter error: {e}")
            ai_response = self._generate_fallback(request.prompt)

        # Extract metadata from generated text
        hashtags = self._extract_hashtags(ai_response)
        cta = self._extract_cta(ai_response)

        # Persist to database
        content_data = {
            "user_id": user_id,
            "platform": request.platform,
            "content_type": request.content_type,
            "prompt": request.prompt,
            "generated_text": ai_response,
            "hashtags": hashtags,
            "call_to_action": cta,
            "status": "draft",
            "image_url": None  # Future: image generation
        }

        result = await content_repository.create(content_data)
        return result

    async def get_history(
        self,
        user_id: str,
        platform: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[dict]:
        """Fetch paginated content with filters."""
        return await content_repository.get_by_user(
            user_id=user_id,
            platform=platform,
            status=status,
            limit=limit,
            offset=offset
        )

    def _extract_hashtags(self, text: str) -> list[str]:
        """Parse hashtags from generated text."""
        import re
        return re.findall(r'#\w+', text)

    def _extract_cta(self, text: str) -> str:
        """Extract call-to-action from text."""
        # ML/pattern matching logic
        return "Check our website"

content_service = ContentService()
```

**Key Responsibilities:**

- Implement business logic
- Orchestrate external service calls (OpenRouter, webhooks)
- Data transformation and enrichment
- Caching and performance optimization
- Error handling with retries

---

### 4. Repository Layer (`app/repositories/`)

**Purpose:** Abstracted data access with raw SQL

**Key Files:**

- `auth_repository.py`
- `content_repository.py`
- `message_repository.py`
- `analytics_repository.py`
- `scheduler_repository.py`
- `tracking_repository.py`
- `social_repository.py`
- `profile_repository.py`

**Example Repository:**

```python
class ContentRepository:

    async def create(self, data: dict) -> dict:
        """Insert new content record."""
        query = """
            INSERT INTO content (
                user_id, platform, content_type, prompt,
                generated_text, hashtags, call_to_action,
                status, image_url, created_at
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, NOW()
            )
            RETURNING *
        """

        async with db.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                data["user_id"],
                data["platform"],
                data["content_type"],
                data["prompt"],
                data["generated_text"],
                data["hashtags"],  # PostgreSQL array
                data["call_to_action"],
                data["status"],
                data["image_url"]
            )

        return self._row_to_dict(row)

    async def get_by_user(
        self,
        user_id: str,
        platform: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[dict]:
        """Fetch content with optional filtering."""
        query = "SELECT * FROM content WHERE user_id = $1"
        params = [user_id]
        param_index = 2

        if platform:
            query += f" AND platform = ${param_index}"
            params.append(platform)
            param_index += 1

        if status:
            query += f" AND status = ${param_index}"
            params.append(status)
            param_index += 1

        query += f" ORDER BY created_at DESC LIMIT ${param_index} OFFSET ${param_index + 1}"
        params.extend([limit, offset])

        async with db.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)

        return [self._row_to_dict(row) for row in rows]

    async def get_by_id(self, content_id: str, user_id: str) -> dict | None:
        """Fetch single content with ownership verification."""
        query = """
            SELECT * FROM content
            WHERE id = $1 AND user_id = $2
        """

        async with db.pool.acquire() as conn:
            row = await conn.fetchrow(query, content_id, user_id)

        return self._row_to_dict(row) if row else None

    async def update(self, content_id: str, user_id: str, data: dict) -> dict:
        """Update content (with ownership check)."""
        allowed_fields = {"generated_text", "hashtags", "call_to_action", "status"}
        update_fields = {k: v for k, v in data.items() if k in allowed_fields}

        if not update_fields:
            raise ValueError("No valid fields to update")

        set_clause = ", ".join(f"{k} = ${i+3}" for i, k in enumerate(update_fields.keys()))
        query = f"""
            UPDATE content
            SET {set_clause}
            WHERE id = $1 AND user_id = $2
            RETURNING *
        """

        async with db.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                content_id,
                user_id,
                *update_fields.values()
            )

        return self._row_to_dict(row)

    async def count_by_user(self, user_id: str) -> int:
        """Count total content for user."""
        query = "SELECT COUNT(*) FROM content WHERE user_id = $1"

        async with db.pool.acquire() as conn:
            count = await conn.fetchval(query, user_id)

        return count

    @staticmethod
    def _row_to_dict(row) -> dict:
        """Convert asyncpg Record to dict."""
        return dict(row) if row else None

content_repository = ContentRepository()
```

**Key Patterns:**

- Raw SQL with parameterized queries (SQL injection prevention)
- asyncpg connection pooling
- Row-to-dict conversion
- Ownership/permission checks in queries
- Query building for dynamic filters

---

## Database Schema

### Core Tables

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    avatar_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Content (Generated social posts)
CREATE TABLE content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    content_type VARCHAR(50),
    prompt TEXT NOT NULL,
    generated_text TEXT NOT NULL,
    hashtags TEXT[] DEFAULT '{}',  -- PostgreSQL array
    call_to_action VARCHAR(255),
    status VARCHAR(50) DEFAULT 'draft',  -- draft | scheduled | posted | archived
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (user_id),
    INDEX (platform),
    INDEX (status)
);

-- Scheduled Posts
CREATE TABLE scheduled_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_id UUID REFERENCES content(id),
    platform VARCHAR(50) NOT NULL,
    post_text TEXT NOT NULL,
    scheduled_for TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',  -- pending | published | failed | cancelled
    published_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (user_id),
    INDEX (scheduled_for),
    INDEX (status)
);

-- Messages (Incoming DMs, comments)
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    sender_name VARCHAR(255) NOT NULL,
    message_text TEXT NOT NULL,
    external_message_id VARCHAR(255),
    is_replied BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (user_id),
    INDEX (platform)
);

-- Social Accounts (Connected platforms)
CREATE TABLE social_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    account_name VARCHAR(255),
    account_id VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, platform, account_id),
    INDEX (user_id)
);

-- Analytics
CREATE TABLE analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scheduled_post_id UUID REFERENCES scheduled_posts(id),
    platform VARCHAR(50) NOT NULL,
    likes INT DEFAULT 0,
    impressions INT DEFAULT 0,
    reach INT DEFAULT 0,
    engagement_rate FLOAT DEFAULT 0.0,
    clicks INT DEFAULT 0,
    shares INT DEFAULT 0,
    comments INT DEFAULT 0,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (user_id),
    INDEX (platform),
    INDEX (recorded_at)
);

-- Tracking Rules
CREATE TABLE tracking_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,  -- hashtag | mention | keyword
    value VARCHAR(255) NOT NULL,
    platform VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (user_id),
    INDEX (type)
);

-- Tracked Events (Mentions, hashtags, keywords found)
CREATE TABLE tracked_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rule_id UUID REFERENCES tracking_rules(id),
    platform VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,  -- comment | mention | hashtag | dm
    content TEXT NOT NULL,
    author_username VARCHAR(255) NOT NULL,
    external_id VARCHAR(255),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (user_id),
    INDEX (rule_id),
    INDEX (is_read)
);
```

**Design Patterns:**

- UUID primary keys (scalable, privacy-friendly)
- Foreign keys with CASCADE delete (referential integrity)
- Indexes on frequently queried columns
- Created_at timestamps on audit trails
- Status enums as VARCHAR for flexibility
- PostgreSQL arrays for tag collections

---

## Authentication & Authorization

### JWT Flow

```python
# app/core/security.py
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentials

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_access_token(user_id: str, expires_delta: timedelta = None) -> str:
    """
    Generate JWT token with user_id as subject.
    Token expires in 24 hours by default.
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=24)

    expire = datetime.utcnow() + expires_delta
    payload = {
        "sub": user_id,  # Subject = user_id
        "exp": expire
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token: str) -> str:
    """Decode JWT and return user_id, or raise exception."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Dependency Injection for Auth

```python
# app/middlewares/auth.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from app.core.security import verify_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security)
) -> str:
    """
    Extract and validate JWT from request headers.
    Returns user_id if valid, raises 401 otherwise.

    Used in routes via:
    @router.get("/endpoint")
    async def handler(user_id: str = Depends(get_current_user)):
        ...
    """
    token = credentials.credentials
    user_id = verify_token(token)
    return user_id
```

### Request Flow with Auth

```
1. Client sends:
   GET /api/v1/me
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

2. Route handler receives Depends(get_current_user)
   FastAPI injects dependency automatically

3. get_current_user() executes:
   - Extracts token from Authorization header
   - Calls verify_token(token)
   - Returns user_id or raises 401

4. Route handler receives user_id parameter
   - Can use directly without re-validating
   - Ownership checks use this user_id

5. Response includes only user's data
   - Repository query: WHERE user_id = $1
```

---

## AI Integration Points

### OpenRouter API (LLM Service)

**File:** `app/utils/openrouter.py`

```python
import httpx

class OpenRouterClient:
    """
    Wrapper around OpenRouter API for LLM inference.
    Handles prompt engineering, response parsing, retries.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.client = httpx.AsyncClient(timeout=60.0)

    async def generate_content(
        self,
        prompt: str,
        tone: str = "professional",
        platform: str | None = None
    ) -> str:
        """
        Generate social media content using LLM.

        Prompt engineering:
        - Includes tone instruction
        - Platform-specific guidance
        - Output format instructions

        Error handling:
        - Timeout: return fallback
        - API error: return fallback
        - Per requirements: ignore errors, continue
        """
        system_prompt = f"""
        You are an expert social media content creator.
        Generate engaging content for {platform} with {tone} tone.
        Include relevant hashtags and a call-to-action.
        Keep response under 280 characters for Twitter.
        """

        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": "openai/gpt-4",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                headers={"Authorization": f"Bearer {self.api_key}"}
            )

            response.raise_for_status()
            data = response.json()

            return data["choices"][0]["message"]["content"]

        except httpx.TimeoutException:
            logger.warning(f"OpenRouter timeout for prompt: {prompt}")
            return self._fallback_content(prompt)

        except httpx.HTTPError as e:
            logger.warning(f"OpenRouter API error: {e}")
            return self._fallback_content(prompt)

        except Exception as e:
            logger.error(f"Unexpected error in content generation: {e}")
            return self._fallback_content(prompt)

    def _fallback_content(self, prompt: str) -> str:
        """Generate simple fallback content when AI unavailable."""
        return f"Check out this: {prompt.split()[0]}... #marketing #growth"

    async def get_ai_reply(self, message: str) -> str:
        """Generate AI reply suggestions for incoming messages."""
        # Similar implementation with message-specific prompt
        pass

openrouter = OpenRouterClient(api_key=settings.OPENROUTER_API_KEY)
```

### Usage in Services

```python
# In content_service.py
try:
    ai_response = await openrouter.generate_content(
        prompt=request.prompt,
        tone=request.tone,
        platform=request.platform
    )
except Exception as e:
    logger.warning(f"AI generation failed: {e}")
    ai_response = "Default content"

# Continue processing even if AI fails
```

---

## Async/Concurrency Patterns

### Async Request Handling

```python
# FastAPI automatically handles async/await
# All endpoint handlers are async

@router.post("/content/generate")
async def generate_content(
    body: GenerateContentSchema,
    user_id: str = Depends(get_current_user)
):
    """
    Async function = non-blocking request handling.
    While waiting for:
    - OpenRouter API response
    - Database queries
    - External webhooks

    FastAPI event loop can process other requests.
    """
    return await content_controller.generate_content(user_id, body)
```

### Connection Pooling

```python
# app/db/connection.py
class Database:
    pool = None

    async def connect(self):
        """Initialize asyncpg connection pool at startup."""
        self.pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=10,          # Min connections
            max_size=100,         # Max connections
            statement_cache_size=0
        )

    async def disconnect(self):
        """Close pool gracefully on shutdown."""
        await self.pool.close()

# Usage in repositories
async with db.pool.acquire() as conn:
    result = await conn.fetchrow(query, *params)
```

### Concurrent Operations

```python
import asyncio

async def batch_operations(user_id: str):
    """Execute multiple operations concurrently."""

    # Gather multiple coroutines
    results = await asyncio.gather(
        content_service.get_history(user_id),
        analytics_service.get_overview(user_id),
        message_service.get_pending(user_id),
        tracking_service.get_rules(user_id)
    )

    history, analytics, messages, rules = results

    return {
        "content": history,
        "analytics": analytics,
        "messages": messages,
        "rules": rules
    }
```

---

## Error Handling

### Global Error Handler

```python
# app/main.py
@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception
):
    """
    Catch all unhandled exceptions.
    Log for debugging, return safe error response.
    """
    logger.exception("Unhandled error: %s", exc)

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

### Service-Level Error Handling

```python
# Example from message_service.py
async def receive_message(
    user_id: str,
    platform: str,
    sender_name: str,
    message_text: str
) -> dict:
    """
    Handle incoming message with error recovery.
    """
    try:
        # Validate platform
        if platform not in SUPPORTED_PLATFORMS:
            raise ValueError(f"Unsupported platform: {platform}")

        # Persist message
        message = await message_repository.create({
            "user_id": user_id,
            "platform": platform,
            "sender_name": sender_name,
            "message_text": message_text
        })

        return message

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error in receive_message: {e}")
        raise HTTPException(status_code=500, detail="Failed to receive message")
```

### HTTP Exception Mapping

```python
# FastAPI automatically converts exceptions to HTTP responses
raise HTTPException(status_code=400, detail="Invalid email")
# → 400 Bad Request { "detail": "Invalid email" }

raise HTTPException(status_code=401, detail="Invalid credentials")
# → 401 Unauthorized { "detail": "Invalid credentials" }

raise HTTPException(status_code=404, detail="Content not found")
# → 404 Not Found { "detail": "Content not found" }

raise HTTPException(status_code=429, detail="Rate limited")
# → 429 Too Many Requests { "detail": "Rate limited" }
```

---

## Deployment & Configuration

### Environment Variables

```bash
# .env
DATABASE_URL=postgresql://user:password@host:5432/dbname
OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxx
JWT_SECRET_KEY=your-super-secret-key
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://frontend.example.com
```

### Configuration Management

```python
# app/core/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Astra AI Marketing API"
    API_VERSION: str = "1.0.0"
    DATABASE_URL: str
    OPENROUTER_API_KEY: str
    JWT_SECRET_KEY: str
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
```

### Application Lifecycle

```python
# app/main.py
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown hooks.
    Manages resource initialization.
    """
    # STARTUP
    logger.info("Starting up Astra AI API…")
    await db.connect()
    # Initialize other resources

    yield  # Application runs here

    # SHUTDOWN
    logger.info("Shutting down…")
    await db.disconnect()
    # Cleanup other resources

app = FastAPI(lifespan=lifespan)
```

### CORS Configuration

```python
# app/core/cors.py
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app: FastAPI):
    """Configure Cross-Origin Resource Sharing."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

### Rate Limiting Middleware

```python
# app/middlewares/rate_limit.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting.
    In production, use Redis for distributed rate limiting.
    """

    def __init__(self, app):
        super().__init__(app)
        self.requests = {}  # IP → [timestamps]

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()

        # Clean old entries
        if client_ip in self.requests:
            self.requests[client_ip] = [
                t for t in self.requests[client_ip]
                if now - t < 60  # 1-minute window
            ]

        # Check limit (10 requests per minute)
        if client_ip in self.requests and len(self.requests[client_ip]) >= 10:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"}
            )

        # Record request
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        self.requests[client_ip].append(now)

        return await call_next(request)
```

---

## Worker Processes

### Scheduled Tasks

**File:** `app/workers/scheduler_worker.py`

```python
"""
Background worker that periodically publishes scheduled posts.
Runs on separate process/container.
"""

async def publish_scheduled_posts():
    """
    Check database for posts that should be published now.
    Call platform APIs to actually post content.
    Update status in database.
    """
    query = """
        SELECT * FROM scheduled_posts
        WHERE status = 'pending'
        AND scheduled_for <= NOW()
        ORDER BY scheduled_for ASC
    """

    async with db.pool.acquire() as conn:
        posts = await conn.fetch(query)

    for post in posts:
        try:
            # Call platform API to publish
            result = await publish_to_platform(
                platform=post["platform"],
                post_text=post["post_text"],
                account_id=post["account_id"]
            )

            # Update status
            update_query = """
                UPDATE scheduled_posts
                SET status = 'published', published_at = NOW()
                WHERE id = $1
            """
            await conn.execute(update_query, post["id"])

        except Exception as e:
            logger.error(f"Failed to publish post {post['id']}: {e}")
            # Mark as failed
```

### Analytics Aggregation

**File:** `app/workers/analytics_worker.py`

```python
"""
Periodically aggregate analytics data for faster queries.
Fetch from platform APIs and update database.
"""

async def aggregate_analytics():
    """Fetch platform metrics and store in analytics table."""
    # Call Instagram API, Facebook API, etc.
    # Insert/update analytics records
    # Compute engagement rates
```

---

## Monitoring & Observability

### Logging

```python
# app/utils/logger.py
import logging

def get_logger(name: str) -> logging.Logger:
    """Get logger instance for module."""
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)
    return logger

# Usage:
logger = get_logger("astra.content_service")
logger.info("Content generated for user %s", user_id)
logger.warning("OpenRouter timeout, using fallback")
logger.error("Database connection failed", exc_info=True)
```

### Health Check

```python
@router.get("/")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}
```

### Metrics (Future)

```python
# Could integrate Prometheus for metrics:
# - Request count/latency by endpoint
# - Error rates
# - Database pool utilization
# - API call counts (OpenRouter)
```

---

## Data Flow Summary

```
User Request
    ↓
Route Handler (validates JWT, extracts params)
    ↓
Controller (orchestrates business logic)
    ↓
Service Layer (core logic, AI calls, data enrichment)
    ↓
Repository Layer (SQL queries, data access)
    ↓
Database (Supabase PostgreSQL)
    ↓
Response JSON
```

---

**Document Version:** 1.0  
**Last Updated:** May 24, 2026  
**Next Review:** June 30, 2026  
**Contact:** Backend Team
