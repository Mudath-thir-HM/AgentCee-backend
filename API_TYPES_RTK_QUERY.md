# API Types & Contracts for RTK Query Integration

**Target Audience:** Senior Frontend Developers (Redux Toolkit + RTK Query)  
**Version:** 1.0  
**Last Updated:** May 24, 2026

---

## Quick Reference: Base Configuration

```typescript
const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: 'http://localhost:8000/api/v1',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.accessToken
      if (token) {
        headers.set('Authorization', `Bearer ${token}`)
      }
      return headers
    }
  }),
  endpoints: builder => ({...})
})
```

---

## Authentication Endpoints

### 1. POST `/auth/register`

Create new user account with JWT token response.

**Request Type:**

```typescript
interface RegisterRequest {
  email: string; // Valid email address (RFC 5322)
  password: string; // Min 8 chars recommended (enforced on FE)
  company_name: string; // Organization name
}
```

**Response Type (201 Created):**

```typescript
interface AuthResponse {
  access_token: string; // JWT - store in secure context
  user: {
    id: string; // UUID v4
    email: string;
    password_hash: string; // Bcrypt hash - DO NOT use in FE logic
    company_name: string;
    avatar_url: string | null;
    connected_platforms: string[]; // Platform slugs: instagram, facebook, etc.
    created_at: string; // ISO 8601 timestamp
  };
}
```

**RTK Query Example:**

```typescript
register: builder.mutation<AuthResponse, RegisterRequest>({
  query: (credentials) => ({
    url: "/auth/register",
    method: "POST",
    body: credentials,
  }),
});
```

**Error Responses:**

- `400 Bad Request` - Email already registered
- `422 Unprocessable Entity` - Invalid email format or validation failure

---

### 2. POST `/auth/login`

Authenticate existing user and obtain JWT.

**Request Type:**

```typescript
interface LoginRequest {
  email: string;
  password: string;
}
```

**Response Type (200 OK):**

```typescript
interface AuthResponse {
  access_token: string;
  user: UserProfile; // Same structure as register response
}
```

**RTK Query Example:**

```typescript
login: builder.mutation<AuthResponse, LoginRequest>({
  query: (credentials) => ({
    url: "/auth/login",
    method: "POST",
    body: credentials,
  }),
});
```

**Error Responses:**

- `401 Unauthorized` - Invalid email or password
- `422 Unprocessable Entity` - Validation failure

**⚠️ Important:** JWT stored client-side should be kept in:

- ✓ HTTP-only cookie (preferred)
- ✓ Memory with secure refresh flow
- ✗ localStorage (XSS vulnerable)

---

## Profile Endpoints

### 1. GET `/me`

Fetch authenticated user's profile (requires Bearer token).

**Request:** No body  
**Query Params:** None

**Response Type (200 OK):**

```typescript
interface UserProfile {
  id: string;
  email: string;
  password_hash: string; // Bcrypt - DO NOT expose
  company_name: string | null;
  avatar_url: string | null;
  connected_platforms: string[];
  created_at: string; // ISO 8601
}
```

**RTK Query Example:**

```typescript
getProfile: builder.query<UserProfile, void>({
  query: () => ({
    url: "/me",
    method: "GET",
  }),
});
```

---

### 2. PATCH `/me`

Update user profile fields.

**Request Type:**

```typescript
interface ProfileUpdateRequest {
  company_name?: string; // Optional - null clears value
  avatar_url?: string; // Optional - presigned S3 URL
}
```

**Response Type (200 OK):**

```typescript
interface ProfileUpdateResponse {
  id: string;
  company_name: string | null;
  avatar_url: string | null;
  connected_platforms: string[];
}
```

**RTK Query Example:**

```typescript
updateProfile: builder.mutation<
  ProfileUpdateResponse,
  Partial<ProfileUpdateRequest>
>({
  query: (updates) => ({
    url: "/me",
    method: "PATCH",
    body: updates,
  }),
  invalidatesTags: ["Profile"],
});
```

---

## Onboarding Endpoints

### 1. POST `/onboarding/connect`

Initiate platform connection (Instagram, Facebook, etc.). Expected to trigger OAuth flow on FE.

**Request Type:**

```typescript
interface ConnectPlatformRequest {
  platform: "instagram" | "facebook" | "x" | "linkedin" | "tiktok";
  account_name: string; // Handle/username
}
```

**Response Type (200 OK):**

