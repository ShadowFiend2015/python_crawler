from urllib.request import urlopen, urlretrieve
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import json

img_count = 0
def download_img(url, name):
    try:
        urlretrieve(url, './BaiduPhotos/%s.jpg'%name)
    except (HTTPError, URLError, FileNotFoundError) as e:
        print(e)
        return False
    return True


def get_img(url):
    global img_count
    try:
        html = urlopen(url)
    except HTTPError as e:
        print(e)
        return
    try:
        bs_obj = BeautifulSoup(html.read(), 'html.parser')
        datas = json.loads(bs_obj.get_text())
        if 'data' in datas:
            for img_info in datas['data']:
                img_name = img_info['fromPageTitleEnc'] if 'fromPageTitleEnc' in img_info else str(img_count)
                img_name = img_name.replace('/', '|')
                img_name = img_name.replace('.', '|')
                if 'replaceUrl' in img_info:
                    if len(img_info['replaceUrl']) > 1 and 'ObjURL' in img_info['replaceUrl'][1]:
                        img_src = img_info['replaceUrl'][1]['ObjURL']
                        download_img_success = download_img(img_src, img_name)
                        if download_img_success is True:
                            img_count += 1



    except AttributeError as e:
        print(e)
        return

# 通过观察发现json网页里有pn=30和rn=30，pn可能代表pagenumber，每次增加30。可通过调range()大小来调整搜索图片的多少
for i in range(30, 601, 30):
    print('saving the photos on the %d(th) page'%int(i/30))
    get_img('http://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&is=&fp=result&queryWord=python&cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=&z=&ic=&word=python&s=&se=&tab=&width=&height=&face=&istype=&qc=&nc=1&fr=&pn=' + str(i) + '&rn=30&gsm=1e&1488784110945=')