import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email: str, candidate_name: str, jobs_with_scores: list):
    from_email = os.getenv("SMTP_FROM")
    password = os.getenv("SMTP_PASSWORD")
    smtp_server = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    subject = "Top Job Matches for You"

    # Create message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    html = f"<h2>Hello {candidate_name},</h2>"
    html += "<p>Here are your top job matches:</p><ul>"
    for job, score in jobs_with_scores:
        html += f"<li><b>{job.title}</b> — Score: {score}</li>"
    html += "</ul><p>Good luck!</p>"

    msg.attach(MIMEText(html, 'html'))

    # Send email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
