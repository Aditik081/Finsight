
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FINNHUB_API_KEY")

BASE_URL = "https://finnhub.io/api/v1"


def _check_api_key():
    if not API_KEY:
        raise ValueError("FINNHUB_API_KEY missing in .env")


# ---------------- STOCK QUOTE ----------------

def get_stock_quote(ticker: str):

    _check_api_key()

    response = requests.get(
        f"{BASE_URL}/quote",
        params={
            "symbol": ticker.upper(),
            "token": API_KEY
        },
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# ---------------- COMPANY SYMBOL SEARCH ----------------

def search_finnhub_symbol(query: str):

    _check_api_key()

    response = requests.get(
        f"{BASE_URL}/search",
        params={
            "q": query,
            "token": API_KEY
        },
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# ---------------- COMPANY PROFILE ----------------

def get_company_profile(ticker: str):

    _check_api_key()

    response = requests.get(
        f"{BASE_URL}/stock/profile2",
        params={
            "symbol": ticker.upper(),
            "token": API_KEY
        },
        timeout=10
    )

    response.raise_for_status()

    return response.json()
