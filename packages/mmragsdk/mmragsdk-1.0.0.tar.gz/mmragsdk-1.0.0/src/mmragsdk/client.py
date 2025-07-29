import os
from dotenv import load_dotenv

from pydantic import BaseModel
from mmragsdk._requests import factory, send
from requests import Response


load_dotenv()


class Client(BaseModel):
  token: str

  def chat(self, prompt: str) -> Response:
    if len(prompt) == 0:
      raise ValueError(
        f"Cannot chat with an empty query: {prompt}"
      )
    request = factory.get_request(self.chat.__name__, self.token, prompt)
    return send(request)

  def search(self, query: str) -> Response:
    if len(query) == 0:
      raise ValueError(
        f"Cannot search with an empty query: {query}"
      )

    request = factory.get_request(self.search.__name__, self.token, query)
    return send(request)

  def upload(self, file_path: str) -> Response:
    if not os.path.exists(file_path):
      raise FileNotFoundError(
        f"Unable to locate the file {file_path} on the system, please check for misspellings"
      )
    request = factory.get_request(self.upload.__name__, self.token, file_path)
    return send(request)

  def clean(self) -> Response:
    request = factory.get_request(self.clean.__name__, self.token, '')
    return send(request)


if __name__ == "__main__":
  client = Client(
    token=os.getenv("TOKEN"),
  )

  # response = client.chat(prompt="What is your name?")
  # print(response.json())
  #
  # with open("test.txt", "w") as f:
  #   f.write('this is a test')
  #
  # res = client.upload("test.txt")
  # print(res.json())
  #
  # res = client.search("is this a test")
  # print(res.json())

  res = client.clean()
  print(res)




