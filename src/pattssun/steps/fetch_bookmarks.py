import json
from datetime import datetime, timezone

import httpx

from pattssun.config import Settings
from pattssun.models import PublicMetrics, Tweet

BOOKMARKS_URL = "https://api.x.com/2/users/{user_id}/bookmarks"

PARAMS = {
    "tweet.fields": "text,author_id,created_at,public_metrics",
    "expansions": "author_id",
    "user.fields": "username,name",
}


async def fetch_bookmarks(settings: Settings) -> list[Tweet]:
    url = BOOKMARKS_URL.format(user_id=settings.x_user_id)
    headers = {"Authorization": f"Bearer {settings.x_bearer_token}"}

    tweets: list[Tweet] = []
    pagination_token: str | None = None

    async with httpx.AsyncClient() as client:
        while True:
            params = {**PARAMS}
            if pagination_token:
                params["pagination_token"] = pagination_token

            resp = await client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()

            if "data" not in data:
                break

            # Build author lookup from includes
            authors: dict[str, dict[str, str]] = {}
            for user in data.get("includes", {}).get("users", []):
                authors[user["id"]] = {
                    "username": user["username"],
                    "name": user["name"],
                }

            for tweet_data in data["data"]:
                author = authors.get(tweet_data["author_id"], {})
                tweets.append(
                    Tweet(
                        id=tweet_data["id"],
                        text=tweet_data["text"],
                        author_username=author.get("username", "unknown"),
                        author_name=author.get("name", "Unknown"),
                        created_at=tweet_data["created_at"],
                        public_metrics=PublicMetrics(**tweet_data.get("public_metrics", {})),
                    )
                )

            meta = data.get("meta", {})
            pagination_token = meta.get("next_token")
            if not pagination_token:
                break

    return tweets


def save_bookmarks(settings: Settings, tweets: list[Tweet]) -> None:
    out_dir = settings.output_dir / "bookmarks"
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"bookmarks_{timestamp}.json"
    path.write_text(
        json.dumps([t.model_dump(mode="json") for t in tweets], indent=2),
        encoding="utf-8",
    )
    print(f"Saved {len(tweets)} bookmarks to {path}")
