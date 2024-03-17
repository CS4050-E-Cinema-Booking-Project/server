import smtplib
from email.mime.text import MIMEText

def send_email(subject, body, recipients):
    sender = "fossil.flicks.noreply@gmail.com"
    password = "wlee rfgo aeis krle"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())