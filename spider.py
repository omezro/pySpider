#coding:utf-8
__author__ = 'omega'

import warnings
warnings.filterwarnings("ignore")
from urllib import request
from bs4 import BeautifulSoup as bs
import matplotlib
matplotlib.rcParams['figure.figsize'] = (10.0, 5.0)
import json
import string
import time
import MySQLdb

domin_url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
headers = {'User-Agent': user_agent}



#获取省
def getProvinceList():
    prequest = request.Request(domin_url, None, headers)
    resp = request.urlopen(prequest)
    html_data = resp.read()
    soup = bs(html_data, 'html.parser')
    provincetable = soup.find_all('table', class_='provincetable')
    provincetr = provincetable[0].find_all('tr', class_='provincetr')
    province_list = []
    city_list = []
    dis_list = []
    for item in provincetr:
        for iitem in item:
            if not iitem.a is None:
                code = iitem.a['href'].split('.')[0]
                name = iitem.a.contents[0]
                city_data = getCityList(code, name)
                city_list.append(city_data[0])
                dis_list.append(city_data[1])
                province_list.append({
                    'code': code,
                    'name': name,
                    'common_name': name,
                    'level': 1
                })
    #TODO 分别输出到json文件里
    print(province_list)
    # with open('D:/pyproject/list/province_list.json','w') as f:
    #     province_json = json.dumps(province_list)
    #     f.write(province_json)
    #     print('province_list export done!')
    #     f.close()
    print(city_list)
    # with open('D:/pyproject/list/city_list.json','w') as f1:
    #     city_json = json.dumps(city_list)
    #     f1.write(city_json)
    #     print('city_list export done!')
    #     f1.close()
    print(dis_list)
    # with open('D:/pyproject/list/dis_list.json','w') as f2:
    #     dis_json = json.dumps(dis_list)
    #     f2.write(dis_json)
    #     print('dis_list export done!')
    #     f2.close()
    #return province_list


#爬取城市数据
def getCityList(pCode, pName):
    crequest = request.Request(domin_url+pCode+'.html', None, headers)
    resp = request.urlopen(crequest)
    html_data = resp.read()
    soup = bs(html_data, 'html.parser')
    citytable = soup.find_all('table', class_='citytable')
    citytr = citytable[0].find_all('tr', class_='citytr')
    city_list = []
    city_code = []
    district_list = []
    for item in citytr:
        for citem in item:
            if citem.a.contents[0].isdigit():
                city_code.append({citem.a.contents[0]})
            else:
                cname = citem.a.contents[0]
                preCode = citem.a['href'].split('.')[0]
                ccode = preCode.split('/')[1]
                district_list.append(getDistrictList(cname, preCode, pCode, pName))
                city_list.append({
                    'name': cname,
                    'code': ccode,
                    'common_name': cname,
                    'province_code': pCode,
                    'province_name': pName,
                    'level': 2
                })
    time.sleep(0.5)
    city_data = [city_list, district_list]
    return city_data


def getDistrictList(cname, ccode, pCode, pName):
    drequest = request.Request(domin_url + ccode + '.html', None, headers)
    resp = request.urlopen(drequest)
    html_data = resp.read()
    soup = bs(html_data, 'html.parser')
    distable = soup.find_all('table', class_='countytable')
    if len(distable):
        distr = distable[0].find_all('tr', class_='countytr')
    else:
        distable = soup.find_all('table', class_='towntable')
        distr = distable[0].find_all('tr', class_='towntr')
    dis_list = []
    dis_code = []
    dis_td = []
    for item in distr:
        for ditem in item:
            if ditem.a is None:
                for dditem in ditem:
                    if dditem.isdigit():
                        dis_td.append(dditem[0:6])
                    else:
                        dis_td.append(dditem)
            else:
                if ditem.a.contents[0].isdigit():
                    dis_code.append({ditem.a.contents[0]})
                else:
                    dname = ditem.a.contents[0]
                    preCode = ditem.a['href'].split('.')[0]
                    dcode = preCode.split('/')[1]
                    dis_list.append({
                        'name': dname,
                        'code': dcode,
                        'common_name': dname,
                        'province_code': pCode,
                        'province_name': pName,
                        'level': 3,
                        'city_code': ccode.split('/')[1],
                        'city_name': cname
                    })
    if len(dis_td):
        dis_list.append({
            'name': dis_td[1],
            'code': dis_td[0],
            'common_name': dis_td[1],
            'province_code': pCode,
            'province_name': pName,
            'level': 3,
            'city_code': ccode.split('/')[1],
            'city_name': cname
        })
    time.sleep(0.5)
    return dis_list


def getStreet():
    #打开数据库
    db = MySQLdb.connect('localhost','root','123456','city_data',charset='utf8')

    #使用cursor方法获取操作游标
    cursor = db.cursor()

    #使用execute方法执行SQL语句
    cursor.execute('SELECT code FROM district')

    #使用 fetchall() 获取所有数据
    data = cursor.fetchall()

    #关闭数据库连接
    db.close()

    for item in data:
        #拼接访问连接
        durl1 = item[0][0:2]
        durl2 = item[0][2:4]
        drequest = request.Request(domin_url + durl1 + '/' + durl2 + '/' + item[0] + '.html', None, headers)
        resp = request.urlopen(drequest)
        html_data = resp.read()
        soup = bs(html_data, 'html.parser')
        distable = soup.find_all('table', class_='countytable')
        #TODO  暂时不需要街道及下级单位




def main():
    commentList = []
    #省 市 区 街道
    #getProvinceList()
    #获取区域信息  通过区域id获取街道信息
    #getStreet()



#主函数
main()



