```typescript
interface OnboardingResponse {
  message: string; // Human-readable confirmation
}
```

**RTK Query Example:**

```typescript
connectPlatform: builder.mutation<OnboardingResponse, ConnectPlatformRequest>({
  query: (payload) => ({
    url: "/onboarding/connect",
    method: "POST",
    body: payload,
  }),
});
```

**Error Responses:**

- `422 Unprocessable Entity` - Invalid platform or validation failure

**Implementation Note:** This likely returns a connection URL or confirmation. Coordinate with backend on OAuth flow.

---

### 2. GET `/onboarding/platforms`

Retrieve list of connected platforms for current user.

**Response Type (200 OK):**

```typescript
interface ConnectedPlatformsResponse extends Array<string> {
  // Array of platform identifiers
  // Example: ['instagram', 'facebook', 'x']
}
```

**RTK Query Example:**

```typescript
getConnectedPlatforms: builder.query<string[], void>({
  query: () => ({
    url: "/onboarding/platforms",
    method: "GET",
  }),
  providesTags: ["Platforms"],
});
```

---

## Social Endpoints

### 1. POST `/social/connect`

Register social media account credentials/tokens.

**Request Type:**

```typescript
interface ConnectSocialRequest {
  platform: string; // instagram | facebook | x | linkedin | tiktok
  account_name: string; // Display name
  account_id: string; // Platform-specific ID (required)
}
```

**Response Type (200 OK):**

```typescript
interface SocialAccount {
  id: string; // UUID - local database ID
  platform: string;
  account_name: string | null;
  account_id: string | null;
  is_active: boolean;
}
```

**RTK Query Example:**

```typescript
connectSocialAccount: builder.mutation<SocialAccount, ConnectSocialRequest>({
  query: (payload) => ({
    url: "/social/connect",
    method: "POST",
    body: payload,
  }),
  invalidatesTags: ["SocialAccounts"],
});
```

---

### 2. GET `/social/accounts`

List all connected social accounts.

**Response Type (200 OK):**

```typescript
interface SocialAccountsList extends Array<SocialAccount> {
  // Each item has structure of SocialAccount
}
```

**RTK Query Example:**

```typescript
getSocialAccounts: builder.query<SocialAccount[], void>({
  query: () => ({
    url: "/social/accounts",
    method: "GET",
  }),
  providesTags: ["SocialAccounts"],
});
```

---

## Messages Endpoints

### 1. GET `/messages/`

Fetch all incoming messages for authenticated user.

**Query Params:** None (pagination coming soon)

**Response Type (200 OK):**

```typescript
interface Message {
  id: string;
  user_id: string;
  platform: string;
  sender_name: string;
  message_text: string;
  external_message_id: string | null;
  is_replied: boolean;
  created_at: string; // ISO 8601
}

interface MessagesListResponse extends Array<Message> {}
```

**RTK Query Example:**

```typescript
getMessages: builder.query<Message[], void>({
  query: () => ({
    url: "/messages/",
    method: "GET",
  }),
  providesTags: ["Messages"],
});
```

---

### 2. POST `/messages/receive`

Ingest incoming message from platform webhook or integration.

**Request Type:**

```typescript
interface ReceiveMessageRequest {
  platform: string; // instagram | facebook | x | linkedin | tiktok
  sender_name: string; // Username/handle of sender
  message_text: string; // Message content
}
```

**Response Type (201 Created):**

```typescript
interface Message {
  id: string;
  user_id: string;
  platform: string;
  sender_name: string;
  message_text: string;
  external_message_id: string | null;
  is_replied: boolean;
  created_at: string;
}
```

**RTK Query Example:**

```typescript
receiveMessage: builder.mutation<Message, ReceiveMessageRequest>({
  query: (payload) => ({
    url: "/messages/receive",
    method: "POST",
    body: payload,
  }),
  invalidatesTags: ["Messages"],
});
```

**Use Case:** Platform webhooks call this to store messages in DB.

---

### 3. POST `/messages/reply`

Send reply to incoming message (triggers AI agent).

**Request Type:**

```typescript
interface ReplyMessageRequest {
  message_id: string; // Reference to original message
  reply_text: string; // Optional - if not provided, AI generates
}
```

**Response Type (200 OK):**

```typescript
interface ReplyResponse {
  message_id: string;
  reply_text: string;
  sent_at: string; // ISO 8601
}
```

**RTK Query Example:**

