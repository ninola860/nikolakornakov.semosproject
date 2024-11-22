import unittest
from app import app, db, UserInfo, UserSpending, HighSpenders
from flask import Flask

class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        # Use in-memory database for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.app = app.test_client()
        # Create all tables in the in-memory database
        with app.app_context():
            db.create_all()
            db.session.query(UserInfo).delete()  # Clear UserInfo table
            db.session.query(UserSpending).delete()  # Clear UserSpending table
            db.session.commit()  # Commit the changes to the database

    def tearDown(self):
        # Drop all tables after each test to ensure clean state
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_total_spent_user(self):
        with app.app_context():
            # Setup test data with unique user_id
            user = UserInfo(user_id=1515, name="Pece Peceski", email="pecepeceski@example.com", age=25)
            db.session.add(user)
            db.session.commit()
            spending = UserSpending(user_id=1515, money_spent=150.00, year=2024)
            db.session.add(spending)
            db.session.commit()

        # Test the total spent API
        response = self.app.get('/total_spent/1515')  # Use self.app instead of self.client
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data['user_id'], 1515)
        self.assertEqual(json_data['total_spent'], 150.00)

    def test_average_spending_by_age(self):
        with app.app_context():
            # Setup test data with unique user_id values
            user1 = UserInfo(user_id=1515, name="Pece Peceski", email="pecepeceski@example.com", age=25)
            user2 = UserInfo(user_id=2525, name="Jane Janeski", email="janejaneski@example.com", age=30)
            user3 = UserInfo(user_id=3535, name="Ace Aceski", email="aceaceski@example.com", age=35)

            spending1 = UserSpending(user_id=1515, money_spent=150.00, year=2024)
            spending2 = UserSpending(user_id=2525, money_spent=250.00, year=2024)
            spending3 = UserSpending(user_id=3535, money_spent=350.00, year=2024)

            db.session.add(user1)
            db.session.add(user2)
            db.session.add(user3)
            db.session.add(spending1)
            db.session.add(spending2)
            db.session.add(spending3)
            db.session.commit()

        # Test the average spending API
        response = self.app.get('/average_spending_by_age')  # Use self.app instead of self.client
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()

        # Check if the averages are calculated correctly
        self.assertEqual(json_data["18-24"], 0)
        self.assertGreater(json_data["25-30"], 0)
        self.assertGreater(json_data["31-36"], 0)
        self.assertEqual(json_data["37-47"], 0)
        self.assertEqual(json_data[">47"], 0)

    def test_write_high_spending_user(self):
        # Test creating or updating high spending user
        response = self.app.post('/write_high_spending_user', data={  # Use self.app instead of self.client
            'user_id': 102030,  # Use a unique user_id for each test
            'total_spending': 100.00
        })
        self.assertEqual(response.status_code, 201)  # Check for successful creation

        json_data = response.get_json()
        self.assertEqual(json_data['user']['user_id'], 102030)
        self.assertEqual(json_data['user']['total_spending'], 100.00)


if __name__ == '__main__':
    unittest.main()


