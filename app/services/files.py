from __future__ import annotations

import csv
import io
import zipfile
from typing import Iterable

from app.schemas import ShipmentRequest

REQUIRED_COLUMNS = {
    "order_id",
    "recipient_name",
    "address1",
    "city",
    "state",
    "zip_code",
    "weight_lb",
}


def parse_shipments_from_csv(raw: bytes) -> tuple[list[ShipmentRequest], list[str]]:
    decoded = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(decoded))
    if not reader.fieldnames:
        return [], ["CSV 文件缺少标题行"]

    missing = REQUIRED_COLUMNS - set(reader.fieldnames)
    if missing:
        return [], [f"缺少必填列: {', '.join(sorted(missing))}"]

    shipments: list[ShipmentRequest] = []
    errors: list[str] = []
    for idx, row in enumerate(reader, start=2):
        try:
            shipments.append(
                ShipmentRequest(
                    order_id=row["order_id"],
                    recipient_name=row["recipient_name"],
                    recipient_phone=row.get("recipient_phone") or None,
                    address1=row["address1"],
                    address2=row.get("address2") or None,
                    city=row["city"],
                    state=row["state"],
                    zip_code=row["zip_code"],
                    weight_lb=float(row["weight_lb"]),
                    service_level=row.get("service_level") or "ground",
                )
            )
        except Exception as exc:  # pydantic validation errors included
            errors.append(f"第 {idx} 行错误: {exc}")

    return shipments, errors


def build_labels_zip(label_ids: Iterable[str]) -> bytes:
    """Create a ZIP package for bulk PDF download.

    PDF content is intentionally minimal for demo purposes and should be replaced
    by real label binary returned from carrier APIs.
    """

    content = io.BytesIO()
    with zipfile.ZipFile(content, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for label_id in label_ids:
            pdf_data = (
                b"%PDF-1.4\n"
                b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n"
                b"2 0 obj<< /Type /Pages /Count 1 /Kids [3 0 R] >>endobj\n"
                b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] >>endobj\n"
                b"trailer<< /Root 1 0 R >>\n%%EOF"
            )
            zf.writestr(f"{label_id}.pdf", pdf_data)

    return content.getvalue()
