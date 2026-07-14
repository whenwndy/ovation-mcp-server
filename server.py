import json
import os
from pathlib import Path
from typing import Optional
from fastmcp import FastMCP
from pydantic import Field

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

_DATA_PATH = Path(__file__).parent / "data" / "ovation.json"
_db: dict = json.loads(_DATA_PATH.read_text())


def _match(record: dict, field: str, value: str) -> bool:
    """Case-insensitive substring match on a field."""
    return value.lower() in str(record.get(field, "")).lower()


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="ovation-mock",
    version="1.0.0",
    instructions=(
        "Mock Ovation guest feedback platform. Query reviews, CSAT scores, NPS, "
        "low-score alerts, and trend data across locations."
    ),
)

# ---------------------------------------------------------------------------
# Locations
# ---------------------------------------------------------------------------

@mcp.tool()
def get_locations(
    id: Optional[str] = Field(default=None, description="Filter by location ID, e.g. L001"),
    name: Optional[str] = Field(default=None, description="Filter by location name (partial match)"),
) -> list[dict]:
    """List locations. Optionally filter by ID or name."""
    results = _db["locations"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    return results


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------

@mcp.tool()
def get_reviews(
    location_id: Optional[str] = Field(default=None, description="Filter by location ID, e.g. L003"),
    flagged: Optional[bool] = Field(default=None, description="If true, return only flagged reviews; if false, only unflagged"),
    min_rating: Optional[int] = Field(default=None, description="Minimum rating (inclusive), 1–5"),
    max_rating: Optional[int] = Field(default=None, description="Maximum rating (inclusive), 1–5"),
    channel: Optional[str] = Field(default=None, description="Filter by review channel, e.g. Google | Yelp | in-app"),
) -> list[dict]:
    """List reviews. Optionally filter by location, flagged status, rating range, or channel."""
    results = _db["reviews"]
    if location_id:
        results = [r for r in results if r["location_id"].upper() == location_id.upper()]
    if flagged is not None:
        results = [r for r in results if r["flagged"] == flagged]
    if min_rating is not None:
        results = [r for r in results if r["rating"] >= min_rating]
    if max_rating is not None:
        results = [r for r in results if r["rating"] <= max_rating]
    if channel:
        results = [r for r in results if _match(r, "channel", channel)]
    return results


# ---------------------------------------------------------------------------
# Review Detail
# ---------------------------------------------------------------------------

@mcp.tool()
def get_review_detail(
    id: str = Field(description="Review ID, e.g. R1A2B"),
) -> Optional[dict]:
    """Return the full review_details record for a given review ID, including verbatim and survey answers."""
    for r in _db["review_details"]:
        if r["id"].upper() == id.upper():
            return r
    return None


# ---------------------------------------------------------------------------
# Feedback Summary
# ---------------------------------------------------------------------------

@mcp.tool()
def get_feedback_summary(
    location_id: Optional[str] = Field(default=None, description="Filter by location ID, e.g. L001"),
    period: Optional[str] = Field(default=None, description="Filter by period string (partial match), e.g. 2026-06-08"),
) -> list[dict]:
    """Return feedback summary records (CSAT, NPS, star distribution, metric scores) per location."""
    results = _db["feedback_summaries"]
    if location_id:
        results = [r for r in results if r["location_id"].upper() == location_id.upper()]
    if period:
        results = [r for r in results if _match(r, "period", period)]
    return results


# ---------------------------------------------------------------------------
# Low-Score Alerts
# ---------------------------------------------------------------------------

@mcp.tool()
def get_low_score_alerts(
    location_id: Optional[str] = Field(default=None, description="Filter by location ID, e.g. L003"),
    status: Optional[str] = Field(default=None, description="Filter by status: open | in_progress"),
) -> list[dict]:
    """List low-score alerts. Optionally filter by location or status."""
    results = _db["low_score_alerts"]
    if location_id:
        results = [r for r in results if r["location_id"].upper() == location_id.upper()]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    return results


# ---------------------------------------------------------------------------
# Trend Analysis
# ---------------------------------------------------------------------------

@mcp.tool()
def get_trend_analysis(
    location_id: Optional[str] = Field(default=None, description="Filter by location ID, e.g. L003"),
    metric: Optional[str] = Field(default=None, description="Filter by metric name (partial match), e.g. speed_of_service | overall_csat"),
) -> list[dict]:
    """Return trend analysis records with weekly score data points. Optionally filter by location or metric."""
    results = _db["trend_analysis"]
    if location_id:
        results = [r for r in results if r["location_id"].upper() == location_id.upper()]
    if metric:
        results = [r for r in results if _match(r, "metric", metric)]
    return results


# ---------------------------------------------------------------------------
# Keyword Themes
# ---------------------------------------------------------------------------

@mcp.tool()
def get_keyword_themes(
    location_id: Optional[str] = Field(default=None, description="Filter by location ID, e.g. L002"),
) -> list[dict]:
    """Return keyword theme records (positive and negative themes with counts) per location."""
    results = _db["keyword_themes"]
    if location_id:
        results = [r for r in results if r["location_id"].upper() == location_id.upper()]
    return results


# ---------------------------------------------------------------------------
# Location Comparison
# ---------------------------------------------------------------------------

@mcp.tool()
def get_location_comparison(
    period: Optional[str] = Field(default=None, description="Filter by period string (partial match), e.g. 2026-06-08"),
) -> list[dict]:
    """Return location comparison rankings (NPS, CSAT, review volume, top/bottom performer)."""
    results = _db["location_comparisons"]
    if period:
        results = [r for r in results if _match(r, "period", period)]
    return results


# ---------------------------------------------------------------------------
# Survey Response Rates
# ---------------------------------------------------------------------------

@mcp.tool()
def get_survey_response_rates(
    location_id: Optional[str] = Field(default=None, description="Filter by location ID, e.g. L001"),
) -> list[dict]:
    """Return survey response rate records (sent, opened, completed, rates) per location."""
    results = _db["survey_response_rates"]
    if location_id:
        results = [r for r in results if r["location_id"].upper() == location_id.upper()]
    return results


# ---------------------------------------------------------------------------
# Alert Thresholds
# ---------------------------------------------------------------------------

@mcp.tool()
def get_alert_thresholds(
    location_id: Optional[str] = Field(default=None, description="Filter by location ID, e.g. L004"),
) -> list[dict]:
    """Return alert threshold configuration per location (rating thresholds, notification settings)."""
    results = _db["alert_thresholds"]
    if location_id:
        results = [r for r in results if r["location_id"].upper() == location_id.upper()]
    return results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
