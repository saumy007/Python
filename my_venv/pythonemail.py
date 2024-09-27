import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration
sender_email = "saumyss0@gmail.com"  # Replace with your email
receiver_email = "saumysharma007@gmail.com"  # Replace with recipient email
password = "pflc fpgu jkxh cvpn"  # Replace with your email password

# Create message
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = "Subject of your email this is subject" 

# Add body to email
body = "Content of your email this is content if thwe maIL"
message.attach(MIMEText(body, "plain"))

# SMTP server configuration
smtp_server = "smtp.gmail.com"
smtp_port = 587

# Start the SMTP session
server = smtplib.SMTP(smtp_server, smtp_port)
server.starttls()

# Login to the SMTP server
server.login(sender_email, password)

# Send email
server.sendmail(sender_email, receiver_email, message.as_string())

# Quit SMTP session
server.quit()

print("Email sent successfully!")