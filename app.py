from flask import Flask
from flask import render_template, url_for, render_template_string
from flask import request, redirect
from flask import session
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
    base_url="https://app.clickup.com/",
    #authorization_url=f"https://app.clickup.com/api?client_id={clickup_client_id}&redirect_uri={redirect_url}",
    authorization_url="https://app.clickup.com/api",
    token_url="https://app.clickup.com/api/v2/oauth/token/",
    token_url_params={'include_client_id': True, 'Content-Type': 'application/json'}
)

app.register_blueprint(clickup_blueprint, url_prefix="/login")


@app.route("/load-profile")
def load_profile():
    # have to use full URL here because base_url is not being used
    r = clickup_blueprint.session.get("https://app.clickup.com/api/v2/team")
    r.raise_for_status()
    data = r.json()
    print(data)
    session["data"] = data
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/")
def index():
    if clickup_blueprint.session.authorized:
        return render_template_string("""Logged in as {{ session["data"] }}<br><a href="{{ url_for("logout") }}">Log Out</a>""")

    return render_template_string("""Not logged in<br><a href="{{ url_for("clickup.login") }}">Log In</a>""")


#@app.route('/')
#def index():

##    word_def = random.choice(all_words)
#    return render_template('welcome.html', word_def=word_def)

#@app.route('/hillary')
#def hillary():
#    resp = clickup_blueprint.session.get('/api/v2/team')
#    print(resp.content)
#    return render_template('hillary.html')

@app.route('/trythis')
def login(token):
    print("is authorized: ", clickup_blueprint.session.authorized)
    print("token", token)
    if not clickup_blueprint.session.authorized:
        return render_template(url_for('clickup.login'))
    
    resp = clickup_blueprint.session.get('/api/v2/team', headers={'Content-Type': 'application/json'})
    assert resp.ok, resp.text
    print(resp.json())

    
    return render_template('hillary.html')

    #session['code'] = request.args.get('code')
    #print("code: ", session['code'])
    #token_url=f"https://app.clickup.com/api/v2/oauth/token"
    #params = {
    #    'client_id': clickup_client_id,
    #    'client_secret': clickup_client_secret,
    #    'code': session['code']
    #}
    #resp = requests.post(token_url, params=params)
    #print(resp.content)
    #session['user_access_token'] = resp.content

    #resp = clickup_blueprint.session.get("/user")
    #assert resp.ok
    #print("Here's the content of my response: " + resp.content)

    #return render_template('hillary.html')


if __name__ == '__main__':
    app.run()
    #app.run(port=5005, debug=True)
