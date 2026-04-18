from pydantic import BaseModel
from decimal import Decimal
from uuid import UUID
from datetime import datetime


class TransactionCreate(BaseModel):
    account_id: UUID
    amount: Decimal


class TransactionRead(TransactionCreate):
    id: UUID
    created_at: datetime
