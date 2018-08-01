from urllib.request import urlopen
import urllib
from bs4 import BeautifulSoup
import queue
import re
import random
import datetime
from inspect import currentframe

base_url = 'https://bj.5i5j.com/zufang'
district = '/huilongguan/'
options = ''
origin_url = base_url + district + options
keywords = ['独卫', '独立卫浴']

class RoomInfo():
    def __init__(self):
        self.title = ''
        self.price = 0
        self.location = ''
        self.detail = ''
        self.date = ''
        self.url = ''
        self.has_keyword = False
        self.rent_type = 0 # 0 - 合租, 1 - 整租

    def __str__(self):
        return 'title: %s   price: %d   location: %s    detail: %s  date: %s    url: %s    has_keyword: %r  rent_type: %d' % (self.title, self.price, self.location, self.detail, self.date, self.url, self.has_keyword, self.rent_type)

    def set_title(self, title: str):
        self.title = title
    def set_price(self, price: int):
        self.price = price
    def set_location(self, location: str):
        self.location = location
    def set_detail(self, detail: str):
        self.detail = detail
    def set_date(self, date: str):
        self.date = date
    def set_url(self, url: str):
        self.url = url
    def set_has_keyword(self):
        self.has_keyword = True
    def set_rent_type(self, type):
        self.rent_type = type

class RoomStatistic():
    def __init__(self):
        self.rooms = []
        self.sum_price = 0
        self.count = 0
        self.keyword_sum_price = 0
        self.keyword_count = 0
        self.keywords = set()
        self.keyword_sharedrent_sum_price = 0
        self.keyword_sharedrent_count = 0

    def set_keywords(self, words: list):
        for word in words:
            self.keywords.add(word)

    def parse_rooms(self, bs_obj: BeautifulSoup):
        try:
            rooms = bs_obj.find('div', {'class': 'list-con-box'}).find_all('div', {'class': 'listCon'})
        except AttributeError as e:
            print('line', get_linenumber(), ':', e)
            return None
        for room in rooms:
            room_info = self.parse_room_info(room)
            self.statistic_room_info(room_info)
            # print('line', get_linenumber(), ':', room_info)


    def parse_room_info(self, room: BeautifulSoup):
        room_info = RoomInfo()
        try:
            tail_url = room.find('h3', {'class': 'listTit'}).find('a').attrs['href']
            room_info.set_url(base_url + tail_url)
        except AttributeError as e:
            print('line', get_linenumber(), ':', e)
        try:
            title = ''.join(room.find('h3', {'class': 'listTit'}).find('a').find_all(text=True, recursive=False))
            room_info.set_title(title)
            for keyword in self.keywords:
                if keyword in title:
                    room_info.set_has_keyword()
                    break
        except AttributeError as e:
            print('line', get_linenumber(), ':', e)
        try:
            ps = room.find('div', {'class': 'listX'}).find_all('p')
            for p in ps:
                i_tag = p.find('i')
                if i_tag == None:
                    continue
                if i_tag.attrs['class'][0] == 'i_01':
                    room_info.set_detail(''.join(p.find_all(text=True, recursive=False)))
                if i_tag.attrs['class'][0] == 'i_02':
                    pre_location = ''.join(p.find('a').find_all(text=True, recursive=False))
                    tail_location = ''.join(p.find_all(text=True, recursive=False))
                    room_info.set_location(pre_location + tail_location)
                if i_tag.attrs['class'][0] == 'i_03':
                    date_about = ''.join(p.find_all(text=True, recursive=False))
                    date_rex = re.search('[0-9]{4}-[0-9]{2}-[0-9]{2}', date_about)
                    date = ''
                    if date_rex is not None:
                        date = date_rex.group(0)
                    else:
                        if date_about[-4:-2] == '今天':
                            date = datetime.datetime.now().strftime("%Y-%m-%d")
                        elif date_about[-4:-2] == '昨天':
                            date = (datetime.datetime.now() - datetime.timedelta(1)).strftime("%Y-%m-%d")
                        elif date_about[-4:-2] == '前天':
                            date = (datetime.datetime.now() - datetime.timedelta(2)).strftime("%Y-%m-%d")
                    room_info.set_date(date)
        except AttributeError as e:
            print('line', get_linenumber(), ':', e)
        try:
            price_type = room.find('div', {'class': 'listX'}).find('div', {'class': 'jia'}).find_all('p')
            for p in price_type:
                if p.has_attr('class') and p.attrs['class'][0] == 'redC':
                    price = ''.join(p.find('strong').find_all(text=True, recursive=False))
                    room_info.set_price(int(price))
                else:
                    type_str = ''.join(p.find_all(text=True, recursive=False))
                    type = 0 if type_str[-2:] == '合租' else 1
                    room_info.set_rent_type(type)
        except AttributeError as e:
            print('line', get_linenumber(), ':', e)
        return room_info

    def statistic_room_info(self, room_info: RoomInfo):
        self.rooms.append(room_info)
        self.sum_price += room_info.price
        self.count += 1
        if room_info.has_keyword:
            self.keyword_sum_price += room_info.price
            self.keyword_count += 1
        if room_info.has_keyword and room_info.rent_type == 0:
            self.keyword_sharedrent_sum_price += room_info.price
            self.keyword_sharedrent_count += 1

    def average_all(self):
        if self.count == 0:
            return 0
        return self.sum_price / self.count
    def average_keyword(self):
        if self.keyword_count == 0:
            return 0
        return self.keyword_sum_price / self.keyword_count
    def average_keyword_sharedrent(self):
        if self.keyword_sharedrent_count == 0:
            return 0
        return self.keyword_sharedrent_sum_price / self.keyword_sharedrent_count
    def print_room_keyword(self):
        for i, room in enumerate(self.rooms):
            if room.has_keyword:
                print('room[%03d]:' % (i), room)
        print('statistic info: keywords[%s]  count[%d]  average_price[%.2f]' % (", ".join(self.keywords),  self.keyword_count, self.average_keyword()))


