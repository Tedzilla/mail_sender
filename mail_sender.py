"""Mail sender package
Created 01.12.2017"""

import smtplib
import re
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email.header import Header
from email.utils import formataddr


class SendMail(object):
    """SendMail class"""

    __sender = "teoworkmail@gmail.com"
    __server = 'localhost'
    __email_validation = r"""^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|
                            (\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|
                            (([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"""

    def __init__(self, **kwargs):
        """Constructor => all functiponality is executed below
        Params :
        recipient => mandatory // can be string of one mail
                                  can be list of mails
                                  can be list of dictionaries where your alias
                                  should be key and value list or one mail
        subject => not mandatory
        message => not mendatory
        attachment => not mendatory
        sender => not mendatory (default = "teoworkmail@gmail.com")
        server => not mendatory (default = 'localhost')"""
        self.__recipient = self.validate_recipients(kwargs.get('recipient'))
        self.__subject = kwargs.get('subject', None)
        self.__message = kwargs.get('message', None)
        self.__attachment = self.validate_attachments(kwargs.get('attachment', None))
        self.__sender = kwargs.get('sender', self.__sender)
        self.__server = kwargs.get('server', self.__server)
        self.__sending(send_to=self.__recipient, \
                    subject=self.__subject, \
                    text=self.__message, \
                    files=self.__attachment)


    @staticmethod
    def validate_recipients(recipient):
        """Validation of recipients"""
        if isinstance(recipient, list):
            for mail_adress in recipient:
                if isinstance(mail_adress, dict):
                    for _, mail_value in mail_adress.items():
                        if isinstance(mail_value, list):
                            for mail_adr in mail_value:
                                if  not re.match(SendMail.__email_validation, mail_adr, re.X):
                                    raise NameError("Your mail is not correct => {}" \
                                                    .format(mail_adr))
                        elif  not isinstance(mail_value, str) and \
                            not re.match(SendMail.__email_validation, mail_value, re.X):
                            raise ValueError("Type of values in dict => {} <= | Value =>{} <=" \
                                            .format(type(mail_value), mail_value))
                elif not re.match(SendMail.__email_validation, mail_adress, re.X):
                    raise TypeError(
                        """Recipient should be list or dict with values =>
                        list of mail adresses.Your structure is {}""".format(mail_adress))
            return recipient
        elif isinstance(recipient, str) and re.match(SendMail.__email_validation, recipient, re.X):
            string_tolist = []
            string_tolist.append(recipient)
            return string_tolist
        else:
            raise NameError("Something wrong with the recipient.Check it again => {}" \
                .format(recipient))

    @staticmethod
    def validate_attachments(attachment):
        """Validation of attachments"""
        if attachment is None:
            return attachment
        elif isinstance(attachment, str):
            attachments = []
            attachments.append(attachment)
            return attachments
        elif isinstance(attachment, list):
            return attachment
        else:
            raise TypeError('Attachment is not correct. Check it again!')

    @staticmethod
    def files_upload(msg, kwargs):
        """Attaching files to the mail static function"""
        if kwargs['files'] is not None:
            for file_a in kwargs['files']:
                with open(file_a, 'rb') as fil:
                    part = MIMEApplication(fil.read(), Name=basename(file_a))
                    part['Content-Disposition'] = 'attachment; filename="{}"' \
                    .format(basename(file_a))
                    msg.attach(part)
       # return msg


    def __sending(self, **kwargs):
        """Sending function"""
        msg = MIMEMultipart()
        if isinstance(kwargs['send_to'][0], dict):
            for mail_dict in kwargs['send_to']:
                for key_mail, value_mail in mail_dict.items():
                    msg['From'] = formataddr((str(Header(key_mail, 'utf-8')), self.__sender))
                    if isinstance(value_mail, list):
                        msg['To'] = COMMASPACE.join(value_mail)
                    else:
                        msg['To'] = value_mail
                    msg['Date'] = formatdate(localtime=True)
                    msg['Subject'] = kwargs['subject']
                    msg.attach(MIMEText(kwargs['text']))
                    self.files_upload(msg, kwargs)
                    with smtplib.SMTP(self.__server) as smtp:
                        smtp.sendmail(self.__sender, value_mail, msg.as_string())
        else:
            msg['From'] = self.__sender
            msg['To'] = COMMASPACE.join(kwargs['send_to'])
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = kwargs['subject']
            msg.attach(MIMEText(kwargs['text']))
            self.files_upload(msg, kwargs)
            with smtplib.SMTP(self.__server) as smtp:
                smtp.sendmail(self.__sender, kwargs['send_to'], msg.as_string())
