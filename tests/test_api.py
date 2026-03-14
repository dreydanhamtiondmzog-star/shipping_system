from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_bulk_upload_csv() -> None:
    csv_content = (
        "order_id,recipient_name,address1,city,state,zip_code,weight_lb\n"
        "SO-1001,Alex,1 Main St,Los Angeles,CA,90001,2.5\n"
    )
    response = client.post(
        "/shipments/bulk-upload",
        files={"file": ("orders.csv", csv_content, "text/csv")},
    )
    body = response.json()
    assert response.status_code == 200
    assert body["success_count"] == 1
    assert body["failed_count"] == 0
    assert body["results"][0]["order_id"] == "SO-1001"


def test_bulk_download_zip() -> None:
    response = client.get("/labels/bulk-download", params={"label_ids": ["LBL-A", "LBL-B"]})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert response.headers["content-disposition"] == "attachment; filename=shipping-labels.zip"
    assert response.content.startswith(b"PK")
