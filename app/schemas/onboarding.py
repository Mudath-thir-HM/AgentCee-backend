from pydantic import BaseModel
from typing import Literal


class ConnectPlatformSchema(
    BaseModel
):
    platform: Literal[
        "instagram",
        "facebook",
        "x",
        "linkedin",
        "tiktok"
    ]

    account_name: str


class OnboardingResponseSchema(
    BaseModel
):
    message: str