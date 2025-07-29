from pydantic import BaseModel


class Request(BaseModel):
  url: str


class SearchRequest(Request):
  pass


class UploadRequest(Request):
  pass


class ChatRequest(Request):
  pass


class CleanRequest(Request):
  pass
