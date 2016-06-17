import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import time

class Email:

    def __init__(self, gmailUsername, gmailPassword):
        self.gmailUsername = gmailUsername
        self.gmailPassword = gmailPassword
        pass

    def send(self, recipients, subject, messageContent):
        logging.info("Attempting to email to {}, from {}, subject '{}' with messageContent: {}".format(recipients, self.gmailUsername, subject, messageContent))
        failure = None

        if not isinstance(recipients, (list, tuple)):
            recipients = [recipients]

        # Try to send the email.  If sending fails, retry 5 times before giving up
        for x in range(0, 5):
            if x is not 0:
                time.sleep(5) # Wait 5 seconds if this is a retry

            try:
                #server = smtplib.SMTP('smtp.gmail.com:587')
                #server.set_debuglevel(1)
                #server.ehlo()
                #starttls = server.starttls()
                #server.ehlo()
                #login = server.login(self.gmailUsername, self.gmailPassword)
                
                emailMessage = MIMEMultipart("alternative")
                emailMessage['Subject'] = "GARAGE: {}".format(subject)
                emailMessage['From'] = self.gmailUsername
                emailMessage['To'] = ", ".join(recipients)
                htmlMessagePart = MIMEText(messageContent, "html")
                emailMessage.attach(htmlMessagePart)
                #sendit = server.sendmail(emailFrom, emailTo, emailMessage.as_string())
                #server.quit()
                logging.info("Sent {}, {}, {}".format(emailMessage['Subject'], emailMessage['From'], emailMessage['To']))

                # Success: so return out of retry loop
                return
            except Exception as e:
                logging.warn("Failed on attempt {} of sending messageContent: {}, {}, {} Because: {}".format(x, subject, messageContent, recipients, e))
                failure = e

        raise failure

