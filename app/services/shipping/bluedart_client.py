"""
Low-level Blue Dart REST API client (Unified API, apigateway.bluedart.com).

Confirmed from the integration spec provided for this project:
  - Auth:      GET  {BLUEDART_TOKEN_URL}
               headers: ClientID=<api key>, clientSecret=<api secret>
               response field: "JWTToken"
  - All other calls send header: JWTToken: <token>
  - Sandbox host: https://apigateway-sandbox.bluedart.com
  - Endpoints:
      POST /in/transportation/waybill/v1/GenerateWayBill
      POST /in/transportation/finder/v1/GetServicesforPincode
      POST /in/transportation/allproduct/v1/GetAllProductsAndSubProducts
      POST /in/transportation/transit/v1/GetDomesticTransitTimeForPinCodeandProduct
      GET  /in/transportation/tracking/v1/shipment?scan={AWB}
  - Profile object used in request bodies: {"LoginID", "LicenceKey", "Api_type"}

NOTE ON REQUEST BODY FIELD NAMES:
GetServicesforPincode uses {"pinCode", "profile"} and
GetDomesticTransitTimeForPinCodeandProduct uses
{"pPinCodeFrom", "pPinCodeTo", "pProductCode", "pSubProductCode", "pPudate",
"pPickupTime", "profile"} - confirmed against the Blue Dart documentation
supplied for this project. GetAllProductsAndSubProducts uses lowercase
"profile" as well. If the sandbox still returns a 4xx "invalid request"
error, the response body is preserved in BlueDartAPIError.response_body so
any remaining mismatch can be corrected here without touching any other
layer.
"""

import time
from typing import Any

import httpx

from app.core.config import settings


class BlueDartAuthError(Exception):
    pass


class BlueDartAPIError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: Any = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class BlueDartClient:

    _token: str | None = None
    _token_fetched_at: float = 0.0

    def __init__(self):
        self.token_url = settings.BLUEDART_TOKEN_URL
        self.base_url = settings.BLUEDART_API_BASE_URL.rstrip("/")
        self.api_key = settings.BLUEDART_API_KEY
        self.api_secret = settings.BLUEDART_API_SECRET
        self.ttl_seconds = settings.BLUEDART_TOKEN_TTL_MINUTES * 60

    @property
    def profile(self) -> dict:
        return {
            "LoginID": settings.BLUEDART_LOGIN_ID,
            "LicenceKey": settings.BLUEDART_LICENCE_KEY,
            "Api_type": settings.BLUEDART_API_TYPE,
        }

    async def _fetch_token(self) -> str:

        if not self.api_key or not self.api_secret:
            raise BlueDartAuthError(
                "BLUEDART_API_KEY / BLUEDART_API_SECRET are not configured in .env"
            )

        async with httpx.AsyncClient(timeout=30) as http:
            response = await http.get(
                self.token_url,
                headers={
                    "ClientID": self.api_key,
                    "clientSecret": self.api_secret,
                },
            )

        if response.status_code != 200:
            raise BlueDartAuthError(
                f"Blue Dart token request failed "
                f"({response.status_code}): {response.text}"
            )

        data = self._safe_json(response)
        token = data.get("JWTToken") if isinstance(data, dict) else None

        if not token:
            raise BlueDartAuthError(
                f"Blue Dart token response missing 'JWTToken' field: {data}"
            )

        BlueDartClient._token = token
        BlueDartClient._token_fetched_at = time.time()

        return token

    async def _get_token(self, force_refresh: bool = False) -> str:

        if (
            not force_refresh
            and BlueDartClient._token
            and (time.time() - BlueDartClient._token_fetched_at) < self.ttl_seconds
        ):
            return BlueDartClient._token

        return await self._fetch_token()

    async def _request(
        self,
        method: str,
        path: str,
        json_body: dict | None = None,
        params: dict | None = None,
    ) -> dict:

        token = await self._get_token()

        url = f"{self.base_url}{path}"

        async def call(jwt_token: str):
            async with httpx.AsyncClient(timeout=30) as http:
                return await http.request(
                    method,
                    url,
                    headers={"JWTToken": jwt_token},
                    json=json_body,
                    params=params,
                )

        response = await call(token)

        if response.status_code in (401, 403):
            token = await self._get_token(force_refresh=True)
            response = await call(token)

        if response.status_code >= 400:
            raise BlueDartAPIError(
                f"Blue Dart API call failed ({response.status_code}) for {path}",
                status_code=response.status_code,
                response_body=self._safe_json(response),
            )

        return self._safe_json(response)

    @staticmethod
    def _safe_json(response) -> Any:
        try:
            return response.json()
        except ValueError:
            return {"raw_text": response.text}

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    async def get_services_for_pincode(self, pincode: str) -> dict:
        return await self._request(
            "POST",
            "/in/transportation/finder/v1/GetServicesforPincode",
            json_body={
                "pinCode": pincode,
                "profile": self.profile,
            },
        )

    async def get_all_products_and_subproducts(self) -> dict:
        return await self._request(
            "POST",
            "/in/transportation/allproduct/v1/GetAllProductsAndSubProducts",
            json_body={"profile": self.profile},
        )

    async def get_domestic_transit_time(
        self,
        origin_pincode: str,
        destination_pincode: str,
        product_code: str,
        pickup_date: str,
        pickup_time: str,
        sub_product_code: str | None = None,
    ) -> dict:
        return await self._request(
            "POST",
            "/in/transportation/transit/v1/GetDomesticTransitTimeForPinCodeandProduct",
            json_body={
                "pPinCodeFrom": origin_pincode,
                "pPinCodeTo": destination_pincode,
                "pProductCode": product_code,
                "pSubProductCode": sub_product_code or "",
                "pPudate": pickup_date,
                "pPickupTime": pickup_time,
                "profile": self.profile,
            },
        )

    async def generate_waybill(self, payload: dict) -> dict:
        return await self._request(
            "POST",
            "/in/transportation/waybill/v1/GenerateWayBill",
            json_body=payload,
        )

    async def track_shipment(self, awb_number: str) -> dict:
        return await self._request(
            "GET",
            "/in/transportation/tracking/v1",
            params={
                "handler": "tnt",
                "action": "custawbquery",
                "loginid": settings.BLUEDART_TRACKING_LOGIN_ID,
                "awb": "awb",
                "numbers": awb_number,
                "format": "json",
                "lickey": settings.BLUEDART_TRACKING_LICENCE_KEY,
                "verno": settings.BLUEDART_TRACKING_VERSION,
                "scan": "1",
            },
        )
