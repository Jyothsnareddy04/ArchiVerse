from fastapi import Header, HTTPException
from config.settings import API_KEY

def verify_api_key(x_api_key: str = Header(...)):

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    return x_api_key
