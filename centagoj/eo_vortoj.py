import random
import re
import requests
from bs4 import BeautifulSoup

# create the list of EO word/definitions
page = requests.get("https://www.esperanto-panorama.net/vortaro/eo-en-u.htm")
soup = BeautifulSoup(page.content, 'html.parser')
pre_sections = soup.find_all('pre')
pre_texts = [pre.text for pre in pre_sections]
all_words = [re.split(r'\s{2,}', row) for pre in pre_texts for row in pre.split('\n')]


def get_word():
    return random.choice(all_words)
