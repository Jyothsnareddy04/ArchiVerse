from pydantic import BaseModel


class CostRequest(BaseModel):
    city: str
    quality: str
    area: int
    budget: int
    house_type: str
    floors: int