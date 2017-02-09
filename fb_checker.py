# fb_checker.py
# Send an email when changes have been made to a FB page
# Written by nckid, February 2017

import sys
import requests
import json
import datetime
import time
import smtplib
from fabric.colors import blue
from fabric.colors import green
from fabric.colors import yellow
from email.mime.text import MIMEText


def fbPageData(page_id, access_token, num_statuses):

    # construct the URL string
    base = "https://graph.facebook.com/v2.8"
    node = "/" + page_id + '/feed'
    parameters = "/?fields=message,created_time,from&limit=%s&access_token=%s" % (num_statuses, access_token)
    url = base + node + parameters

    # retrieve data
    r = requests.get(url)
    response = r.content
    jr = json.loads(response)

    # for the item in "data"
    # print the information
    # jd = jr["data"]
    # for item in jd:
    #     print "----------------------------"
    #     print item.get("message")
    #     print item.get("created_time")

    # dump all the json
    # print json.dumps(jr, indent=4, sort_keys=True)

    return jr


# looks for posts from specified username
def print_last_response(page_info, username):
    count = 0

    while True:
        u = page_info["data"][count]["from"]["name"]
        m = page_info["data"][count]["message"]
        ct = page_info["data"][count]["created_time"]

        if u == username:
            break
        else:
            count = count + 1

    return ct, m, u


def send_alert(subject, body):
    # create a text/plain message
    # also, convert the text, so the emjois don't cause errors...
    msg = MIMEText(body.encode('utf-8'))

    from_email = ''
    to_email = ''

    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    # send the message via our own SMTP server, but don't include the envelope header.
    s = smtplib.SMTP('')  # SMTP server
    s.sendmail(from_email, [to_email], msg.as_string())
    s.quit()


print (blue("[+] Script starting.."))

# number of statuses you want to pull
num_statuses = '5'

# FB Developer Information
app_id = ''  # SENSITVE
app_secret = ''  # SENSITVE

# create the access token
access_token = app_id + "|" + app_secret

# FB page ID
# found in the page's URL
page_id = ''  # SENSITVE

# username of the FB page
username = ""  # SENSITVE

# hit the page and return the information
page_info = fbPageData(page_id, access_token, num_statuses)

# print the information from the USER'S last message
ct, m, u = print_last_response(page_info, username)

while True:
    try:
        # open the file containing the pervious data
        with open('last_response.txt', 'r') as pd:
            # pass the previous current time
            pct = pd.read()

        # compare the current time to the previous current time
        if ct == pct:
            print "[-] Nothing changed... --> ", datetime.datetime.now()
            time.sleep(60)
            continue
        else:
            print (green("[!] Something changed! --> ", datetime.datetime.now()))
            # close the file being read, so it can be written to
            pd.close()

            # change the saved data
            csd = open('last_response.txt', 'w')
            csd.write(str(ct))
            csd.close()

            # output the latest post
            print (blue("[-] This is the lastest message:\n\n%s\n\n%s\n\n%s\n\n" % (u, m, ct)))

            # too lazy to build error handling for the message right now...
            print (green("[+] Sending the email...hopefully it goes!"))

            # subject and body of the email
            subject = '[UPDATE] New Post! %s' % datetime.datetime.now()
            body = "This is the lastest message:\n\n%s\n\n%s\n\n%s\n\n" % (u, m, ct)
            # send email
            send_alert(subject, body)

            print (green("[+] Sending cleared...waiting for new posts."))

            # DON'T STOP! THERE MIGHT BE MORE POSTS!!!
            time.sleep(60)
            continue
    except IOError:
        print (yellow("No baseline found."))
        print (yellow("Creating file.."))
        previous = open('last_response.txt', 'w')
        previous.close()
        print (blue("File created..."))
        continue
    except KeyboardInterrupt:
        break
    break

print (blue("[+] Script ending.."))

sys.exit(0)
