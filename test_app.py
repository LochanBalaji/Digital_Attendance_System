# import unittest
# from app import app
import sys
import os
import unittest

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app 
class AttendanceAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    # Test Home Page
    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Students', response.data)

    # Test Marking Present
    def test_mark_attendance_present(self):
        response = self.client.get('/mark/1RV21CS001/present', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Students', response.data)

    # Test Marking Absent
    def test_mark_attendance_absent(self):
        response = self.client.get('/mark/1RV21CS001/absent', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Students', response.data)


    # Test Password Verification Failure
    def test_verify_password_failure(self):
        response = self.client.post('/verify', data={'password': 'Wrong'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Incorrect password', response.data)

    
    # Test Update Attendance API
    def test_update_attendance_api(self):
        response = self.client.post('/update_attendance', json=[
            {'usn': '1RV21CS001', 'status': 'present'},
            {'usn': '1RV21CS002', 'status': 'absent'}
        ])
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Updated attendance', response.data)

if __name__ == '__main__':
    unittest.main()