```typescript
replyToMessage: builder.mutation<ReplyResponse, ReplyMessageRequest>({
  query: (payload) => ({
    url: "/messages/reply",
    method: "POST",
    body: payload,
  }),
  invalidatesTags: ["Messages"],
});
```

---

### 4. POST `/messages/ai-suggest`

Get AI-powered reply suggestions and sentiment analysis.

**Request Type:**

```typescript
interface AISuggestRequest {
  platform: string;
  message_text: string;
  sender_name: string;
  context?: string; // Optional historical context
}
```

**Response Type (200 OK):**

```typescript
interface AISuggestion {
  suggestions: string[]; // 3-5 reply options
  sentiment: "positive" | "negative" | "neutral";
  urgency: "low" | "medium" | "high";
}
```

**RTK Query Example:**

```typescript
getAISuggestions: builder.query<AISuggestion, AISuggestRequest>({
  query: (payload) => ({
    url: "/messages/ai-suggest",
    method: "POST",
    body: payload,
  }),
});
```

**⚠️ Note:** This may call OpenRouter API - handle timeout gracefully (30-60s).

---

### 5. POST `/messages/auto-reply`

Automatically reply to message using AI.

**Request Type:**

```typescript
interface AutoReplyRequest {
  platform: string;
  message_text: string;
  sender_name: string;
  interaction_type?: "comment" | "dm" | "mention";
}
```

**Response Type (200 OK):**

```typescript
interface AutoReplyResponse {
  success: boolean;
  reply_id: string;
  reply_text: string;
}
```

---

## Content Endpoints

### 1. POST `/content/generate`

Generate AI-powered social media content.

**Request Type:**

```typescript
interface GenerateContentRequest {
  platform: string; // instagram | facebook | x | linkedin | tiktok
  content_type: string; // post | caption | thread | story | carousel
  prompt: string; // User's content direction
  tone?: string; // professional | casual | humorous | inspirational
}
```

**Response Type (201 Created):**

```typescript
interface GeneratedContent {
  id: string;
  user_id: string;
  platform: string;
  content_type: string;
  prompt: string;
  generated_text: string;
  hashtags: string[];
  call_to_action: string;
  status: "draft" | "scheduled" | "posted" | "archived";
  image_url: string | null;
  created_at: string;
}
```

**RTK Query Example:**

```typescript
generateContent: builder.mutation<GeneratedContent, GenerateContentRequest>({
  query: (payload) => ({
    url: "/content/generate",
    method: "POST",
    body: payload,
  }),
  invalidatesTags: ["Content"],
});
```

**⚠️ Timeout:** 60-120s (involves OpenRouter API call)  
**Error Handling:** Gracefully handle OpenRouter API errors (ignore per requirements)

---

### 2. GET `/content/history`

Fetch paginated content generation history.

**Query Params:**

```typescript
interface ContentHistoryParams {
  platform?: string; // Filter by platform
  status?: string; // Filter by status (draft | scheduled | posted)
  limit?: number; // 1-100, default 50
  offset?: number; // Pagination offset, default 0
}
```

**Response Type (200 OK):**

```typescript
interface ContentHistoryResponse {
  items: GeneratedContent[];
  total: number;
  limit: number;
  offset: number;
}
```

**RTK Query Example:**

```typescript
getContentHistory: builder.query<ContentHistoryResponse, ContentHistoryParams>({
  query: (params) => ({
    url: "/content/history",
    method: "GET",
    params,
  }),
  providesTags: ["Content"],
});
```

---

### 3. GET `/content/{content_id}`

Fetch single content item by ID.

**Path Params:**

```typescript
interface GetContentParams {
  content_id: string;
}
```

**Response Type (200 OK):**

```typescript
interface GeneratedContent {
  // Same as generation response
}
```

**RTK Query Example:**

```typescript
getContent: builder.query<GeneratedContent, string>({
  query: (contentId) => ({
    url: `/content/${contentId}`,
    method: "GET",
  }),
  providesTags: (result, error, contentId) => [
    { type: "Content", id: contentId },
  ],
});
```

---

### 4. PATCH `/content/{content_id}`

Update generated content (edit text, add hashtags, etc.).

**Request Type:**

```typescript
interface UpdateContentRequest {
  generated_text?: string;
  hashtags?: string[];
  call_to_action?: string;
  status?: string; // Update draft status
}
```

**Response Type (200 OK):**

```typescript
interface GeneratedContent {
  // Updated content object
}
```

---

## Scheduler Endpoints

