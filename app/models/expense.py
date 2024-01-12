from pydantic import BaseModel
from typing import Optional


class ExpenseItem(BaseModel):
    invoice_date: Optional[str]

    vendor_name: Optional[str]

    invoice_id: Optional[str]
    payment_term: Optional[str]

    product_name: Optional[str]
    product_code: Optional[str]
    quantity: Optional[str]

    invoice_total_amount: Optional[float]
    invoice_total_currency_symbol: Optional[str]
    invoice_total_currency_code: Optional[str]

    vendor_tax_id: Optional[str]

    amount_amount: Optional[float]
    amount_currency_symbol: Optional[str]
    amount_currency_code: Optional[str]

    unit_price_amount: Optional[float]
    unit_price_currency_symbol: Optional[str]
    unit_price_currency_code: Optional[str]

    customer_name: Optional[str]
    customer_address_receipient: Optional[str]

    created_at: Optional[str]
