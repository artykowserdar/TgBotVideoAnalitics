CREATE TABLE IF NOT EXISTS videos (
    id UUID PRIMARY KEY,
    creator_id TEXT NOT NULL,
    video_created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    views_count INTEGER NOT NULL,
    likes_count INTEGER NOT NULL,
    comments_count INTEGER NOT NULL,
    reports_count INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS video_snapshots (
    id TEXT PRIMARY KEY,
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    views_count INTEGER NOT NULL,
    likes_count INTEGER NOT NULL,
    comments_count INTEGER NOT NULL,
    reports_count INTEGER NOT NULL,
    delta_views_count INTEGER NOT NULL,
    delta_likes_count INTEGER NOT NULL,
    delta_comments_count INTEGER NOT NULL,
    delta_reports_count INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);