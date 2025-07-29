from mmragsdk._requests.factory import  get_request
from mmragsdk import URL
from dotenv import load_dotenv
import os
from unittest.mock import ANY


TEST_API = "1234567890"
TEST_INPUT = 'user123'


def test_get_chat_request():
  request = get_request('chat', TEST_API, TEST_INPUT)

  assert request.url == URL + '/chat'
  assert request.method == "POST"
  assert request.headers == {"Content-Type": "application/json", "Authorization": "Bearer " + TEST_API}
  assert request.json == {"query": TEST_INPUT}

def test_get_search_request():
  request = get_request('search', TEST_API, TEST_INPUT)

  assert request.url == URL + '/search'
  assert request.method == "POST"
  assert request.headers == {"Content-Type": "application/json", "Authorization": "Bearer " + TEST_API}
  assert request.json == {"query": TEST_INPUT}


def test_get_upload_request():
  test_path = 'test.txt'
  with open(test_path, 'w') as f:
    f.write('test')

  request = get_request('upload', TEST_API, test_path)

  assert request.url == URL + '/upload-file'
  assert request.method == "POST"
  assert request.headers == {"Authorization": "Bearer " + TEST_API}
  assert request.files == {"file": (test_path, ANY, "multipart/form-data")}


def test_get_clean_request():
  request = get_request('clean', TEST_API, TEST_INPUT)

  assert request.url == URL + '/cleanUp'
  assert request.method == "POST"
  assert request.headers == {"Content-Type": "application/json", "Authorization": "Bearer " + TEST_API}
  assert request.json == {}
