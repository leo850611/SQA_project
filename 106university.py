# coding=utf-8
import requests
import re
from bs4 import BeautifulSoup
## Copyright (C) 2017 Leo Sheu. <loli>

header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4,ja;q=0.2',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'
}
session = requests.Session()

#學校代號及名稱
school = session.get("http://freshman.tw/cross/",headers = header)
schoolsoup = BeautifulSoup(school.text, "html.parser")
schoolname = schoolsoup.findAll('span',{'class':'college_name'})
#schoolnum = schoolsoup.findAll('a',{'href':re.compile("/cross/106/\d")})
schoolList = []
for school in schoolname:
    schoolList.append(school.text.split(' '))    
print(schoolList)

