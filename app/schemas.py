from datetime import datetime
from pydantic import BaseModel, Field


class ShipmentRequest(BaseModel):
    order_id: str = Field(..., description="商家订单号")
    recipient_name: str
    recipient_phone: str | None = None
    address1: str
    address2: str | None = None
    city: str
    state: str
    zip_code: str
    weight_lb: float = Field(..., gt=0)
    service_level: str = Field(default="ground")


class ShipmentResult(BaseModel):
    order_id: str
    carrier: str
    tracking_number: str
    label_id: str
    status: str


class BulkUploadResponse(BaseModel):
    uploaded_at: datetime
    total_rows: int
    success_count: int
    failed_count: int
    results: list[ShipmentResult]
    errors: list[str]
