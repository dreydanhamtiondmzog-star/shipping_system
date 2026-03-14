from datetime import datetime, timezone

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import Response

from app.schemas import BulkUploadResponse
from app.services.carriers import CarrierConfig, CarrierGateway
from app.services.files import build_labels_zip, parse_shipments_from_csv

app = FastAPI(title="Custom US Shipping Platform", version="0.1.0")
carrier = CarrierGateway(
    CarrierConfig(
        carrier_name="USPS",
        api_key="replace-with-real-secret",
    )
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/shipments/bulk-upload", response_model=BulkUploadResponse)
async def bulk_upload(file: UploadFile = File(...)) -> BulkUploadResponse:
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="当前示例仅支持 CSV 文件上传")

    raw = await file.read()
    shipments, errors = parse_shipments_from_csv(raw)

    results = [carrier.create_shipment(s) for s in shipments]
    return BulkUploadResponse(
        uploaded_at=datetime.now(timezone.utc),
        total_rows=len(shipments) + len(errors),
        success_count=len(results),
        failed_count=len(errors),
        results=results,
        errors=errors,
    )


@app.get("/labels/bulk-download")
def bulk_download_labels(label_ids: list[str] = Query(...)) -> Response:
    if not label_ids:
        raise HTTPException(status_code=400, detail="请至少提供一个 label_id")

    zip_data = build_labels_zip(label_ids)
    return Response(
        content=zip_data,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=shipping-labels.zip"},
    )
