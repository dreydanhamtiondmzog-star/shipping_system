from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from app.schemas import ShipmentRequest, ShipmentResult


@dataclass
class CarrierConfig:
    carrier_name: str
    api_key: str


class CarrierGateway:
    """A lightweight abstraction for US local carrier APIs.

    Replace `create_shipment` with real HTTP requests when integrating with
    USPS/UPS/FedEx or 3PL aggregators such as ShipEngine/EasyPost.
    """

    def __init__(self, config: CarrierConfig):
        self.config = config

    def create_shipment(self, shipment: ShipmentRequest) -> ShipmentResult:
        digest = sha256(f"{shipment.order_id}:{self.config.carrier_name}".encode()).hexdigest()
        tracking_number = digest[:12].upper()
        label_id = f"LBL-{digest[12:20].upper()}"
        return ShipmentResult(
            order_id=shipment.order_id,
            carrier=self.config.carrier_name,
            tracking_number=tracking_number,
            label_id=label_id,
            status="created",
        )
