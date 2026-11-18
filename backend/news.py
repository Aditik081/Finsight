
import os
from database import articles_collection, companies_collection
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from database import articles_collection

load_dotenv(
    
)

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")


# ---------------- SENTIMENT ANALYSIS ----------------

POSITIVE_WORDS = {
    "profit", "growth", "surge", "gain", "success",
    "strong", "record", "upgrade", "beat", "positive",
    "rise", "rises", "increase", "increases",
    "bullish", "revenue growth", "expansion"
}

NEGATIVE_WORDS = {
    "loss", "decline", "drop", "fall", "crash",
    "fraud", "lawsuit", "warning", "weak",
    "downgrade", "miss", "negative", "risk",
    "debt", "layoff", "layoffs", "bearish",
    "decrease", "decreases"
}


def analyze_sentiment(text: str):
    text = (text or "").lower()

    positive_score = sum(
        1 for word in POSITIVE_WORDS if word in text
    )

    negative_score = sum(
        1 for word in NEGATIVE_WORDS if word in text
    )

    if positive_score > negative_score:
        return "Positive"

    elif negative_score > positive_score:
        return "Negative"

    return "Neutral"


# ---------------- COMPANY NEWS ----------------

def fetch_company_news(ticker: str):
    ticker = ticker.upper().strip()

    company = companies_collection.find_one(
        {"ticker": ticker},
        {"_id": 0, "name": 1}
    )

    company_name = company.get("name", "") if company else ""

    print("Company name:", company_name)

    if not FINNHUB_API_KEY:
        print("FINNHUB_API_KEY missing from .env")

        return list(
            articles_collection.find(
                {"ticker": ticker}, {"_id": 0}
            ).sort("published_at", -1).limit(20)
        )

    today = datetime.now(timezone.utc).date()
    start_date = today - timedelta(days=7)

    url = "https://finnhub.io/api/v1/company-news"

    params = {
        "symbol": ticker,
        "from": start_date.isoformat(),
        "to": today.isoformat(),
        "token": FINNHUB_API_KEY
    }

    try:
        response = requests.get(
            url, params=params, timeout=15
        )

        response.raise_for_status()
        articles = response.json()

        saved_news = []

        for article in articles:

            if not article.get("headline") or not article.get("url"):
                continue

            headline = article["headline"]
            summary = article.get("summary", "")

            sentiment = analyze_sentiment(
                headline + " " + summary
            )

            news_item = {
                "ticker": ticker,
                "headline": headline,
                "source": article.get("source", "Finnhub"),
                "url": article["url"],
                "published_at": article.get("datetime"),
                "summary": summary,
                "sentiment": sentiment
            }

            articles_collection.update_one(
                {"url": news_item["url"]},
                {"$set": news_item},
                upsert=True
            )

            saved_news.append(news_item)

        return saved_news

    except (requests.RequestException, ValueError) as error:

        print(f"News fetch failed: {error}")

        return list(
            articles_collection.find(
                {"ticker": ticker}, {"_id": 0}
            ).sort("published_at", -1).limit(20)
        )


# ---------------- MARKET NEWS ----------------

def fetch_market_news():
    return list(
        articles_collection.find(
            {"ticker": None}, {"_id": 0}
        ).sort("published_at", -1).limit(30)
    )


def update_existing_sentiments():
    articles = articles_collection.find({
        "sentiment": {"$exists": False}
    })

    updated_count = 0

    for article in articles:
        text = (
            article.get("headline", "") + " " +
            article.get("summary", "")
        )

        sentiment = analyze_sentiment(text)

        articles_collection.update_one(
            {"_id": article["_id"]},
            {"$set": {"sentiment": sentiment}}
        )

        updated_count += 1

    print(f"Updated articles: {updated_count}")
  
