from pydantic import BaseModel


class FlagResponse(BaseModel):
    country_code: str
    flag_url: str
    options: list[str]
