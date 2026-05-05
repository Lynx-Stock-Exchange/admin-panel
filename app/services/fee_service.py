import httpx

from app.core.config import settings
from app.core.exceptions import AppException
from app.dtos.fee import FeeRateUpdateRequest

_STUB_ORDERS: list[dict] = []


class FeeService:
    def __init__(self):
        self._stub_fee_rate: float = 0.001

    def _headers(self) -> dict:
        return {"X-Admin-Token": settings.exchange_admin_token}

    def _handle_response(self, response: httpx.Response) -> dict | list:
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                body = e.response.json()
                error = body.get("error", {})
                raise AppException(
                    code=error.get("code", "EXCHANGE_ERROR"),
                    message=error.get("message", "Exchange returned an error."),
                    status_code=e.response.status_code,
                    details=error.get("details", {}),
                )
            except (ValueError, KeyError):
                raise AppException(
                    code="EXCHANGE_ERROR",
                    message=f"Exchange returned status {e.response.status_code}.",
                    status_code=502,
                )
        except httpx.RequestError:
            raise AppException(
                code="EXCHANGE_UNREACHABLE",
                message="Could not reach the exchange. Is it running?",
                status_code=503,
            )

    def get_fee_rate(self) -> dict:
        if settings.use_stubs:
            return {"rate": self._stub_fee_rate, "message": "Current exchange fee rate."}
        with httpx.Client() as client:
            response = client.get(
                f"{settings.exchange_base_url}/market/status",
                headers=self._headers(),
            )
            data = self._handle_response(response)
            return {"rate": data.get("fee_rate", 0.001), "message": "Current exchange fee rate."}

    def update_fee_rate(self, req: FeeRateUpdateRequest) -> dict:
        if settings.use_stubs:
            self._stub_fee_rate = req.rate
            return {"rate": self._stub_fee_rate, "message": f"Fee rate updated to {req.rate}."}
        with httpx.Client() as client:
            response = client.put(
                f"{settings.exchange_base_url}/admin/fees",
                headers=self._headers(),
                json={"rate": req.rate},
            )
            data = self._handle_response(response)
            return {"rate": data.get("rate", req.rate), "message": f"Fee rate updated to {req.rate}."}

    def get_revenue(self) -> dict:
        if settings.use_stubs:
            filled = [o for o in _STUB_ORDERS if o["status"] == "FILLED"]
            total = round(sum(o["exchange_fee"] for o in filled), 4)
            return {
                "fee_rate": self._stub_fee_rate,
                "total_revenue": total,
                "filled_order_count": len(filled),
                "orders": filled,
            }
        with httpx.Client() as client:
            response = client.get(
                f"{settings.exchange_base_url}/admin/orders",
                headers=self._headers(),
                params={"status": "FILLED", "page_size": 1000},
            )
            data = self._handle_response(response)
            orders = data if isinstance(data, list) else data.get("orders", [])
            filled = [o for o in orders if o.get("status") == "FILLED"]
            total = round(sum(o.get("exchange_fee", 0) for o in filled), 4)
            fee_info = self.get_fee_rate()
            return {
                "fee_rate": fee_info["rate"],
                "total_revenue": total,
                "filled_order_count": len(filled),
                "orders": filled,
            }


fee_service = FeeService()