import os

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(page_title="Spotify Engagement Analytics", layout="wide")
DB_URI = os.getenv(
    "MYSQL_URI",
    "mysql+mysqlconnector://root:root@localhost:3306/spotify_analytics_dw",
)


@st.cache_data(ttl=300)
def load_data():
    engine = create_engine(DB_URI)
    try:
        tracks = pd.read_sql(
            "SELECT t.*, a.artist_name, a.primary_genre FROM tracks t "
            "LEFT JOIN artists a ON t.artist_id = a.artist_id",
            engine,
        )
        events = pd.read_sql("SELECT * FROM engagement_events", engine)
        return tracks, events
    finally:
        engine.dispose()


st.title("Spotify Engagement & Telemetry Analytics")
try:
    tracks_df, events_df = load_data()
except Exception as exc:
    st.error("Could not load MySQL data. Check that MySQL is running, the schema is loaded, and MYSQL_URI is correct.")
    st.exception(exc)
    st.stop()

merged = events_df.merge(tracks_df, on="track_id", how="left")
genres = ["All"] + sorted(tracks_df["primary_genre"].dropna().unique().tolist())
genre = st.sidebar.selectbox("Filter by genre", genres)
if genre != "All":
    merged = merged[merged["primary_genre"] == genre]

plays = merged[merged["event_type"].isin(["stream_complete", "stream_skip"])].copy()
notifs = merged[merged["event_type"].isin(["push_notif_open", "push_notif_dismiss"])].copy()
skip_rate = plays["event_type"].eq("stream_skip").mean() * 100 if not plays.empty else 0
open_rate = notifs["event_type"].eq("push_notif_open").mean() * 100 if not notifs.empty else 0
avg_duration = merged["duration_mins"].mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Telemetry events", f"{len(merged):,}")
c2.metric("Stream skip rate", f"{skip_rate:.1f}%")
c3.metric("Push notification open rate", f"{open_rate:.1f}%")
c4.metric("Average track duration", f"{avg_duration:.2f} min" if pd.notna(avg_duration) else "N/A")

left, right = st.columns(2)
with left:
    st.subheader("Skip rate by track duration")
    if plays.empty:
        st.info("No stream events match this filter.")
    else:
        plays["length_bucket"] = plays["duration_mins"].gt(4).map(
            {True: "> 4 min", False: "≤ 4 min"}
        )
        summary = plays.groupby("length_bucket")["event_type"].apply(
            lambda values: values.eq("stream_skip").mean() * 100
        ).rename("Skip rate (%)").reset_index()
        st.bar_chart(summary, x="length_bucket", y="Skip rate (%)")

with right:
    st.subheader("Notification open rate by delivery mode")
    if notifs.empty:
        st.info("No notification events match this filter.")
    else:
        summary = notifs.groupby("notification_delivery_mode")["event_type"].apply(
            lambda values: values.eq("push_notif_open").mean() * 100
        ).rename("Open rate (%)").reset_index()
        st.bar_chart(summary, x="notification_delivery_mode", y="Open rate (%)")
