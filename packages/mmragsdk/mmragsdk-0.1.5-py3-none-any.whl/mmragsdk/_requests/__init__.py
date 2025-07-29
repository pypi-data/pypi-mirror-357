import requests
from requests import Request, Response


def send(req: Request) -> Response:
  session = requests.Session()
  prepared = session.prepare_request(req)
  response = session.send(prepared)

  return response