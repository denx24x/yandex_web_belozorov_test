import json
import requests
import unittest


class TestNews(unittest.TestCase):
    def test_add_news(self):
        payload = {'api_key': 'yes, i am admin', 'title': '123', 'content': '321'}
        res = requests.post('http://127.0.0.1:5000/api/news', headers={"Content-Type": "application/json"}, data=json.dumps(payload)).json()
        self.assertEqual({'success': 'OK'}, res)

    def test_add_news2(self):  # чтобы от отсутствия не падало
        payload = {'api_key': 'yes, i am admin', 'title': '123', 'content': '321'}
        res = requests.post('http://127.0.0.1:5000/api/news', headers={"Content-Type": "application/json"}, data=json.dumps(payload)).json()
        self.assertEqual({'success': 'OK'}, res)

    def test_no_api_key_add_news(self):
        payload = {'title': '123', 'content': '321'}
        res = requests.post('http://127.0.0.1:5000/api/news', headers={"Content-Type": "application/json"},
                            data=json.dumps(payload)).status_code
        self.assertEqual(400, res)

    def test_wrong_api_key_add_news(self):
        payload = {'api_key': '321', 'title': '123', 'content': '321'}
        res = requests.post('http://127.0.0.1:5000/api/news', headers={"Content-Type": "application/json"},
                            data=json.dumps(payload)).status_code
        self.assertEqual(400, res)

    def test_get_news(self):
        res = requests.get('http://127.0.0.1:5000/api/news', headers={"Content-Type": "application/json"})
        res.json()
        self.assertEqual(200, res.status_code)

    def test_put_news(self):
        payload = {'api_key': 'yes, i am admin', 'title': '123', 'content': '321', 'id': requests.get('http://127.0.0.1:5000/api/news', headers={"Content-Type": "application/json"}).json()['news'][0]['id']}
        res = requests.put('http://127.0.0.1:5000/api/news', headers={"Content-Type": "application/json"}, data=json.dumps(payload)).json()
        self.assertEqual({'success': 'OK'}, res)

    def test_no_api_key_put_news(self):
        payload = {'title': '123', 'content': '321', 'id':
            requests.get('http://127.0.0.1:5000/api/news', headers={"Content-Type": "application/json"}).json()['news'][0][
                'id']}
        res = requests.put('http://127.0.0.1:5000/api/news', headers={"Content-Type": "application/json"},
                           data=json.dumps(payload)).json()
        self.assertIn('api_key', res['message'])

    def test_wrong_api_key_put_news(self):
        payload = {'api_key': '321', 'title': '123', 'content': '321', 'id': requests.get('http://127.0.0.1:5000/api/news', headers={"Content-Type": "application/json"}).json()['news'][0]['id']}
        res = requests.put('http://127.0.0.1:5000/api/news', headers={"Content-Type": "application/json"}, data=json.dumps(payload)).json()
        self.assertEqual({'message': 'Wrong api_key'}, res)

    def test_delete_news(self):
        payload = {'api_key': 'yes, i am admin', 'title': '123', 'content': '321', 'id': requests.get('http://127.0.0.1:5000/api/news', headers={"Content-Type": "application/json"}).json()['news'][0]['id']}
        res = requests.delete('http://127.0.0.1:5000/api/news', headers={"Content-Type": "application/json"}, data=json.dumps(payload)).json()
        self.assertEqual({'success': 'OK'}, res)

    def test_no_api_key_delete_news(self):
        payload = {'title': '123', 'content': '321', 'id':
            requests.get('http://127.0.0.1:5000/api/news', headers={"Content-Type": "application/json"}).json()['news'][0][
                'id']}
        res = requests.delete('http://127.0.0.1:5000/api/news', headers={"Content-Type": "application/json"},
                           data=json.dumps(payload)).json()
        self.assertIn('api_key', res['message'])

    def test_wrong_api_key_delete_news(self):
        payload = {'api_key': '321', 'title': '123', 'content': '321', 'id': requests.get('http://127.0.0.1:5000/api/news', headers={"Content-Type": "application/json"}).json()['news'][0]['id']}
        res = requests.delete('http://127.0.0.1:5000/api/news', headers={"Content-Type": "application/json"}, data=json.dumps(payload)).json()
        self.assertEqual({'message': 'Wrong api_key'}, res)


class TestVote(unittest.TestCase):
    def test_vote(self):
        res = requests.post('http://127.0.0.1:5000/vote?val=1&id=1&type=mod&api_key=yes, i am admin')
        self.assertEqual(404, res.status_code)

    def test_wrong_api_key_vote(self):
        res = requests.post('http://127.0.0.1:5000/vote?val=1&id=1&type=news&api_key=321')
        self.assertEqual(400, res.status_code)


class TestMod(unittest.TestCase):
    def test_get_users(self):
        res = requests.get('http://127.0.0.1:5000/api/mod', headers={"Content-Type": "application/json"})
        res.json()
        self.assertEqual(200, res.status_code)

    def test_get_users2(self):
        res = requests.get('http://127.0.0.1:5000/api/mod?id=1', headers={"Content-Type": "application/json"})
        res.json()
        self.assertEqual(200, res.status_code)


class TestUser(unittest.TestCase):
    def test_get_users(self):
        res = requests.get('http://127.0.0.1:5000/api/users', headers={"Content-Type": "application/json"})
        res.json()
        res.json()
        self.assertEqual(200, res.status_code)

    def test_get_users2(self):
        res = requests.get('http://127.0.0.1:5000/api/users?id=1', headers={"Content-Type": "application/json"})
        res.json()
        self.assertEqual(200, res.status_code)


class TestMessage(unittest.TestCase):
    def test_vote(self):
        res = requests.post('http://127.0.0.1:5000/send_message?name=test&message=123&api_key=yes, i am admin')
        self.assertEqual(200, res.status_code)

    def test_wrong_api_key_vote(self):
        res = requests.post('http://127.0.0.1:5000/send_message?name=test&message=123&api_key=123')
        self.assertEqual(400, res.status_code)


if __name__ == '__main__':
    unittest.main()
