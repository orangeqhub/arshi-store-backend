from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # Database
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Storage
    UPLOAD_DIR: str
    SITE_URL: str
    RAZORPAY_KEY_ID: str

    RAZORPAY_KEY_SECRET: str

    # Blue Dart - auth
    BLUEDART_API_KEY: str = ""
    BLUEDART_API_SECRET: str = ""
    BLUEDART_TOKEN_URL: str = (
        "https://apigateway.bluedart.com/in/transportation/token/v1/login"
    )
    BLUEDART_TOKEN_TTL_MINUTES: int = 600

    # Blue Dart - API host (sandbox by default)
    BLUEDART_API_BASE_URL: str = (
        "https://apigateway-sandbox.bluedart.com"
    )

    # Blue Dart - profile (used in request payloads)
    BLUEDART_LOGIN_ID: str = ""
    BLUEDART_LICENCE_KEY: str = ""
    BLUEDART_TRACKING_LOGIN_ID: str = ""
    BLUEDART_TRACKING_LICENCE_KEY: str = ""
    BLUEDART_TRACKING_VERSION: str = "1.3"
    BLUEDART_API_TYPE: str = "S"

    # Blue Dart - account-specific values (never guess, must be configured)
    BLUEDART_CUSTOMER_CODE: str = ""
    BLUEDART_ORIGIN_AREA: str = ""
    BLUEDART_PRODUCT_CODE: str = ""
    BLUEDART_SUB_PRODUCT_CODE: str = ""

    # Blue Dart - shipper / pickup address (this business's own address)
    BLUEDART_SHIPPER_NAME: str = ""
    BLUEDART_SHIPPER_ADDRESS1: str = ""
    BLUEDART_SHIPPER_ADDRESS2: str = ""
    BLUEDART_SHIPPER_CITY: str = ""
    BLUEDART_SHIPPER_STATE: str = ""
    BLUEDART_SHIPPER_PINCODE: str = ""
    BLUEDART_SHIPPER_PHONE: str = ""
    BLUEDART_SHIPPER_EMAIL: str = ""

    class Config:
        env_file = ".env"


settings = Settings()