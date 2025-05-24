from pydantic import BaseModel, HttpUrl
from typing import List

class FeedsConfig(BaseModel):
    tech_ai_feeds: List[HttpUrl]
    general_feeds: List[HttpUrl]