from pathlib import Path
import json

root = Path("tests/week02/fixtures")
(root / "invoices").mkdir(parents=True, exist_ok=True)
(root / "recorded").mkdir(parents=True, exist_ok=True)
(root / "expected").mkdir(parents=True, exist_ok=True)

cases = [
  {
    "id": "02",
    "quirk": "EUR single line",
    "text": "INVOICE #INV-1002\nIssued 2026-01-05\nFrom: Berlin Supplies GmbH\nEUR\nWidgets x2 @ 12.50 = 25.00\nTOTAL 25.00",
    "data": {
      "invoice_id": "INV-1002", "invoice_date": "2026-01-05",
      "vendor": "Berlin Supplies GmbH", "currency": "EUR", "total": "25.00",
      "line_items": [{"description": "Widgets", "quantity": 2, "unit_price": "12.50", "total": "25.00"}],
    },
  },
  {
    "id": "03",
    "quirk": "GBP multi-line",
    "text": "Invoice INV-1003 | 2026-02-14 | Vendor: Thames Office Ltd | GBP\nPaper A4 x10 @ 3.00 = 30.00\nToner x1 @ 45.00 = 45.00\nGrand total: 75.00",
    "data": {
      "invoice_id": "INV-1003", "invoice_date": "2026-02-14",
      "vendor": "Thames Office Ltd", "currency": "GBP", "total": "75.00",
      "line_items": [
        {"description": "Paper A4", "quantity": 10, "unit_price": "3.00", "total": "30.00"},
        {"description": "Toner", "quantity": 1, "unit_price": "45.00", "total": "45.00"},
      ],
    },
  },
  {
    "id": "04",
    "quirk": "messy spacing / USD",
    "text": "inv: INV-1004\ndate:2026-03-01\nvendor:  CloudNine SaaS\ncurrency:USD\nitem Seat licence | qty 5 | unit 9.99 | line 49.95\ntotal=49.95",
    "data": {
      "invoice_id": "INV-1004", "invoice_date": "2026-03-01",
      "vendor": "CloudNine SaaS", "currency": "USD", "total": "49.95",
      "line_items": [{"description": "Seat licence", "quantity": 5, "unit_price": "9.99", "total": "49.95"}],
    },
  },
  {
    "id": "05",
    "quirk": "EUR hospitality",
    "text": "Facture INV-1005\nDate: 2026-03-20\nFournisseur: Cafe Lumiere\nDevise: EUR\nCafe x3 @ 4.00 = 12.00\nTotal: 12.00",
    "data": {
      "invoice_id": "INV-1005", "invoice_date": "2026-03-20",
      "vendor": "Cafe Lumiere", "currency": "EUR", "total": "12.00",
      "line_items": [{"description": "Cafe", "quantity": 3, "unit_price": "4.00", "total": "12.00"}],
    },
  },
  {
    "id": "06",
    "quirk": "GBP consulting hours",
    "text": "INV-1006\n2026-04-02\nNordic Consulting LLP\nGBP\nAdvisory hours x8 @ 120.00 = 960.00\nTotal due 960.00",
    "data": {
      "invoice_id": "INV-1006", "invoice_date": "2026-04-02",
      "vendor": "Nordic Consulting LLP", "currency": "GBP", "total": "960.00",
      "line_items": [{"description": "Advisory hours", "quantity": 8, "unit_price": "120.00", "total": "960.00"}],
    },
  },
  {
    "id": "07",
    "quirk": "USD three lines",
    "text": "Invoice INV-1007 dated 2026-04-18 from Harbor Hardware (USD).\nNails x100 @ 0.05 = 5.00\nHammer x1 @ 15.00 = 15.00\nTape x2 @ 2.50 = 5.00\nTOTAL 25.00",
    "data": {
      "invoice_id": "INV-1007", "invoice_date": "2026-04-18",
      "vendor": "Harbor Hardware", "currency": "USD", "total": "25.00",
      "line_items": [
        {"description": "Nails", "quantity": 100, "unit_price": "0.05", "total": "5.00"},
        {"description": "Hammer", "quantity": 1, "unit_price": "15.00", "total": "15.00"},
        {"description": "Tape", "quantity": 2, "unit_price": "2.50", "total": "5.00"},
      ],
    },
  },
  {
    "id": "08",
    "quirk": "EUR print run",
    "text": "INV-1008 / 2026-05-09 / Vendor Atlas Print / EUR\nBrochures x50 @ 0.40 = 20.00\nTotal EUR 20.00",
    "data": {
      "invoice_id": "INV-1008", "invoice_date": "2026-05-09",
      "vendor": "Atlas Print", "currency": "EUR", "total": "20.00",
      "line_items": [{"description": "Brochures", "quantity": 50, "unit_price": "0.40", "total": "20.00"}],
    },
  },
  {
    "id": "09",
    "quirk": "GBP noisy header",
    "text": "*** TAX INVOICE ***\nNo. INV-1009\nInvoice Date: 2026-05-30\nBill From: Meadow Farm Organics\nCurrency Code: GBP\nEggs (box) x4 @ 3.25 = 13.00\nAmount Payable: 13.00",
    "data": {
      "invoice_id": "INV-1009", "invoice_date": "2026-05-30",
      "vendor": "Meadow Farm Organics", "currency": "GBP", "total": "13.00",
      "line_items": [{"description": "Eggs (box)", "quantity": 4, "unit_price": "3.25", "total": "13.00"}],
    },
  },
  {
    "id": "10",
    "quirk": "USD freight",
    "text": "INV-1010\n2026-06-11\nPacific Freight Co\nUSD\nShipping lane A x1 @ 220.00 = 220.00\nTotal: 220.00",
    "data": {
      "invoice_id": "INV-1010", "invoice_date": "2026-06-11",
      "vendor": "Pacific Freight Co", "currency": "USD", "total": "220.00",
      "line_items": [{"description": "Shipping lane A", "quantity": 1, "unit_price": "220.00", "total": "220.00"}],
    },
  },
  {
    "id": "11",
    "quirk": "EUR two services",
    "text": "Invoice INV-1011\nDate 2026-07-01\nVendor: SoftServe EU\nCurrency EUR\nSupport plan x1 @ 80.00 = 80.00\nOnboarding x1 @ 150.00 = 150.00\nTotal 230.00",
    "data": {
      "invoice_id": "INV-1011", "invoice_date": "2026-07-01",
      "vendor": "SoftServe EU", "currency": "EUR", "total": "230.00",
      "line_items": [
        {"description": "Support plan", "quantity": 1, "unit_price": "80.00", "total": "80.00"},
        {"description": "Onboarding", "quantity": 1, "unit_price": "150.00", "total": "150.00"},
      ],
    },
  },
  {
    "id": "12",
    "quirk": "GBP lowercase currency word",
    "text": "inv-1012\n2026-07-22\nvendor: Bright Lamps UK\npound sterling (GBP)\nLamp shade x2 @ 18.00 = 36.00\ntotal 36.00",
    "data": {
      "invoice_id": "INV-1012", "invoice_date": "2026-07-22",
      "vendor": "Bright Lamps UK", "currency": "GBP", "total": "36.00",
      "line_items": [{"description": "Lamp shade", "quantity": 2, "unit_price": "18.00", "total": "36.00"}],
    },
  },
  {
    "id": "13",
    "quirk": "USD high quantity",
    "text": "INV-1013 | 2026-08-08 | BulkPack Inc | USD\nZip ties x1000 @ 0.02 = 20.00\nTotal 20.00",
    "data": {
      "invoice_id": "INV-1013", "invoice_date": "2026-08-08",
      "vendor": "BulkPack Inc", "currency": "USD", "total": "20.00",
      "line_items": [{"description": "Zip ties", "quantity": 1000, "unit_price": "0.02", "total": "20.00"}],
    },
  },
  {
    "id": "14",
    "quirk": "EUR vendor",
    "text": "INV-1014\n2026-09-15\nVendor: Zurich Optics AG\nEUR\nLens kit x1 @ 399.00 = 399.00\nTotal: 399.00",
    "data": {
      "invoice_id": "INV-1014", "invoice_date": "2026-09-15",
      "vendor": "Zurich Optics AG", "currency": "EUR", "total": "399.00",
      "line_items": [{"description": "Lens kit", "quantity": 1, "unit_price": "399.00", "total": "399.00"}],
    },
  },
  {
    "id": "15",
    "quirk": "GBP year-end",
    "text": "Invoice INV-1015\nDate: 2026-12-31\nFrom: YearEnd Audit Partners\nCurrency: GBP\nYear-end review x1 @ 1500.00 = 1500.00\nTotal due: 1500.00",
    "data": {
      "invoice_id": "INV-1015", "invoice_date": "2026-12-31",
      "vendor": "YearEnd Audit Partners", "currency": "GBP", "total": "1500.00",
      "line_items": [{"description": "Year-end review", "quantity": 1, "unit_price": "1500.00", "total": "1500.00"}],
    },
  },
]

for c in cases:
    cid = c["id"]
    (root / "invoices" / f"{cid}.txt").write_text(c["text"] + "\n", encoding="utf-8")
    payload = json.dumps(c["data"], indent=2) + "\n"
    (root / "recorded" / f"{cid}.json").write_text(payload, encoding="utf-8")
    (root / "expected" / f"{cid}.json").write_text(payload, encoding="utf-8")
    print(f"wrote {cid} ({c['quirk']})")
print("done")