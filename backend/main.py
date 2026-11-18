
import re
from datetime import datetime, timezone, timedelta
from analytics import get_sentiment_stats, get_sentiment_trend
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ai_insights import generate_news_insights
from analytics import get_sentiment_stats

from database import companies_collection

from news import (
    fetch_company_news,
    fetch_market_news,
    articles_collection,
    update_existing_sentiments
)

from stock import (
    get_stock_quote,
    search_finnhub_symbol,
    get_company_profile
)


app = FastAPI(title="FinSight AI")


# ---------------- COMPANY MODEL ----------------

class Company(BaseModel):
    name: str
    ticker: str
    sector: str

    description: str = ""
    headquarters: str = ""
    website: str = ""

    exchange: str = ""
    country: str = ""
    currency: str = ""

    provider_symbols: dict[str, str] = Field(
        default_factory=dict
    )


# ---------------- CORS ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- HELPER ----------------

def _clean(docs):
    for document in docs:
        if "_id" in document:
            document["_id"] = str(document["_id"])

    return docs


# ---------------- HOME & HEALTH ----------------

@app.get("/")
def home():
    return {
        "message": "FinSight AI Backend is running"
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy"
    }


# ---------------- ADD COMPANY ----------------

@app.post("/api/companies")
def add_company(company: Company):

    company_data = company.model_dump()

    company_data["ticker"] = company_data["ticker"].upper()
    company_data["exchange"] = company_data["exchange"].upper()
    company_data["country"] = company_data["country"].upper()
    company_data["currency"] = company_data["currency"].upper()

    existing = companies_collection.find_one({
        "ticker": company_data["ticker"]
    })

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Company already exists"
        )

    result = companies_collection.insert_one(company_data)

    return {
        "message": "Company added successfully",
        "id": str(result.inserted_id)
    }


# ---------------- GET ALL COMPANIES ----------------

@app.get("/api/companies")
def get_companies():

    companies = list(
        companies_collection.find().limit(500)
    )

    return _clean(companies)


# ---------------- GLOBAL COMPANY SEARCH ----------------

@app.get("/api/companies/search")
def search_company(query: str):

    query = query.strip()

    if not query:
        return []

    safe_query = re.escape(query)

    mongo_companies = list(
        companies_collection.find({
            "$or": [
                {"name": {"$regex": safe_query, "$options": "i"}},
                {"ticker": {"$regex": safe_query, "$options": "i"}},
                {"description": {"$regex": safe_query, "$options": "i"}}
            ]
        }).limit(20)
    )

    results = _clean(mongo_companies)

    existing_tickers = {
        company.get("ticker", "").upper()
        for company in results
    }

    try:
        finnhub_data = search_finnhub_symbol(query)

        for item in finnhub_data.get("result", []):

            ticker = item.get("symbol", "").upper()

            if not ticker or "." in ticker:
                continue

            if ticker in existing_tickers:
                continue

            results.append({
                "name": item.get("description", ""),
                "ticker": ticker,
                "sector": "",
                "description": "",
                "headquarters": "",
                "website": "",
                "exchange": "",
                "country": "",
                "currency": "",
                "provider_symbols": {
                    "finnhub": ticker
                }
            })

            existing_tickers.add(ticker)

            if len(results) >= 20:
                break

    except Exception as e:
        print("FINNHUB COMPANY SEARCH ERROR:", repr(e))

    return results[:20]


# ---------------- COMPANY PROFILE ----------------

@app.get("/api/company-profile/{ticker}")
def company_profile(ticker: str):

    try:
        profile = get_company_profile(ticker)

        if not profile:
            raise HTTPException(
                status_code=404,
                detail="Company profile not found"
            )

        return profile

    except HTTPException:
        raise

    except Exception as e:
        print("COMPANY PROFILE ERROR:", repr(e))

        raise HTTPException(
            status_code=502,
            detail="Company profile could not be retrieved"
        )


# ---------------- GET COMPANY BY TICKER ----------------