### 1. POST `/scheduler/`

Create scheduled post for future publishing.

**Request Type:**

```typescript
interface CreateScheduledPostRequest {
  content_id?: string; // Reference to generated content
  platform: string; // Required
  post_text: string; // Required
  scheduled_for: string; // ISO 8601 future datetime (required)
}
```

**Response Type (201 Created):**

```typescript
interface ScheduledPost {
  id: string;
  user_id: string;
  content_id: string | null;
  platform: string;
  post_text: string;
  scheduled_for: string; // ISO 8601
  status: "pending" | "published" | "failed" | "cancelled";
  published_at: string | null;
  error_message: string | null;
  created_at: string;
}
```

**RTK Query Example:**

```typescript
schedulePost: builder.mutation<ScheduledPost, CreateScheduledPostRequest>({
  query: (payload) => ({
    url: "/scheduler/",
    method: "POST",
    body: payload,
  }),
  invalidatesTags: ["ScheduledPosts"],
});
```

**Validation:** `scheduled_for` must be future datetime (validated on backend).

---

### 2. GET `/scheduler/`

List scheduled posts with optional filtering.

**Query Params:**

```typescript
interface ScheduledPostsQuery {
  status?: "pending" | "published" | "failed" | "cancelled";
  platform?: string;
}
```

**Response Type (200 OK):**

```typescript
interface ScheduledPostsList extends Array<ScheduledPost> {}
```

**RTK Query Example:**

```typescript
getScheduledPosts: builder.query<
  ScheduledPost[],
  { status?: string; platform?: string }
>({
  query: (params) => ({
    url: "/scheduler/",
    method: "GET",
    params,
  }),
  providesTags: ["ScheduledPosts"],
});
```

---

### 3. GET `/scheduler/{post_id}`

Fetch single scheduled post.

**Response Type (200 OK):**

```typescript
interface ScheduledPost {
  // Same structure as schedule response
}
```

---

### 4. PATCH `/scheduler/{post_id}`

Update scheduled post (reschedule, cancel, edit).

**Request Type:**

```typescript
interface UpdateScheduledPostRequest {
  post_text?: string;
  scheduled_for?: string; // New datetime
  status?: "pending" | "cancelled";
}
```

**Response Type (200 OK):**

```typescript
interface ScheduledPost {}
```

---

## Analytics Endpoints

### 1. POST `/analytics/record`

Ingest analytics metrics (called by webhooks).

**Request Type:**

```typescript
interface RecordAnalyticsRequest {
  scheduled_post_id?: string;
  platform: string;
  likes?: number; // default 0
  impressions?: number; // default 0
  reach?: number; // default 0
  engagement_rate?: number;
  clicks?: number; // default 0
  shares?: number; // default 0
  comments?: number; // default 0
}
```

**Response Type (201 Created):**

```typescript
interface AnalyticsRecord {
  id: string;
  user_id: string;
  scheduled_post_id: string | null;
  platform: string;
  likes: number;
  impressions: number;
  reach: number;
  engagement_rate: number;
  clicks: number;
  shares: number;
  comments: number;
  recorded_at: string;
}
```

---

### 2. GET `/analytics/overview`

Get aggregated analytics across all platforms.

**Response Type (200 OK):**

```typescript
interface AnalyticsOverview {
  total_reach: number;
  total_impressions: number;
  avg_engagement_rate: number;
  total_likes: number;
  total_shares: number;
  total_comments: number;
  total_clicks: number;
  posts_this_week: number;
  top_platform: string;
  growth_percentage: number;
}
```

**RTK Query Example:**

```typescript
getAnalyticsOverview: builder.query<AnalyticsOverview, void>({
  query: () => ({
    url: "/analytics/overview",
    method: "GET",
  }),
  providesTags: ["Analytics"],
});
```

---

### 3. GET `/analytics/weekly-engagement`

Get daily engagement data for last 7 days.

**Response Type (200 OK):**

```typescript
interface WeeklyEngagementData {
  day: "Mon" | "Tue" | "Wed" | "Thu" | "Fri" | "Sat" | "Sun";
  engagement: number;
}

// Return is array of 7 items, one per day
interface WeeklyEngagementResponse extends Array<WeeklyEngagementData> {}
```

**RTK Query Example:**

```typescript
getWeeklyEngagement: builder.query<WeeklyEngagementData[], void>({
  query: () => ({
    url: "/analytics/weekly-engagement",
    method: "GET",
  }),
  providesTags: ["Analytics"],
});
```

