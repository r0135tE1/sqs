from pydantic import BaseModel


class FlagResponse(BaseModel):
    country_code: str
    country_name: str
    flag_url: str
    options: list[str]
