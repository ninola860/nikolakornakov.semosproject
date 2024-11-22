from flask import Flask, jsonify, json, request
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from statistics import mean
from sqlalchemy import func
import requests

load_dotenv()

app = Flask(__name__)
# db_path = os.path.join(os.path.dirname(__file__), 'users_vouchers.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)

class UserInfo(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)

class UserSpending(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    money_spent = db.Column(db.Float, nullable=False)
    year = db.Column(db.Integer, nullable=False)

class HighSpenders(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    total_spending = db.Column(db.Float, nullable=False)

@app.route("/total_spent/<int:user_id>", methods=["GET"])
def total_spent_user(user_id):
    total_spent = db.session.query(func.sum(UserSpending.money_spent)).filter_by(user_id=user_id).scalar()
    return jsonify({'user_id': user_id, 'total_spent': total_spent or 0})
      
@app.route("/average_spending_by_age", methods=["GET"])
def average_spending_by_age():
    age_groups = {
        "18-24": [],
        "25-30": [],
        "31-36": [],
        "37-47": [],
        ">47": []
        
    }
    users = db.session.query(UserInfo, UserSpending).join(UserSpending, UserInfo.user_id == UserSpending.user_id).all()

    for user_info, user_spending in users:
        if user_info.age < 18:
            continue
        elif 18 <= user_info.age <= 24:
            age_groups["18-24"].append(user_spending.money_spent)
        elif 25 <= user_info.age <= 30:
            age_groups["25-30"].append(user_spending.money_spent)
        elif 31 <= user_info.age <= 36:
            age_groups["31-36"].append(user_spending.money_spent)
        elif 37 <= user_info.age <= 47:
            age_groups["37-47"].append(user_spending.money_spent)
        else:
            age_groups[">47"].append(user_spending.money_spent)

    averages_by_age = {}
    for group, data in age_groups.items():
        if data:  # Only calculate the mean if there is data
            averages_by_age[group] = mean(data)
        else:
            averages_by_age[group] = 0  # Default value for empty groups

    return jsonify(averages_by_age)
         
@app.route("/send_form_data", methods=["GET"])
def form_data():
    return '''
    <form method="POST" action="/write_high_spending_user">
        <label for="user_id">Enter the user id:</label>
        <input type="number" name="user_id" required /><br>
        
        <label for="total_spending">Enter the total spending:</label>
        <input type="number" step="0.01" name="total_spending" required /><br>
        
        <input type="submit" value="Submit"/>
    </form>
    '''

@app.route("/write_high_spending_user", methods=["POST"])           
def write_high_spending_user():
    user_id = int(request.form.get('user_id'))
    total_spending = float(request.form.get('total_spending'))

    existing_user = db.session.get(HighSpenders, user_id)
    try:
        if existing_user:
            existing_user.total_spending = total_spending
            user_data = {"user_id": existing_user.user_id, "total_spending": existing_user.total_spending}
            message = "Successfully updated High Spending User!"
            status_code = 200
        else:
            new_user = HighSpenders(user_id=user_id, total_spending=total_spending)
            db.session.add(new_user)
            user_data = {"user_id": new_user.user_id, "total_spending": new_user.total_spending}
            message = "Successfully created new High Spending User!"
            status_code = 201
        
        db.session.commit()
        return jsonify({"message": message, "user": user_data}), status_code
    
    except Exception as e:
        db.session.rollback()
        status_code = 500
        
        return jsonify({"error": "Failed to create or update high spending user", "details": str(e)}), status_code

if __name__ == '__main__':
    app.run(debug=True)






