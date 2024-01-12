from pydantic import BaseModel
from typing import Optional


class ExpenseItem(BaseModel):
    created_at: Optional[str]
    vendor_name: Optional[str]
    vendor_tax_id: Optional[str]
    payment_term: Optional[str]

    product_name: Optional[str]
    product_code: Optional[str]
    quantity: Optional[str]

    amount_amount: Optional[float]
    amount_currency_symbol: Optional[str]
    amount_currency_code: Optional[str]

    unit_price_amount: Optional[float]
    unit_price_currency_symbol: Optional[str]
    unit_price_currency_code: Optional[str]