---

### 4. GET `/analytics/platforms`

Get per-platform breakdown of posts and engagement.

**Response Type (200 OK):**

```typescript
interface PlatformBreakdown {
  platform: string;
  posts: number;
  total_likes: number;
  total_impressions: number;
  avg_engagement_rate: number;
}

// Return may be single object or array - verify with backend
interface PlatformsBreakdownResponse extends Array<PlatformBreakdown> {}
```

**RTK Query Example:**

```typescript
getPlatformsBreakdown: builder.query<PlatformBreakdown[], void>({
  query: () => ({
    url: "/analytics/platforms",
    method: "GET",
  }),
  providesTags: ["Analytics"],
});
```

---

### 5. GET `/analytics/platforms/{platform}`

Get analytics for specific platform.

**Path Params:**

```typescript
interface PlatformAnalyticsParams {
  platform: string;
}
```

**Response Type (200 OK):**

```typescript
interface PlatformAnalytics {
  platform: string;
  posts: number;
  total_likes: number;
  total_impressions: number;
  avg_engagement_rate: number;
  // May include additional time-series data
}
```

---

## Tracking Endpoints

### 1. POST `/tracking/rules`

Create tracking rule for hashtags, mentions, or keywords.

**Request Type:**

```typescript
interface CreateTrackingRuleRequest {
  type: "hashtag" | "mention" | "keyword";
  value: string; // e.g., "marketing", "@brand", "#growth"
  platform?: string; // Optional - null = all platforms
}
```

**Response Type (201 Created):**

```typescript
interface TrackingRule {
  id: string;
  user_id: string;
  type: "hashtag" | "mention" | "keyword";
  value: string; // Normalized (lowercase, stripped of # or @)
  platform: string | null;
  is_active: boolean;
}
```

**RTK Query Example:**

```typescript
createTrackingRule: builder.mutation<TrackingRule, CreateTrackingRuleRequest>({
  query: (payload) => ({
    url: "/tracking/rules",
    method: "POST",
    body: payload,
  }),
  invalidatesTags: ["TrackingRules"],
});
```

**Value Normalization:** Backend strips leading `#` and `@`, converts to lowercase.

---

### 2. GET `/tracking/rules`

List all tracking rules with optional active filter.

**Query Params:**

```typescript
interface GetTrackingRulesParams {
  active_only?: boolean; // default true
}
```

**Response Type (200 OK):**

```typescript
interface TrackingRulesList extends Array<TrackingRule> {}
```

**RTK Query Example:**

```typescript
getTrackingRules: builder.query<TrackingRule[], { activeOnly?: boolean }>({
  query: (params) => ({
    url: "/tracking/rules",
    method: "GET",
    params: { active_only: params.activeOnly },
  }),
  providesTags: ["TrackingRules"],
});
```

---

### 3. PATCH `/tracking/rules/{rule_id}`

Enable or disable tracking rule.

**Request Type:**

```typescript
interface ToggleTrackingRuleRequest {
  is_active: boolean;
}
```

**Response Type (200 OK):**

```typescript
interface TrackingRule {
  // Updated rule
}
```

**RTK Query Example:**

```typescript
toggleTrackingRule: builder.mutation<
  TrackingRule,
  { ruleId: string; isActive: boolean }
>({
  query: ({ ruleId, isActive }) => ({
    url: `/tracking/rules/${ruleId}`,
    method: "PATCH",
    body: { is_active: isActive },
  }),
  invalidatesTags: (result, error, { ruleId }) => [
    { type: "TrackingRules", id: ruleId },
  ],
});
```

---

## Global Error Handling

All endpoints follow standard HTTP status codes:

```typescript
interface ApiErrorResponse {
  detail: string; // Error message
  // May include additional fields per endpoint
}

// Standard codes:
// 200/201 - Success
// 400 - Bad Request (validation failure)
// 401 - Unauthorized (missing/invalid token)
// 403 - Forbidden (insufficient permissions)
// 404 - Not Found
// 405 - Method Not Allowed (wrong HTTP verb)
// 422 - Unprocessable Entity (schema validation)
// 429 - Too Many Requests (rate limiting)
// 500 - Internal Server Error (server crash)
```

**RTK Query Global Error Handler:**

