from urllib.request import urlopen
import urllib
from bs4 import BeautifulSoup


def get_air_quality(url):
    try:
        html = urlopen(url)
    except urllib.error.HTTPError as e:
        print(e)
        return None
    try:
        bs_obj = BeautifulSoup(html.read(), 'html.parser')
        air_quality = bs_obj.find('div', {'class': 'fright clearfix'}).dd
        # print('$$$: ', air_quality)
    except AttributeError as e:
        print(e)
        return None
    return air_quality


def show_air_quality():
    url = 'http://tianqi.2345.com/air-71141.htm'
    air_quality = get_air_quality(url)
    air_quality_rank = air_quality.find('div', {'class': 'td td2'}).i.get_text()
    air_quality_index = air_quality.find('div', {'class': 'td td3 tc'}).span.get_text()
    print('今日PM2.5指数：', air_quality_index, air_quality_rank)


show_air_quality()