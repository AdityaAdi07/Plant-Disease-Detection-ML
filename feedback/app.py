from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

app = Flask(__name__)

# MongoDB configuration
MONGO_URI = "mongodb+srv://sushmaaditya717:rdqdcaYTLY7p50za@adityaadi.vztbe.mongodb.net/mern_1_db"
DB_NAME = "mern_1_db"
COLLECTION_NAME = "users"

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "sushmaaditya717@gmail.com"
SENDER_PASSWORD = "adkyjtsjguuzqlmn"
RECEIVER_EMAIL = "sushmaaditya717@gmail.com"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if request.method == 'POST':
        feedback_data = {
            'plant_name_accuracy': request.form.get('plant_accuracy'),
            'disease_detection_accuracy': request.form.get('disease_accuracy'),
            'confidence_score': request.form.get('confidence_score'),
            'improvement_suggestions': request.form.get('improvements'),
            'timestamp': datetime.now()
        }
        
        # Save to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        collection.insert_one(feedback_data)
        
        # Send email
        send_email_notification(feedback_data)
        
        return redirect(url_for('thank_you'))

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

def send_email_notification(feedback_data):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = "New Feedback Submission"
    
    body = f"""
    New feedback received:
    
    Plant Name Accuracy: {feedback_data['plant_name_accuracy']}
    Disease Detection Accuracy: {feedback_data['disease_detection_accuracy']}
    Confidence Score: {feedback_data['confidence_score']}
    Improvement Suggestions: {feedback_data['improvement_suggestions']}
    Timestamp: {feedback_data['timestamp']}
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

if __name__ == '__main__':
    app.run(port=5050, debug=True)