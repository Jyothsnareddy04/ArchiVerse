import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SERPAPI_KEY")


def extract_price_from_text(text):
    import re
    matches = re.findall(r'₹\s?(\d+)', text)
    if matches:
        values = [int(x) for x in matches]
        return sum(values) // len(values)
    return None


def fetch_price(query):
    response = requests.get(
        "https://serpapi.com/search",
        params={
            "engine": "google",
            "q": query,
            "api_key": API_KEY
        }
    )

    data = response.json()

    # AI Overview
    ai = data.get("ai_overview", {})
    blocks = ai.get("text_blocks", [])

    for block in blocks:
        if "list" in block:
            for item in block["list"]:
                if isinstance(item, dict) and "snippet" in item:
                    price = extract_price_from_text(item["snippet"])
                    if price:
                        return price

    # Organic
    for res in data.get("organic_results", []):
        snippet = res.get("snippet", "")
        price = extract_price_from_text(snippet)
        if price:
            return price

    return None


# 🔥 ADD THIS FUNCTION (YOUR ERROR FIX)
def sanitize_market(market):

    if not (300 <= market["cement"] <= 600):
        market["cement"] = 380

    if not (40000 <= market["steel"] <= 90000):
        market["steel"] = 65000

    if not (2000 <= market["sand"] <= 8000):
        market["sand"] = 4000

    return market


def fetch_real_market_rates(city="Hyderabad"):

    cement = fetch_price("cement price per bag India") or 380
    steel = fetch_price("steel price per ton India") or 65000
    sand = fetch_price("sand price per ton India") or 4000

    return sanitize_market({
        "cement": cement,
        "steel": steel,
        "sand": sand,
        "labor_min": 700,
        "labor_max": 1200
    })