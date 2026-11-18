
from datetime import datetime, timezone

from database import articles_collection


# ---------------- SENTIMENT STATISTICS ----------------

def get_sentiment_stats(ticker):

    ticker = ticker.upper()

    articles = list(
        articles_collection.find(
            {"ticker": ticker},
            {"_id": 0, "sentiment": 1}
        )
    )

    total = len(articles)

    positive = 0
    negative = 0
    neutral = 0
    missing = 0

    for article in articles:

        sentiment = article.get("sentiment")

        if sentiment == "Positive":
            positive += 1

        elif sentiment == "Negative":
            negative += 1

        elif sentiment == "Neutral":
            neutral += 1

        else:
            missing += 1

    return {
        "ticker": ticker,
        "total_articles": total,
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "missing": missing,

        "positive_percentage": round(
            positive / total * 100, 2
        ) if total else 0,

        "negative_percentage": round(
            negative / total * 100, 2
        ) if total else 0,

        "neutral_percentage": round(
            neutral / total * 100, 2
        ) if total else 0
    }


# ---------------- DAILY SENTIMENT TREND ----------------

def get_sentiment_trend(ticker):

    ticker = ticker.upper()

    articles = list(
        articles_collection.find(
            {
                "ticker": ticker,
                "published_at": {"$exists": True}
            },
            {
                "_id": 0,
                "published_at": 1,
                "sentiment": 1
            }
        ).sort("published_at", 1)
    )

    daily_data = {}

    for article in articles:

        timestamp = article.get("published_at")

        if not timestamp:
            continue

        try:
            date = datetime.fromtimestamp(
                float(timestamp),
                timezone.utc
            ).strftime("%Y-%m-%d")

        except (ValueError, TypeError, OSError):
            continue

        if date not in daily_data:

            daily_data[date] = {
                "positive": 0,
                "negative": 0,
                "neutral": 0
            }

        sentiment = article.get("sentiment")

        if sentiment == "Positive":
            daily_data[date]["positive"] += 1

        elif sentiment == "Negative":
            daily_data[date]["negative"] += 1

        elif sentiment == "Neutral":
            daily_data[date]["neutral"] += 1

    return {
        "ticker": ticker,
        "trend": [
            {
                "date": date,
                **counts
            }
            for date, counts in daily_data.items()
        ]
    }