@app.get("/api/companies/{ticker}")
def get_company(ticker: str):

    ticker = ticker.upper()

    company = companies_collection.find_one({
        "ticker": ticker
    })

    cache_time = None

    if company:
        cache_time = company.get("profile_cached_at")

    if cache_time:

        if cache_time.tzinfo is None:
            cache_time = cache_time.replace(
                tzinfo=timezone.utc
            )

        if datetime.now(timezone.utc) - cache_time < timedelta(days=7):
            company["_id"] = str(company["_id"])
            return company

    try:
        profile = get_company_profile(ticker)

        if not profile:

            if company:
                company["_id"] = str(company["_id"])
                return company

            raise HTTPException(
                status_code=404,
                detail="Company profile not found"
            )

        profile_data = {
            "ticker": ticker,
            "profile_cached_at": datetime.now(timezone.utc)
        }

        field_mapping = {
            "name": "name",
            "country": "country",
            "currency": "currency",
            "exchange": "exchange",
            "website": "weburl",
            "sector": "finnhubIndustry",
            "logo": "logo",
            "marketCapitalization": "marketCapitalization",
            "ipo": "ipo"
        }

        for db_field, api_field in field_mapping.items():

            value = profile.get(api_field)

            if value not in (None, ""):
                profile_data[db_field] = value

        companies_collection.update_one(
            {"ticker": ticker},
            {"$set": profile_data},
            upsert=True
        )

        updated_company = companies_collection.find_one({
            "ticker": ticker
        })

        updated_company["_id"] = str(
            updated_company["_id"]
        )

        return updated_company

    except HTTPException:
        raise

    except Exception as e:

        print("COMPANY PROFILE ERROR:", repr(e))

        if company:
            company["_id"] = str(company["_id"])
            return company

        raise HTTPException(
            status_code=502,
            detail="Company profile could not be retrieved"
        )


# ---------------- STOCK SEARCH ----------------

@app.get("/api/stocks/search/{query}")
def search_stock_symbol(query: str):

    try:
        return search_finnhub_symbol(query)

    except Exception as e:

        print("FINNHUB SEARCH ERROR:", repr(e))

        raise HTTPException(
            status_code=502,
            detail="Stock symbol search failed"
        )


# ---------------- STOCK QUOTE ----------------

@app.get("/api/stocks/{ticker}")
def stock_quote(ticker: str):

    try:
        return get_stock_quote(ticker)

    except Exception as e:

        print("FINNHUB STOCK ERROR:", repr(e))

        raise HTTPException(
            status_code=502,
            detail="Stock quote could not be retrieved"
        )


# ---------------- MARKET NEWS ----------------

@app.get("/api/news")
def get_market_news():

    try:
        fetch_market_news()

    except Exception as e:
        print("MARKET NEWS ERROR:", repr(e))

    articles = list(
        articles_collection.find({
            "ticker": None
        })
        .sort("published_at", -1)
        .limit(30)
    )

    return _clean(articles)


# ---------------- COMPANY NEWS ----------------

@app.get("/api/news/{ticker}")
def get_company_news(ticker: str):

    ticker = ticker.upper()

    try:
        fetch_company_news(ticker)

    except Exception as e:
        print("COMPANY NEWS ERROR:", repr(e))

    articles = list(
        articles_collection.find({
            "ticker": ticker
        })
        .sort("published_at", -1)
        .limit(30)
    )

    return _clean(articles)


# ---------------- UPDATE NEWS SENTIMENTS ----------------

@app.post("/api/news/update-sentiments")
def update_sentiments():

    try:
        update_existing_sentiments()

        return {
            "message": "Existing article sentiments updated"
        }

    except Exception as e:

        print("SENTIMENT UPDATE ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail="Failed to update sentiments"
        )


# ---------------- AI NEWS INSIGHTS ----------------

@app.get("/api/ai-insights/{ticker}")
def get_ai_insights(ticker: str):

    ticker = ticker.upper()

    try:
        articles = list(
            articles_collection.find(
                {"ticker": ticker},
                {"_id": 0}
            )
            .sort("published_at", -1)
            .limit(15)
        )

        if not articles:
            raise HTTPException(
                status_code=404,
                detail="No news available for this company"
            )

        insights = generate_news_insights(articles)

        return {
            "ticker": ticker,
            "ai_insights": insights
        }

    except HTTPException:
        raise

    except Exception as e:

        print("AI INSIGHTS ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail="Failed to generate AI insights"
        )


# ---------------- TEST COMPANY ----------------

@app.get("/api/test-company/{ticker}")
def test_company(ticker: str):

    company = companies_collection.find_one(
        {"ticker": ticker.upper()},
        {"_id": 0, "name": 1}
    )

    return {
        "company": company
    }


# ---------------- ANALYTICS INSIGHTS ----------------

@app.get("/api/insights/{ticker}")
def get_insights(ticker: str):

    ticker = ticker.upper()

    try:
        insights = get_sentiment_stats(ticker)

        return {
            "success": True,
            "data": insights
        }

    except Exception as e:

        print("ANALYTICS INSIGHTS ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail="Failed to generate analytics insights"
        )
@app.get("/api/insights/{ticker}")
def get_insights(ticker: str):
    ticker = ticker.upper()

    try:
        stats = get_sentiment_stats(ticker)
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        print("SENTIMENT STATS ERROR:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to generate sentiment statistics"
        )


@app.get("/api/insights/trend/{ticker}")
def get_insights_trend(ticker: str):
    ticker = ticker.upper()

    try:
        trend = get_sentiment_trend(ticker)
        return {
            "success": True,
            "data": trend
        }
    except Exception as e:
        print("SENTIMENT TREND ERROR:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to generate sentiment trend"
        )
