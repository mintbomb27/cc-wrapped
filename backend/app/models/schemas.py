from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CardBase(BaseModel):
    name: str
    last_4_digits: str
    bank: str = "other"  # 'hdfc', 'axis', 'other'

class CardCreate(CardBase):
    pass

class Card(CardBase):
    id: int

    class Config:
        from_attributes = True

class StatementBase(BaseModel):
    pass

class Statement(StatementBase):
    id: int
    card_id: int
    file_path: str
    upload_date: datetime

    class Config:
        from_attributes = True
