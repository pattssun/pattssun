from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class PublicMetrics(BaseModel):
    retweet_count: int = 0
    reply_count: int = 0
    like_count: int = 0
    quote_count: int = 0
    bookmark_count: int = 0
    impression_count: int = 0


class Tweet(BaseModel):
    id: str
    text: str
    author_username: str
    author_name: str
    created_at: datetime
    public_metrics: PublicMetrics


class Clip(BaseModel):
    clip_number: int
    duration_seconds: int
    narration: str
    tone: str
    emotion: str
    delivery: str
    purpose: str


class Script(BaseModel):
    total_duration_seconds: int
    clip_count: int
    clips: list[Clip]


class ScrapedBookmark(BaseModel):
    author_username: str
    text: str
    tweet_url: str
    scraped_at: str
    script: Script | None = None
