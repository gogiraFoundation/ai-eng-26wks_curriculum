# src/schemas/invoice.py
# Invoice extract schema: Pydantic contract for LLM / API payloads.

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Currency = Literal["USD", "EUR", "GBP"]


class LineItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str = Field(..., min_length=1, description="Line item description")
    quantity: int = Field(..., gt=0, description="Quantity purchased")
    unit_price: Decimal = Field(..., gt=0, description="Price per unit")
    total: Decimal = Field(..., gt=0, description="Line total (quantity * unit_price)")

    @model_validator(mode="after")
    def total_matches_quantity_and_price(self) -> LineItem:
        expected = (self.quantity * self.unit_price).quantize(Decimal("0.01"))
        actual = self.total.quantize(Decimal("0.01"))
        if actual != expected:
            raise ValueError(
                f"line total {self.total} != quantity * unit_price ({expected})"
            )
        return self


class Invoice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    invoice_id: str = Field(..., min_length=1, description="Unique invoice identifier")
    invoice_date: date = Field(..., description="Invoice date (ISO date)")
    vendor: str = Field(..., min_length=1, description="Vendor / supplier name")
    currency: Currency = Field(..., description="ISO currency code")
    total: Decimal = Field(..., gt=0, description="Invoice grand total")
    line_items: list[LineItem] = Field(..., min_length=1, description="Invoice lines")

    @field_validator("total", "line_items", mode="before")
    @classmethod
    def _passthrough(cls, value: object) -> object:
        return value

    @model_validator(mode="after")
    def total_matches_line_items(self) -> Invoice:
        lines_sum = sum(
            (item.total for item in self.line_items),
            start=Decimal("0"),
        ).quantize(Decimal("0.01"))
        grand = self.total.quantize(Decimal("0.01"))
        if grand != lines_sum:
            raise ValueError(f"invoice total {self.total} != sum(line_items) ({lines_sum})")
        return self


def main() -> None:
    invoice = Invoice(
        invoice_id="INV-1001",
        invoice_date=date.today(),
        vendor="Acme Inc.",
        currency="USD",
        total=Decimal("100.00"),
        line_items=[
            LineItem(
                description="Product A",
                quantity=1,
                unit_price=Decimal("100.00"),
                total=Decimal("100.00"),
            )
        ],
    )
    print(invoice.model_dump_json(indent=2))


if __name__ == "__main__":
    main()