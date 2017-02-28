from urllib.request import urlopen
import urllib
from bs4 import BeautifulSoup
import re
import random


def get_links(article_url):
    try:
        html = urlopen('https://en.wikipedia.org' + article_url)
    except urllib.error.HTTPError as e:
        print(e)
        return None
    try:
        bs_obj = BeautifulSoup(html.read(), 'html.parser')
        links = bs_obj.find('div', {'id': 'bodyContent'}).find_all('a', {'href': re.compile('^(/wiki/)((?!:).)*$')})
    except AttributeError as e:
        print(e)
        return None
    return links


links = get_links('/wiki/Kevin_Bacon')
while len(links) > 0:
    new_article_url = links[random.randint(0, len(links) - 1)].attrs['href']
    print(new_article_url)
    links = get_links(new_article_url)
