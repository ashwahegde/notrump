import smtplib
from email.mime.text import MIMEText

from flask import current_app

def send_text_email(to_address, subject, message_body, from_address = None):
    try:
        if not from_address:
            from_address = current_app.config["smtp_sender_address"]
        if not to_address:
            message = prrq_status_response(False, "to_address not provided.")
            return message
        if isinstance(to_address, str):
            to_address = [to_address]
        current_app.logger.info(f"sending mail to: {to_address}")
        msg = MIMEText(message_body,'plain')
        msg['From'] = from_address
        msg['To'] = ", ".join(to_address)
        msg['Subject'] = subject
        send_msg = msg.as_string()
    except Exception as e:
        current_app.logger.info("Error formatting inputs for the mail.")
        return prrq_status_response(False, "Mail unsuccessful.")
    try:
        s = smtplib.SMTP(current_app.config["smtp_server_ip"])#,port=current_app.config["smtp_server_port"])
        s.starttls()
        s.login(current_app.config["smtp_sender_address"], current_app.config["password"])
        s.sendmail(from_address, to_address, send_msg)
        s.quit()
        current_app.logger.info("Mail has been sent Successfully.")
        return True, "Mail has been sent Successfully."
    except Exception as e:
        current_app.logger.info(f"failed to send the mail. ERROR - {e}")
        return False, "Mail unsuccessful."
