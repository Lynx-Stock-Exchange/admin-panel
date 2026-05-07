import httpx

from app.core.config import settings
from app.core.exceptions import AppException
from app.dtos.fee import FeeRateUpdateRequest


class FeeService:
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
            except (ValueError, KeyError, AttributeError):
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
        with httpx.Client() as client:
            response = client.get(
                f"{settings.exchange_base_url}/admin/fees",
                headers=self._headers(),
            )
            data = self._handle_response(response)
            return {"rate": data.get("fee_rate", 0.001), "message": "Current exchange fee rate."}

    def update_fee_rate(self, req: FeeRateUpdateRequest) -> dict:
        with httpx.Client() as client:
            response = client.put(
                f"{settings.exchange_base_url}/admin/fees",
                headers=self._headers(),
                json={"rate": req.rate},
            )
            data = self._handle_response(response)
            return {"rate": data.get("fee_rate", req.rate), "message": f"Fee rate updated to {req.rate}."}

    def get_revenue(self) -> dict:
        with httpx.Client() as client:
            response = client.get(
                f"{settings.exchange_base_url}/admin/revenue",
                headers=self._headers(),
            )
            return self._handle_response(response)


fee_service = FeeService()