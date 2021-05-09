from flask import Flask
from flask import render_template

import requests
import re
import random
from bs4 import BeautifulSoup

app = Flask(__name__)

# create the list of EO word/definitions
page = requests.get("https://www.esperanto-panorama.net/vortaro/eo-en-u.htm")
soup = BeautifulSoup(page.content, 'html.parser')
pre_sections = soup.find_all('pre')
pre_texts = [pre.text for pre in pre_sections]
all_words = [re.split(r'\s{2,}', row)  for pre in pre_texts for row in pre.split('\n')]


@app.route('/')
def index():

    word_def = random.choice(all_words)
    return render_template('welcome.html', word_def=word_def)

if __name__ == '__main__':
    app.run()
