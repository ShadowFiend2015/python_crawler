from urllib import request
from urllib import error
import urllib
from datetime import datetime, timedelta
from inspect import currentframe
import json
import mysql.connector

# channel_list = ["cctv1", "cctv2", "cctv3", "cctv4", "cctv5", "cctv6", "cctv7", "cctv8", "cctv9", "cctv10", "cctv11", "cctv12", "cctv13", "cctv14", "cctv15"]

mydb = mysql.connector.connect(
  host="ip",
  user="user",
  passwd="password!",
  database="dbname"
)

class TV():
    def __init__(self, id, name, alias):
        self.id = id
        self.name = name
        self.alias = alias

# read data from mysql
def get_channel_list():
    channel_list = []
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM tv_channels")
    myresult = mycursor.fetchall()
    for x in myresult:
        channel_list.append(TV(x[0], x[4], x[5]))
    return channel_list

def grab(url):
    try:
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )

        with urllib.request.urlopen(req) as x:
            data_str = x.read().decode('utf-8')
    except (urllib.error.HTTPError, AttributeError) as e:
        print('line', get_linenumber(), ':', e)
        return None
    data_str = data_str[9:-2]
    data = json.loads(data_str)
    return data

# save data to mysql
def save_datas(datas, channel):
    if 'data' not in datas or channel.alias not in datas['data'] or 'list' not in datas['data'][channel.alias] or datas['data'][channel.alias]['list'] is None:
        print('line', get_linenumber(), ':', channel.alias, 'data is None')
        return
    mycursor = mydb.cursor()

    sql = "INSERT INTO shows (name, tv_id, tv_name, start, end, sts, ets) VALUES (%s, %s, %s, %s, %s, %s, %s)"

    for show in datas['data'][channel.alias]['list']:
        val = (show['title'], channel.id, channel.name, datetime.fromtimestamp(show['startTime']).strftime('%Y-%m-%d %H:%M:%S'),
               datetime.fromtimestamp(show['endTime']).strftime('%Y-%m-%d %H:%M:%S'), show['startTime'], show['endTime'])
        try:
            mycursor.execute(sql, val)
        except mysql.connector.errors.IntegrityError as e:
            print('line', get_linenumber(), ':', e)
    mydb.commit()

# use for debug
def get_linenumber():
    cf = currentframe()
    return cf.f_back.f_lineno

def main():
    channel_list = get_channel_list()
    monday = datetime.today() - timedelta(days=datetime.today().weekday())
    thisweek = [(monday + timedelta(days=x)).strftime('%Y%m%d') for x in range(0, 7)]
    for channel in channel_list:
        for day in thisweek:
            url = 'http://api.cntv.cn/epg/getEpgInfoByChannelNew?c=%s&serviceId=tvcctv&d=%s&t=jsonp&cb=setItem1' % (channel.alias, day)
            datas = grab(url)
            save_datas(datas, channel)


if __name__ == '__main__':
    main()
