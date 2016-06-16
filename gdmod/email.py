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

    def send(self, emailTo, subject, message):
        logging.info("Attempting to email to {}, from {}, subject '{}' with message: {}".format(emailTo, self.gmailUsername, subject, message))
        failure = None

        # Try to send the email.  If sending fails, retry 5 times before giving up
        for x in range(0, 5):
            if x is not 0:
                time.sleep(5) # Wait 5 seconds if this is a retry

            try:
                #server = smtplib.SMTP('smtp.gmail.com:587')
                #starttls = server.starttls()
                #login = server.login(self.gmailUsername, self.gmailPassword)
                garageMessage = MIMEMultipart()
                garageMessage['Subject'] = "GARAGE: {}".format(subject)
                garageMessage['From'] = self.gmailUsername
                garageMessage['To'] = emailTo
                #sendit = server.sendmail(emailFrom, emailTo, garageMessage.as_string())
                #server.quit()
                logging.info("Sent {}, {}, {}".format(garageMessage['Subject'], garageMessage['From'], garageMessage['To']))

                # Success: so return out of retry loop
                return
            except Exception as e:
                logging.warn("Failed on attempt {} of sending message: {}, {}, {} Because: {}".format(x, subject, message, emailTo, e))
                failure = e

        raise failure

