import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Email:

    def __init__(self, gmailUsername, gmailPassword):
        self.gmailUsername = gmailUsername
        self.gmailPassword = gmailPassword
        pass

    def send(self, emailTo, emailFrom, subject, message):
        print("Attempting to email to {}, from {}, subject '{}' with message: {}".format(emailTo, emailFrom, subject, message))
        try:
            #server = smtplib.SMTP('smtp.gmail.com:587')
            #starttls = server.starttls()
            #login = server.login(self.gmailUsername, self.gmailPassword)
            garageMessage = MIMEMultipart()
            garageMessage['Subject'] = "GARAGE: {}".format(subject)
            garageMessage['From'] = emailFrom
            garageMessage['To'] = emailTo
            #sendit = server.sendmail(emailFrom, emailTo, garageMessage.as_string())
            #server.quit()
            print("Sent {}".format(garageMessage))
        except:
            print("Failed sending message")
            pass        

