from pydantic import BaseModel, field_validator
from datetime import date
from typing import Optional, Literal
from decimal import Decimal

TypeLiteral = Literal["income", "expense"]
CategoryLiteral = Literal["salary", "carryover", "groceries", "eating_out"]

class TransactionBase(BaseModel):
    date: date
    type: TypeLiteral
    category: CategoryLiteral
    amount: Decimal
    description: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        return v.quantize(Decimal("0.01"))

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    date: Optional[date] = None
    type: Optional[TypeLiteral] = None
    category: Optional[CategoryLiteral] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None

class TransactionRead(TransactionBase):
    id: int

    class Config:
        from_attributes = True

class Summary(BaseModel):
    income: float
    expenses: float
    net: float
