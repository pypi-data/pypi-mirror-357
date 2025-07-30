from pydantic import BaseModel


class Uploader(BaseModel):
    filename: str
    filetype: str
    expiration: int | None = None
