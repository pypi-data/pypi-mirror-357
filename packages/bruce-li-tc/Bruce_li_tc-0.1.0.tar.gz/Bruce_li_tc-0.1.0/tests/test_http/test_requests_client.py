import unittest
from bruce_li_tc.http.requests_client import RequestsClient


class TestRequestsClient(unittest.TestCase):
    def test_get_request(self):
        client = RequestsClient()
        response = client.get('https://httpbin.org/get')

        self.assertEqual(response['status_code'], 200)
        self.assertIn('headers', response)
        self.assertIn('content', response)

    def test_post_request(self):
        client = RequestsClient()
        response = client.post('https://httpbin.org/post', data={'key': 'value'})

        self.assertEqual(response['status_code'], 200)
        self.assertIn('headers', response)
        self.assertIn('json', response)
        self.assertEqual(response['json']['form'], {'key': 'value'})