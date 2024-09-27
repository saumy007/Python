cred = credentials.Certificate('/content/drive/MyDrive/MRDev/employee-analytics-test-firebase-adminsdk-vovjb-5efb8c260a.json')
firebase_admin.initialize_app(cred, {'databaseURL': 'https://employee-analytics-test-default-rtdb.firebaseio.com/'})


# 2. Get a reference to the desired database path
ref = db.reference('/Saumy/online')

def track_data_changes(ref):  
  previous_data = None
  while True:
    data1 = ref.get()
    if data1.exists():
      if previous_data is not None and data.val() != previous_data:
        print(f"Change detected! New data: {data1.val()}")
        send_email("saumyss0@gmail.com","saumysharma007@gmail.com","pflc fpgu jkxh cvpn","Subject of your email this is subject","Content of your email this is content if thwe maIL",data1)

      previous_data = data1.val()
    else:
      print("Data does not exist at the specified path.",data1)
    

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(sender_email, receiver_email, password, subject, body,data):
    # Create message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    
    # Add body to email
    message.attach(MIMEText(body, "plain"))

    # SMTP server configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    try:
        # Start the SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        # Login to the SMTP server
        server.login(sender_email, password)

        # Send email
        server.sendmail(sender_email, receiver_email, message.as_string(),data)

        print("Email sent successfully!", data)

    except Exception as e:
        print("An error occurred:", e)

    finally:
        # Quit SMTP session
        server.quit()


