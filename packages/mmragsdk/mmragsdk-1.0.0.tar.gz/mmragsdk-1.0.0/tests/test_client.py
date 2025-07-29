from mmragsdk import Client
from dotenv import load_dotenv
import os

import pytest


load_dotenv()


RANDOM_PATH = 'random_path'
client = Client(token=os.getenv("TOKEN"))
REAL_PATH = 'test.txt'
with open(REAL_PATH, 'w') as f:
  f.write('test')


def test_missing_file_path_error():
  with pytest.raises(FileNotFoundError):
    client.upload(RANDOM_PATH)


def test_empty_search_query_raises():
  with pytest.raises(ValueError):
    client.search('')


def test_empty_chat_prompt_raises():
  with pytest.raises(ValueError):
    client.chat('')


def test_chat_success():
  response = client.chat("How are you?")

  assert response.status_code == 200


def test_search_success():
  response = client.search('test')

  assert response.status_code == 200


def test_upload_success():
  response = client.upload(REAL_PATH)

  assert response.status_code == 200


def test_clean_success():
  response = client.clean()
  assert response.status_code == 200


def test_invalid_token_chat_error():
  client.token = 'wrong token'
  response = client.chat('t')
  assert response.status_code == 403


def test_invalid_token_search_error():
  client.token = 'wrong token'
  response = client.search('t')
  assert response.status_code == 403


def test_invalid_token_upload_error():
  client.token = 'wrong token'
  response = client.chat('t')
  assert response.status_code == 403


def test_invalid_token_clean_error():
  client.token = 'wrong token'
  response = client.clean()
  assert response.status_code == 403