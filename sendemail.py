import smtplib, ssl
import secrets

port = secrets.email_port  # For SSL
smtp_server = secrets.smtp_server
sender_email = secrets.sender_email
sender_password = secrets.sender_password
send_as = secrets.send_as
send_to = secrets.send_to # List Data Type, can contain single entry
# Create a secure SSL context
context = ssl.create_default_context()
server = smtplib.SMTP(smtp_server, port)
server.starttls(context=context)
server.login(sender_email, password)
log_file = secrets.log_file_location 
# Declares message, will be overwritten in following loop
message = """\
Subject: ILLiad User Management -
"""
# Need to find better way to check than loop through log, this is quick and dirty
for row in open(log_file,"r"):
    if "FAILURE" in row:
        message = """Subject: ILLiad Staging User Management - FAILURE

"""
    else:
        message = """Subject: ILLiad Staging User Management - SUCCESS

"""
for row in open(log_file,"r"):
        message += row
# Send email to each recipient, if singular List should have one entry
for recipient in send_to:
        server.sendmail(send_as, recipient, message)
