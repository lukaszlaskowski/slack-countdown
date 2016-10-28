#!/usr/bin/python
# -*- coding: latin-1 -*-
from flask.ext.script import Manager
from flask import Flask
from datetime import datetime
import json
import os
import requests
import sys

app = Flask(__name__)
manager = Manager(app)

SLACK_URL = os.environ.get('SLACK_URL')
if not SLACK_URL:
	print("Missing environment variable SLACK_URL")
	exit(1)

def days_from_date(strdate):
    currentdate = datetime.today()
    futuredate = datetime.strptime(strdate, '%Y-%m-%d')
    delta = futuredate - currentdate
    return delta.days + 1


def get_image_url(tag):
	response = requests.get("http://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC&tag=" + tag)
	imageUrl = response.json().get("data").get("fixed_height_downsampled_url")
	return imageUrl


def post(text, imageUrl, event):
    payload = {
		"text": text,
		"icon_emoji": ":boss:",
        "attachments": [{   
				"image_url": imageUrl,
                "color": "#000000"
            }]
    }
    
    r = requests.post(SLACK_URL, data=json.dumps(payload))


def post_error(message):
    payload = {
        "attachments": [{
                "title": "Błąd!",
                "text": message,
                "color": "#d60000"
            }]
    }
    
    r = requests.post(SLACK_URL, data=json.dumps(payload))


@manager.option("-d", "--deadline", dest="date",
                      help="Specify the deadline in ISO format: yyyy-mm-dd", metavar="DEADLINE")
@manager.option("-e", "--event", dest="event", 
                      help="Name of the deadline event",metavar="EVENT")


def deadline(date, event): 
	try:
		days = days_from_date(date)
		text = ""
		imageUrl = ""

		if (days < -1):
			return
		elif (days == -1):
			imageUrl = get_image_url("applause")
			text = "*%s* już się skończył. *Bravo!*" % (event)
		elif days == 0:
			imageUrl = get_image_url("scared")
			text = "Deadline dla *%s* jest *dzisiaj*!" % (event)
		elif days == 1:
			imageUrl = get_image_url("what")
			text = "Do końca *%s* pozostał *%d dzień*!" % (event, 1)
		elif days > 1:
			imageUrl = get_image_url("party hard")
			text = "Do końca *%s* pozostało *%d dni!*" % (event, days)
			
		post(text, imageUrl, event)
	except:
		post_error(sys.exc_info()[0])

@manager.command
def initiate():
    payload = { "text": "App is now connected to your Slack Channel."}
    r = requests.post(SLACK_URL, data=json.dumps(payload))

    
if __name__ == "__main__":
    manager.run()


