-- ============================================================================
-- Live API Ingestion & Real-Time Engagement Pipeline (Spotify / FCM Model)
-- Relational Warehouse Schema
-- ============================================================================

CREATE DATABASE IF NOT EXISTS spotify_analytics_dw;
USE spotify_analytics_dw;

CREATE TABLE artists (
    artist_id VARCHAR(20) PRIMARY KEY,
    artist_name VARCHAR(100) NOT NULL,
    primary_genre VARCHAR(80),
    followers_count BIGINT,
    artist_popularity INT
);

CREATE TABLE tracks (
    track_id VARCHAR(30) PRIMARY KEY,
    track_name VARCHAR(150) NOT NULL,
    artist_id VARCHAR(20) NOT NULL,
    album_name VARCHAR(150),
    release_date DATE,
    duration_ms INT NOT NULL,
    popularity_score INT,
    explicit BOOLEAN,
    danceability DECIMAL(3,2),
    energy DECIMAL(3,2),
    tempo_bpm DECIMAL(5,1),
    duration_mins DECIMAL(5,2),
    FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
);

CREATE TABLE playlists (
    playlist_id VARCHAR(20) PRIMARY KEY,
    playlist_name VARCHAR(100) NOT NULL,
    curator_type VARCHAR(30),
    followers BIGINT,
    is_public BOOLEAN
);

CREATE TABLE playlist_tracks (
    playlist_id VARCHAR(20),
    track_id VARCHAR(30),
    position INT,
    added_at DATE,
    PRIMARY KEY (playlist_id, track_id),
    FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id),
    FOREIGN KEY (track_id) REFERENCES tracks(track_id)
);

CREATE TABLE engagement_events (
    event_id BIGINT PRIMARY KEY,
    event_timestamp DATETIME NOT NULL,
    user_id VARCHAR(20) NOT NULL,
    track_id VARCHAR(30) NOT NULL,
    event_type VARCHAR(30) NOT NULL,
    played_ms INT,
    device_type VARCHAR(30),
    notification_delivery_mode VARCHAR(20),
    FOREIGN KEY (track_id) REFERENCES tracks(track_id)
);

-- ============================================================================
