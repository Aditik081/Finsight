import os
import requests
from dotenv import load_dotenv
from pymongo import UpdateOne
from database import companies_collection

load_dotenv()
KEY = os.getenv("FINNHUB_KEY")

# US, London, Tokyo, Hong Kong, India (NSE), Toronto, Frankfurt
EXCHANGES = ["US", "L", "T", "HK", "NS", "TO", "F"]


def import_exchange(exchange):
    r = requests.get(
        "https://finnhub.io/api/v1/stock/symbol",
        params={"exchange": exchange, "token": KEY},
        timeout=60,
    )
    r.raise_for_status()

    ops = []
    for s in r.json():
        if s.get("type") != "Common Stock" or not s.get("description"):
            continue
        ops.append(UpdateOne(
            {"ticker": s["symbol"]},
            {"$set": {
                "name": s["description"].title(),
                "ticker": s["symbol"],
                "sector": "N/A",
                "exchange": exchange,
                "currency": s.get("currency"),
            }},
            upsert=True,
        ))
    if ops:
        companies_collection.bulk_write(ops)
    print(exchange, "->", len(ops), "companies")


for ex in EXCHANGES:
    try:
        import_exchange(ex)
    except Exception as e:
        print(ex, "skipped:", e)