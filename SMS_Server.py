from twilio.rest import TwilioRestClient
import twilio.twiml
import os
import json
import re
import shutil
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import Encoders


from flask import Flask, request, make_response

app = Flask(__name__)

app.debug = True
app.secret_key = '3kjbh645ikuh69er8gtyhoi45t98er(^&(*hjkgnvf'

ACCOUNT_SID = "AC73f144c9d7209ff6ebb9de9988512886"
AUTH_TOKEN = "c893ece55d239042f01e4aeca0427cd0"

client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

BANNED_INITIALS = ["FAG", "ASS", "FUK", "PEE", "POO", "SEX", "TIT", "CUM", "JIZ", "GAY", "NIG"]

DATABASE = "entrants.txt"

def add_entrant(initials, number):
    try:
        with open(DATABASE, "r" "utf8") as fin:
            entrants = json.load(fin)
        entrants[number] = initials
    except:
        shutil.copy("entrantsbackup.txt", "entrants.txt")
        return False, "load"
    try:
        with open(DATABASE, 'w' 'utf8') as fout:
            json.dump(entrants, fout)
        print "added", number
        shutil.copy("entrants.txt", "entrantsbackup.txt")
        send_email()
        return True, None
    except:
        print "dump failure"
        return False, "dump"

def make_fixtures():
    try:
        with open(DATABASE, "r") as fin:
            entrants = json.load(fin)
        entrants["+15124843205"] = "WHG"
        with open(DATABASE, "w") as fout:
            json.dump(entrants, fout)
        return True
    except:
        return False

def notify_winner(winner):
    try:
        with open(DATABASE, "r") as fin:
            entrants = json.load(fin)
            entrants.pop(winner, None)
        with open(DATABASE, "w") as fout:
            json.dump(entrants, fout)
    except:
        pass
    body = "CONGRATULATIONS! The wheel o' winners has chosen you! Show this text to the MC to claim your prize!"
    message = client.messages.create(body=body,
                                     to=winner,
                                     from_="+15129107535")
    print message.sid

def notify_database_error(number, err):
    body = "Database entry FAILED for phone number %s. Error: %s." % (number, err)
    message = client.messages.create(body=body,
                                     to="+15124843205",
                                     from_="+15129107535")
    print message.sid

def clear_db():

    with open(DATABASE, 'w') as fout:
        fout.write('{}')

def send_email():
    send_from = "ERAFFLE"
    send_to = "william.gest@q2ebanking.com"
    subj = "entrants"

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = "REVIEW SCRAPER REPORT: " + subj


    part = MIMEBase('application', "octet-stream")
    part.set_payload(open("entrants.txt", "rb").read())
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename("entrants.txt"))
    msg.attach(part)
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login("q2scraper@gmail.com", "scraper!!")

    try:
        server.sendmail(send_from, send_to, msg.as_string())
    except:
        pass
    server.close()

@app.route('/', methods=['GET', 'POST'])
def receive_text():
    if request.values.get('Body', None) == "CLEAR" and request.values.get('From', None) == "+15124843205":
        clear_db()
        resp = twilio.twiml.Response()
        message = "DB CLEARED."
        resp.message(message)
        return str(resp)
    try:
        initials = request.values.get('Body', None)[:3].upper()
        number = request.values.get('From', None)
        valid = re.match('^[\w ]+$', initials) is not None
        if not initials or len(initials) < 2 or not valid:
            raise TypeError
        if len(initials) == 2:
            initials += " "
        if initials in BANNED_INITIALS:
            raise ValueError
        success, err = add_entrant(initials, number)
        if success:
            message = "You've been entered! Initials recieved: %s. If you want to change your initials, just send a new message. --MUST BE PRESENT TO WIN.--" % initials
        else:
            message = "Entry error. Please try again."
            notify_database_error(number, err)

    except TypeError:
        message = "Entry not successful: we need your initials (2-3 letters, no numbers or special characters). Please try again."
    except IndexError:
        message = "Entry not successful: we need your initials (2-3 letters, no numbers or special characters). Please try again."
    except ValueError:
        message = "Those initials can not be used. Please try again."

    resp = twilio.twiml.Response()
    resp.message(message)
    return str(resp)

@app.route('/entrants', methods=['GET'])
def download_entrants():
    with open(DATABASE) as fin:
        response = make_response(fin.read())
        response.headers["Content-Disposition"] = "attachment; filename=" + DATABASE
        return response



#make_fixtures()
