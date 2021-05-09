from flask import Flask
from flask import render_template
from flask_dance.consumer import OAuth2ConsumerBlueprint

import os
import requests
import re
import random
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

# create the list of EO word/definitions
page = requests.get("https://www.esperanto-panorama.net/vortaro/eo-en-u.htm")
soup = BeautifulSoup(page.content, 'html.parser')
pre_sections = soup.find_all('pre')
pre_texts = [pre.text for pre in pre_sections]
all_words = [re.split(r'\s{2,}', row)  for pre in pre_texts for row in pre.split('\n')]


clickup_client_id = os.environ['CLICKUP_CLIENT_ID']
clickup_client_secret = os.environ['CLICKUP_CLIENT_SECRET']
#redirect_url = "http://127.0.0.1:5005/hillary.html"
redirect_url = "centagoj.herokuapp.com/login"

clickup_blueprint = OAuth2ConsumerBlueprint(
    "clickup", __name__,
    client_id=clickup_client_id,
    client_secret=clickup_client_secret,
    base_url="https://app.clickup.com",
    #token_url=f"https://app.clickup.com/api?client_id={clickup_client_id}&redirect_uri={redirect_url}",
    authorization_url=f"https://app.clickup.com/api?client_id={clickup_client_id}&redirect_uri={redirect_url}",
)
app.register_blueprint(clickup_blueprint, url_prefix="/login")


@app.route('/')
def index():

    word_def = random.choice(all_words)
    return render_template('welcome.html', word_def=word_def)

@app.route('/hillary')
def hillary():
    return render_template('hillary.html')

@app.route('/redirect')
def redirect():
    resp = clickup_blueprint.session.get("/user")
    assert resp.ok
    print("Here's the content of my response: " + resp.content)

    return render_template('hillary.html')


if __name__ == '__main__':
    app.run()
    #app.run(port=5005, debug=True)
