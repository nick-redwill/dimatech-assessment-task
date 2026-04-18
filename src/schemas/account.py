from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel


class AccountCreate(BaseModel):
    user_id: int
    balance: Decimal = Decimal("0.00")


class AccountUpdate(BaseModel):
    balance: Decimal


class AccountRead(AccountCreate):
    id: UUID
