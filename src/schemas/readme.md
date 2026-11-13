```text
InvoiceExtract
  invoice_id: str
  invoice_date: date   # ISO string in JSON
  vendor: str
  total: Decimal       # or constrained number
  currency: enum       # e.g. GBP, USD, EUR
  line_items: list[{ description, quantity, unit_price }]
```