```typescript
const apiSlice = createApi({
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/v1',
    prepareHeaders: /* ... */
  }),
  endpoints: builder => ({}),
  // Handle errors globally
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore certain non-serializable values if needed
        ignoredActions: ['auth/setCredentials']
      }
    })
})

// In components:
const { data, isLoading, error } = useGetProfileQuery()

if (error) {
  const apiError = error as ApiErrorResponse
  console.error(apiError.detail)
}
```

---

## Rate Limiting

All endpoints are rate-limited to prevent abuse.

```typescript
// Client should implement exponential backoff:
const retryRequest = async (fn: () => Promise<T>, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error: any) {
      if (error.status === 429) {
        const delay = Math.pow(2, i) * 1000;
        await new Promise((resolve) => setTimeout(resolve, delay));
      } else {
        throw error;
      }
    }
  }
};
```

---

## Authentication Flow (Redux Store Shape)

```typescript
interface AuthState {
  accessToken: string | null;
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// Typical RTK state:
const authSlice = createSlice({
  name: "auth",
  initialState: {
    accessToken: localStorage.getItem("token"),
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addMatcher(apiSlice.endpoints.login.matchFulfilled, (state, action) => {
        state.accessToken = action.payload.access_token;
        state.user = action.payload.user;
        state.isAuthenticated = true;
        localStorage.setItem("token", action.payload.access_token);
      })
      .addMatcher(apiSlice.endpoints.login.matchRejected, (state) => {
        state.error = "Login failed";
      });
  },
});
```

---

## WebSocket Integration (Future)

Currently, all endpoints are RESTful. For real-time features (incoming messages, live analytics), consider WebSocket integration:

```typescript
// Pseudo-code for future implementation
const socket = io("http://localhost:8000", {
  auth: {
    token: store.getState().auth.accessToken,
  },
});

socket.on("message:new", (message: Message) => {
  dispatch(
    apiSlice.util.updateQueryData("getMessages", undefined, (draft) => {
      draft.unshift(message);
    }),
  );
});
```

---

## Summary: RTK Query Hooks Template

```typescript
export const astraApi = createApi({
  reducerPath: 'astraApi',
  baseQuery: fetchBaseQuery({
    baseUrl: 'http://localhost:8000/api/v1',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.accessToken
      if (token) headers.set('Authorization', `Bearer ${token}`)
      return headers
    }
  }),
  tagTypes: [
    'Profile',
    'SocialAccounts',
    'Messages',
    'Content',
    'ScheduledPosts',
    'Analytics',
    'TrackingRules'
  ],
  endpoints: builder => ({
    // Auth
    register: builder.mutation<AuthResponse, RegisterRequest>(...),
    login: builder.mutation<AuthResponse, LoginRequest>(...),

    // Profile
    getProfile: builder.query<UserProfile, void>(...),
    updateProfile: builder.mutation<ProfileUpdateResponse, Partial<ProfileUpdateRequest>>(...),

    // Messaging
    getMessages: builder.query<Message[], void>(...),
    receiveMessage: builder.mutation<Message, ReceiveMessageRequest>(...),
    replyMessage: builder.mutation<ReplyResponse, ReplyMessageRequest>(...),

    // Content Generation
    generateContent: builder.mutation<GeneratedContent, GenerateContentRequest>(...),
    getContentHistory: builder.query<ContentHistoryResponse, ContentHistoryParams>(...),

    // Scheduling
    schedulePost: builder.mutation<ScheduledPost, CreateScheduledPostRequest>(...),
    getScheduledPosts: builder.query<ScheduledPost[], ScheduledPostsQuery>(...),

    // Analytics
    getAnalyticsOverview: builder.query<AnalyticsOverview, void>(...),
    getWeeklyEngagement: builder.query<WeeklyEngagementData[], void>(...),
    getPlatformsBreakdown: builder.query<PlatformBreakdown[], void>(...),

    // Tracking
    createTrackingRule: builder.mutation<TrackingRule, CreateTrackingRuleRequest>(...),
    getTrackingRules: builder.query<TrackingRule[], GetTrackingRulesParams>(...),
    toggleTrackingRule: builder.mutation<TrackingRule, ToggleTrackingRuleRequest>(...),
  })
})

export const {
  useRegisterMutation,
  useLoginMutation,
  useGetProfileQuery,
  useUpdateProfileMutation,
  // ... etc
} = astraApi
```

---

**Last Updated:** May 24, 2026  
**Maintainer:** Backend Team  
**Issues/Questions:** Create backend GitHub issue with `[API]` prefix
