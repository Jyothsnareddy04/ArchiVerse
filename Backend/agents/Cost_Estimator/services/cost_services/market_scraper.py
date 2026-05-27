import requests
from bs4 import BeautifulSoup

def sanitize_market(market):
    # realistic Indian ranges
    if not (300 <= market["cement"] <= 600):
        market["cement"] = 380

    if not (40000 <= market["steel"] <= 90000):
        market["steel"] = 65000

    if not (2000 <= market["sand"] <= 8000):
        market["sand"] = 4000

    return market

def fetch_market_rates():

    data = {
        "cement": 380,
        "steel": 65000,
        "sand": 4500,
        "labor_min": 600,
        "labor_max": 1000
    }

    try:
        url = "https://dir.indiamart.com/search.mp?ss=cement+price+hyderabad"
        res = requests.get(url, timeout=5)

        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")

            # 🔥 Example parsing (adjust selector)
            price_tag = soup.find("span", {"class": "price"})
            if price_tag:
                price = price_tag.text.replace("₹", "").strip()
                data["cement"] = float(price)

    except Exception as e:
        print("Scraper failed, using fallback:", e)

    return data