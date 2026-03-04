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
