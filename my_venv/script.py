import firebase_admin
from firebase_admin import credentials, db
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from datetime import datetime, timedelta
import schedule
import time

# Initialize Firebase app
cred = credentials.Certificate('/content/drive/MyDrive/MR JSON/employee-analytics-test-firebase-adminsdk-vovjb-5efb8c260a.json')
firebase_admin.initialize_app(cred, {'databaseURL': 'https://employee-analytics-test-default-rtdb.firebaseio.com/'})

def send_email(sender_email, receiver_email, password, subject, body):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print("An error occurred:", e)

def sendMail():
    ref = db.reference("/")
    documents = ref.get()

    for key, data in documents.items():
        try:
            heartbeat_time_str = data.get("Heartbeat", None)
            if heartbeat_time_str:
                heartbeat_time = datetime.fromisoformat(heartbeat_time_str)

                url = "https://worldtimeapi.org/api/timezone/Asia/Kolkata"
                response = requests.get(url)

                if response.status_code == 200:
                    current_time_str = response.json()["datetime"]
                    current_time = datetime.fromisoformat(current_time_str)

                    time_diff = current_time - heartbeat_time

                    if time_diff > timedelta(minutes=3):
                        print(f"Key: {key}, Difference exceeded 10 minutes. BOOM!")
                        send_email("saumyss0@gmail.com","saagarbafna1963@gmail.com","pflc fpgu jkxh cvpn","Subject of your email this is subject",f"Content of your email this is content if thwe maIL \nData: {key}")
                        print("Email Sent")
                    else:
                        print(f"Key: {key}, Difference within 10 minutes.")
                else:
                    print("Failed to fetch current time from WorldTimeAPI.")
            else:
                print(f"No heartbeat data found for key: {key}")
        except Exception as e:
            print(f"Error processing key {key}: {e}")

# Schedule the job to run every 1 minute
schedule.every(1).minutes.do(sendMail)

# Run the scheduler in an infinite loop
while True:
    schedule.run_pending()
    time.sleep(1)