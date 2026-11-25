# Spotify Engagement Analytics Pipeline

Python ETL loads the included CSV extracts into a MySQL warehouse. A Streamlit dashboard explores simulated playback and notification events alongside track metadata.

## Findings in the included sample

| Track duration | Plays | Skip rate |
| --- | ---: | ---: |
| ≤ 4 minutes | 942 | 22.82% |
| > 4 minutes | 871 | 52.12% |

These are descriptive results from the supplied sample data, not a causal product finding. Foreground and background notification open rates are also close in this sample (67.61% and 67.13%).

## Structure

```text
data/raw/                 Sample Spotify playlist JSON
data/processed/           Artists, tracks, playlists, links, and event CSVs
sql/01_schema_ddl.sql     MySQL tables and keys
sql/02_analytical_marts.sql  Sample analytical queries
src/etl_ingest.py         JSON parser and transactional CSV loader
app.py                    Streamlit dashboard
```

The included JSON is a fixture. The ETL parser accepts both legacy `track` and current `item` playlist payload keys; no live Spotify connector or credentials are included.

## Quickstart

1. Create a MySQL database/user and set `MYSQL_URI`, for example `mysql+mysqlconnector://user:password@localhost:3306/spotify_analytics_dw`.
2. Install packages: `pip install -r requirements.txt`.
3. Create the schema: `mysql -u root -p < sql/01_schema_ddl.sql`.
4. Preview JSON parsing: `python src/etl_ingest.py --parse-only`.
5. Load the CSVs: `python src/etl_ingest.py`.
6. Launch the dashboard: `streamlit run app.py`.

The ETL replaces the warehouse's table contents in one transaction. Do not point it at a warehouse containing data you need to preserve.
