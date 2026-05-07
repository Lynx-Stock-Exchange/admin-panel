import httpx

from app.core.config import settings
from app.core.exceptions import AppException
from app.dtos.option import OptionCreateRequest


class OptionService:
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


    def list_options(self) -> list[dict]:
        with httpx.Client() as client:
            response = client.get(
                f"{settings.exchange_base_url}/admin/options",
                headers=self._headers(),
            )
            return self._handle_response(response)

    def get_total(self) -> dict:
        return {"count": len(self.list_options())}

    def create_option(self, req: OptionCreateRequest) -> dict:
        with httpx.Client() as client:
            response = client.post(
                f"{settings.exchange_base_url}/admin/options",
                headers=self._headers(),
                json=req.model_dump(mode="json"),
            )
            return self._handle_response(response)


option_service = OptionService()