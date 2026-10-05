"""Synthetic XLSX fixture, authored independently of the reconciliation engine."""

from pathlib import Path

from openpyxl import Workbook

path = Path(__file__).resolve().parents[1] / "examples" / "target.xlsx"
book = Workbook()
sheet = book.active
sheet.title = "Export"
sheet.append(["Reference", "Currency", "Amount", "Date", "Status"])
for row in [
    ["00017", "EUR", "100.00", "2026-09-02", "booked"],
    ["INV-002", "EUR", "249.00", "2026-09-03", "booked"],
    ["INV-004", "EUR", "50.00", "2026-09-05", "booked"],
    ["INV-005", "EUR", "11.00", "2026-09-06", "booked"],
    ["BOUNDARY", "EUR", "9.00", "2026-09-30", "booked"],
    ["REFUND", "EUR", "-15.00", "2026-09-08", "booked"],
    ["PLN-01", "PLN", "121.00", "2026-09-09", "booked"],
    ["TARGET-ONLY", "EUR", "30.00", "2026-09-11", "booked"],
    ["BAD-DATE", "EUR", "7.00", "2026-09-10", "booked"],
    ["INV-006", "EUR", "80.00", "2026-09-07", "cancelled"],
    ["USD-01", "EUR", "0.00", "2026-08-31", "booked"],
]:
    sheet.append(row)
book.save(path)
print(path)
