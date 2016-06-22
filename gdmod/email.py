import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import time
import os.path

class Email:

    def __init__(self, gmailUsername, gmailPassword, cssStyle=None):
        self.gmailUsername = gmailUsername
        self.gmailPassword = gmailPassword
        self.cssStyle = cssStyle
        pass

    def send(self, recipients, subject, messageContent, files=None):
        logging.info("Attempting to email to {}, from {}, subject '{}' with messageContent: {}".format(recipients, self.gmailUsername, subject, messageContent))
        failure = None

        if not isinstance(recipients, (list, tuple)):
            recipients = [recipients]

        htmlMessage = ('{}\n{}\n{}'.format(self.__create_header(), messageContent, self.__create_footer()))
        logging.debug("Create html message: {}".format(htmlMessage))

        # Try to send the email.  If sending fails, retry 5 times before giving up
        for x in range(0, 5):
            if x is not 0:
                time.sleep(5) # Wait 5 seconds if this is a retry

            try:
                #server = smtplib.SMTP('smtp.gmail.com:587')
                #server.ehlo()
                #starttls = server.starttls()
                #server.ehlo()
                #login = server.login(self.gmailUsername, self.gmailPassword)
                
                emailTo = ", ".join(recipients)
                emailMessage = MIMEMultipart("alternative")
                emailMessage['Subject'] = "GARAGE: {}".format(subject)
                emailMessage['From'] = self.gmailUsername
                emailMessage['To'] = emailTo
                htmlMessagePart = MIMEText(htmlMessage, "html")
                emailMessage.attach(htmlMessagePart)

                for f in files or []:
                    if os.path.isfile(f):
                        with open(f, "rb") as fil:
                            part = MIMEApplication(
                                fil.read(),
                                Name=basename(f)
                            )
                        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
                        msg.attach(part)
                    else:
                        logging.warn('Attempting to email file {} but no such file exists'.format(f))

                #sendit = server.sendmail(self.gmailUsername, emailTo, emailMessage.as_string())
                #server.quit()
                logging.info("Sent {}, {}, {}".format(emailMessage['Subject'], emailMessage['From'], emailMessage['To']))

                # Success: so return out of retry loop
                return
            except Exception as e:
                logging.warn("Failed on attempt {} of sending htmlMessage: {}, {}, {} Because: {}".format(x, subject, htmlMessage, recipients, e))
                failure = e

        raise failure

    def __create_header(self):
        header = """\
        <html>
          <head>
            <style>
                %s
            </style>
          </head>
          <body>
          <div>
        """
        return header % (self.cssStyle)

    def __create_footer(self):
        footer = """\
              <p>
              Sincerly,<br>
              <i>The Garage Door</i> 
              </div>
          </body>
        </html>
        """
        return footer