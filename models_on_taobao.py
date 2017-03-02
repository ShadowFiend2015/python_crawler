# https://www.taobao.com/markets/mm/mmku?spm=5679.126488.640763.1.kNu7CW 这个网站上的mm，图片的src地址在动态网页里，在chrome中检查，看Network，搜json可找到该动态返回json文件的网址
from urllib.request import urlopen, urlretrieve
import urllib
from bs4 import BeautifulSoup
import re, json

class Model():
    def __init__(self, image_src, name):
        self.image_src = image_src
        self.name = name


def get_models_info(url):
    models = []
    try:
        html = urlopen(url)
    except urllib.error.HTTPError as e:
        print(e)
        return models
    try:
        bs_obj = BeautifulSoup(html.read().decode('gbk'), 'html.parser')
        temp_str = bs_obj.get_text()
    except AttributeError as e:
        print(e)
        return models
    try:
        data = re.search('\{.*\}', temp_str)
        data = temp_str[data.span()[0]:data.span()[1]]
        data = json.loads(data)
    except AttributeError as e:
        print(e)
        return models
    if 'dataList' in data:
        for model_info in data['dataList']:
            if 'avatarUrl' in model_info:
                name = model_info['darenNick'] if 'darenNick' in model_info else '???'
                model = Model(model_info['avatarUrl'], name)
                models.append(model)
    return models


def download_image(model, model_index):
    image_url = model.image_src
    try:
        if image_url[0:2] == '//':
            image_url = 'http:' + image_url
        urlretrieve(image_url, './ModelPhotos/%s.jpg'%model.name)
    except (ValueError, urllib.error.HTTPError) as e:
        print(e)
        return
    print('saving the photo of %d(th) model now'%model_index)


def main():
    models = []
    for i in range(1, 68):
        url = 'https://mm.taobao.com/alive/list.do?scene=all&page=' + str(i) + '&_ksTS=1488371586709_139&callback=jsonp140'
        print(url)
        models += get_models_info(url)
    for idx, model in enumerate(models):
        download_image(model, idx)


main()

