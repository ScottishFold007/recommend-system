import requests
from bs4 import BeautifulSoup
import json
import re
import pymysql
import time

def get_html(url):
    r=requests.get(url,verify=False)
    if r.status_code==200:
        text=r.text
#        print(r.status_code)
    else:
        print("return no headers")
    return text

def parse_header(text1):
    content=json.loads(text1)
    descrip=content.get("data").get("userInfo").get("description")
    follow_count=content.get("data").get("userInfo").get("follow_count")
    followers_count=content.get("data").get("userInfo").get("followers_count")
    gender=content.get("data").get("userInfo").get("gender")
    statuses_count=content.get("data").get("userInfo").get("statuses_count")
    screen_name=content.get("data").get("userInfo").get("screen_name")
    verified_reason=content.get("data").get("userInfo").get("verified_reason")
    id=content.get("data").get("userInfo").get("id")
    return descrip,follow_count,followers_count,gender,statuses_count,screen_name,verified_reason,id



def parse_content(text):
    headers=parse_header(text1)
    weibo=json.loads(text)
    texts=weibo.get("data").get("cards")
    name=headers[5]
    res=[]
    for text in texts:
        li=[]
        try:
            cons=text.get("mblog").get("text")
            con=re.sub('\<.*?\>','',cons)
            created_at=text.get("mblog").get("created_at")
            li.extend([name,con,created_at])
            res.append(li)
        except Exception as e:
            print("raise a error")
            print(e)
    return res

def save_data(data):
    conn=pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        charset='utf8mb4',
        port=3306,
        db='weibocrawl'
    )
    cursor=conn.cursor()
#    sql1='insert into weibocrawl.user_info(descrip,follow_count,followers_count,gender,statuses_count,screen_name,verified_reason,id) values (%s,%s,%s,%s,%s,%s,%s,%s)'
    sql2='insert into weibocrawl.user_content(name,con,created_at)values(%s,%s,%s)'
    try:
        for i in data:
            cursor.execute(sql2,(i[0],i[1],i[2]))
#        cursor.execute(sql1,(data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7]))
        conn.commit()
        print("insert done")
    except Exception as e:
        print(e)
        conn.rollback()
    return data

if __name__ == "__main__":
    uid=['1642351362','3623353053', '1784537661','1669879400','1609648201','1746274673','1280761142','1659809154','1230663070','1731769015',
         '2945931603','1241148864','1649166140','1717675430']
    for j in uid:
    #      url1='https://m.weibo.cn/api/container/getIndex?uid={0}&luicode=10000011&' \
    #           'lfid=100103type%3D1%26q%3D%E5%88%98%E6%98%8A%E7%84%B6&type=uid&value' \
    #           '={0}&containerid=100505{0}'.format(j)
        # text1 = get_html(url1)
        # headers=parse_header(text1)
        # save_data(headers)
        i = 1
        url0='https://m.weibo.cn/api/container/getIndex?uid={0}&luicode=10000011&' \
             'lfid=100103type%3D1%26q%3D%E5%88%98%E6%98%8A%E7%84%B6&type=uid&value' \
             '={0}&containerid=107603{0}&page={1}'.format(j,str(i))
        status = requests.get(url0).status_code
        response = json.loads(requests.get(url0).text).get('ok')
        while status==200 and response==1:
            url1 = 'https://m.weibo.cn/api/container/getIndex?uid={0}&luicode=10000011&' \
                   'lfid=100103type%3D1%26q%3D%E5%88%98%E6%98%8A%E7%84%B6&type=uid&value' \
                    '={0}&containerid=100505{0}'.format(j)
            url2 = 'https://m.weibo.cn/api/container/getIndex?uid={0}&luicode=10000011&' \
                   'lfid=100103type%3D1%26q%3D%E5%88%98%E6%98%8A%E7%84%B6&type=uid&value' \
                   '={0}&containerid=107603{0}&page={1}'.format(j, str(i))
            text1 = get_html(url1)
            headers=parse_header(text1)
            text2 = get_html(url2)
            text=parse_content(text2)
            save_data(text)
            print('------------this is the {} page-----------'.format(i))
            i += 1
            status = requests.get(url2).status_code
            response=json.loads(requests.get(url2).text).get('ok')
