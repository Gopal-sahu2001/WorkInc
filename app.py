from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
import stripe
import os

app = Flask(__name__)

# Initialize MongoDB & Stripe Sandbox
# (Using os.environ makes your code secure and ready for cloud deployment later!)
MONGO_URI = os.environ.get("MONGO_URI")
STRIPE_KEY = os.environ.get("STRIPE_SECRET_KEY")

client = MongoClient(MONGO_URI)
db = client['workinc_db']
stripe.api_key = STRIPE_KEY

@app.route('/')
def home():
    # Looks inside the /templates folder for your landing page
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_email = data.get('email')
    user_name = data.get('name')
    
    users_collection = db.users
    existing_user = users_collection.find_one({"email": user_email})
    
    if existing_user:
        return jsonify({"message": f"Welcome back, {existing_user['name']}! (Account already exists)"}), 200
    else:
        # Create Stripe Customer dynamically inside Stripe Sandbox
        stripe_customer = stripe.Customer.create(
            email=user_email,
            name=user_name
        )
        
        # Save everything into MongoDB
        new_user = {
            "name": user_name,
            "email": user_email,
            "stripe_customer_id": stripe_customer.id
        }
        users_collection.insert_one(new_user)
        return jsonify({"message": f"Account created for {user_name}! Stripe ID saved."}), 201

if __name__ == '__main__':
    app.run(debug=True)
