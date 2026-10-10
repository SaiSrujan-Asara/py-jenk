import unittest
from app import app

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_status_code(self):
        # Sends a GET request to '/' and checks for a 200 OK status
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_home_data(self):
        # Checks if the response contains the correct text
        response = self.app.get('/')
        self.assertIn(b"Hello from Jenkins and Flask!", response.data)

if __name__ == '__main__':
    unittest.main()