class Urls():
    def __init__(self, init_url):
        self.visited_urls = set()
        self.next_urls = queue.Queue()
        self.next_urls.put(init_url)

    def add_url(self, new_url: str):
        if new_url == '' or new_url in self.visited_urls:
            return None
        self.next_urls.put(new_url)

    def get_url(self):
        url = ''
        while url == '':
            if self.next_urls.empty():
                return None
            url = self.next_urls.get()
            if url not in self.visited_urls:
                self.visited_urls.add(url)
                return url

    def is_empty(self):
        return self.next_urls.empty()

    def add_url_by_bs(self, bs_obj: BeautifulSoup):
        if bs_obj is None:
            return None
        next_url = ''
        try:
            links = bs_obj.find('div', {'class': 'pageBox'}).find('div', {'class': 'pageSty rf'}).find_all('a')
            for link in links:
                if ''.join(link.find_all(text=True, recursive=False)) == '下一页':
                    next_url = base_url + link.attrs['href']
                    break
        except AttributeError as e:
            print('line', get_linenumber(), ':', e)
            return None
        self.add_url(next_url)

def parse_url(url: str):
    next_url = ''
    try:
        html = urlopen(url)
    except urllib.error.HTTPError as e:
        print('line', get_linenumber(), ':', e)
        return None
    return BeautifulSoup(html.read(), 'html.parser')

def get_linenumber():
    cf = currentframe()
    return cf.f_back.f_lineno

def main():
    urls = Urls(origin_url)
    room_statistic = RoomStatistic()
    room_statistic.set_keywords(keywords)
    while not urls.is_empty():
        current_url = urls.get_url()
        if current_url is None:
            break
        print('line', get_linenumber(), ':', current_url)
        bs_obj = parse_url(current_url)
        if bs_obj is None:
            continue
        urls.add_url_by_bs(bs_obj)
        # TODO bs_obj
        room_statistic.parse_rooms(bs_obj)
        # break is just for test
        # break
        print('url[%s] finished' % current_url)
    room_statistic.print_room_keyword()
    print('line', get_linenumber(), ':', 'finished!')



if __name__ == '__main__':
  main()