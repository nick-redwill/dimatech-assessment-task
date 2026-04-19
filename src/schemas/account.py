from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel


class AccountCreate(BaseModel):
    id: UUID | None = None
    user_id: int
    balance: Decimal = Decimal("0.00")


class AccountUpdate(BaseModel):
    balance: Decimal


class AccountRead(AccountCreate):
    id: UUID
