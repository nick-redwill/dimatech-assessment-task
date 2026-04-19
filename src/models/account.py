from decimal import Decimal
from uuid import uuid4, UUID
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base

if TYPE_CHECKING:
    from models.user import UserOrm
    from models.transaction import TransactionOrm


class AccountOrm(Base):
    __tablename__ = "accounts"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    balance: Mapped[float] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
    )

    user: Mapped["UserOrm"] = relationship(back_populates="accounts")
    transactions: Mapped[list["TransactionOrm"]] = relationship(
        back_populates="account",
        cascade="all, delete-orphan",
    )
