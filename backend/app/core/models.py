from sqlalchemy import Column, Integer, Date, String, Numeric, Text, Enum as SAEnum
from app.core.database import Base

TYPE_ENUM = ("income", "expense")
CATEGORY_ENUM = ("salary", "carryover", "groceries", "eating_out")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    type = Column(
        SAEnum(*TYPE_ENUM, name="transaction_type", native_enum=False),
        nullable=False,
    )
    category = Column(
        SAEnum(*CATEGORY_ENUM, name="transaction_category", native_enum=False),
        nullable=False,
    )
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(Text, nullable=True)
