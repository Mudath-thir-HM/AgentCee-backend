-- ============================================================
-- Migration 002: Scheduler, Analytics, Tracking
-- ============================================================

-- Scheduled Posts
CREATE TABLE IF NOT EXISTS scheduled_posts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    content_id  UUID REFERENCES generated_assets(id) ON DELETE SET NULL,
    platform    TEXT NOT NULL,
    post_text   TEXT NOT NULL,
    scheduled_for TIMESTAMP WITH TIME ZONE NOT NULL,
    status      TEXT NOT NULL DEFAULT 'pending',
    -- pending | published | failed | cancelled
    published_at  TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_scheduled_posts_user_id
    ON scheduled_posts(user_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_status
    ON scheduled_posts(status);
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_scheduled_for
    ON scheduled_posts(scheduled_for);

-- Post Analytics
CREATE TABLE IF NOT EXISTS post_analytics (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    scheduled_post_id UUID REFERENCES scheduled_posts(id) ON DELETE SET NULL,
    platform          TEXT NOT NULL,
    likes             INTEGER NOT NULL DEFAULT 0,
    impressions       INTEGER NOT NULL DEFAULT 0,
    reach             INTEGER NOT NULL DEFAULT 0,
    engagement_rate   FLOAT NOT NULL DEFAULT 0,
    clicks            INTEGER NOT NULL DEFAULT 0,
    shares            INTEGER NOT NULL DEFAULT 0,
    comments          INTEGER NOT NULL DEFAULT 0,
    recorded_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_post_analytics_user_id
    ON post_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_post_analytics_platform
    ON post_analytics(platform);
CREATE INDEX IF NOT EXISTS idx_post_analytics_recorded_at
    ON post_analytics(recorded_at);

-- Tracking Rules (hashtags, mentions, keywords)
CREATE TABLE IF NOT EXISTS tracking_rules (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    type       TEXT NOT NULL,
    -- hashtag | mention | keyword
    value      TEXT NOT NULL,
    platform   TEXT,
    -- NULL = all platforms
    is_active  BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (user_id, type, value, platform)
);

CREATE INDEX IF NOT EXISTS idx_tracking_rules_user_id
    ON tracking_rules(user_id);

-- Tracked Events
CREATE TABLE IF NOT EXISTS tracked_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    rule_id         UUID REFERENCES tracking_rules(id) ON DELETE SET NULL,
    platform        TEXT NOT NULL,
    event_type      TEXT NOT NULL,
    content         TEXT,
    author_username TEXT,
    external_id     TEXT,
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tracked_events_user_id
    ON tracked_events(user_id);
CREATE INDEX IF NOT EXISTS idx_tracked_events_rule_id
    ON tracked_events(rule_id);

-- Ensure generated_assets table has status column
-- (May already exist, safe to add if missing)
ALTER TABLE generated_assets
    ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'draft';

ALTER TABLE generated_assets
    ADD COLUMN IF NOT EXISTS image_url TEXT;

-- RLS Policies
ALTER TABLE scheduled_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE post_analytics   ENABLE ROW LEVEL SECURITY;
ALTER TABLE tracking_rules   ENABLE ROW LEVEL SECURITY;
ALTER TABLE tracked_events   ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users own scheduled_posts" ON scheduled_posts
    USING (user_id = auth.uid()::UUID);

CREATE POLICY "Users own post_analytics" ON post_analytics
    USING (user_id = auth.uid()::UUID);

CREATE POLICY "Users own tracking_rules" ON tracking_rules
    USING (user_id = auth.uid()::UUID);

CREATE POLICY "Users own tracked_events" ON tracked_events
    USING (user_id = auth.uid()::UUID);
