#!/usr/bin/env python3

import smtplib, ssl
import secrets
import email 

# Construct message based on results of ILLiad update
# If any step failed, status should be failed. 
message=""
update_status = "UNKNOWN"
with open("im_output.txt", "r") as results:
    for row in results:
        if "FAILURE" in row:
           update_status = "FAILURE"
        else: 
           update_status = "SUCCESS"
        message += row
msg = email.message.EmailMessage()
msg['Subject'] = "Subject: ILLiad %s User Management - %s" % (secrets.environment, update_status) 
msg['From'] = secrets.sender
msg['To'] = secrets.recipients
msg.set_content(message)

# Use SSL for email but ignore bad host name error. 
context = ssl.create_default_context()
context.check_hostname = False  
server = smtplib.SMTP(secrets.smtp_server, 587)
server.starttls(context=context)
server.send_message(msg)
server.quit()


