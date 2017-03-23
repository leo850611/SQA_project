# coding=utf-8
import requests
from bs4 import BeautifulSoup
import re
import sqlite3
import time
## Copyright (C) 2017 Leo Sheu. <loli>

def school_db():
    curs.execute('CREATE TABLE school(snumber INT PRIMARY KEY, sname VARCHAR(20))')
    curs.execute('CREATE TABLE department(snum INT, dnumber VARCHAR(10) PRIMARY KEY, dname VARCHAR(50))')
    
    #學校代號及名稱
    school = requests.get('http://freshman.tw/cross/')
    school_soup = BeautifulSoup(school.text, "html.parser")
    school_name = school_soup.findAll('span',{'class':'college_name'})
    school_list = []
    for school in school_name:
        school_list.append(school.text.split(' '))
        curs.execute('INSERT INTO school (snumber,sname) VALUES(?,?)', (school.text.split(' ')[0],school.text.split(' ')[1]))
    conn.commit()    
    curs.execute('SELECT * from school ORDER BY snumber')
    print(curs.fetchall()) #(1, '國立臺灣大學')

    for school_num in school_list:
        #科系代號及名稱
        department_page = requests.get('http://freshman.tw/cross/106/' + str(school_num[0]))
        department_soup = BeautifulSoup(department_page.text, "html.parser")
        department_num = department_soup.findAll('a',{'class':'d-block'})
        for department in department_num:
            if(department.text != '清華學院學士班'): #校系代碼重複 http://freshman.tw/cross/106/011412
                curs.execute('INSERT INTO department (snum,dnumber,dname) VALUES(?,?,?)', (int(school_num[0]),str(department)[25:31],department.text))            
    conn.commit() 
    curs.execute('SELECT * from department ORDER BY dnumber')
    print(curs.fetchall()) #(153, '153172', '都市計畫與景觀學系')
    
    
if __name__ == '__main__':
    conn = sqlite3.connect('106.db')
    curs = conn.cursor()
    #school_db()
    #curs.execute('CREATE TABLE person(pnumber INT, area CHAR(4),place CHAR(4), pschool VARCHAR(20), pdepartment VARCHAR(50))')
    
    department_list = curs.execute('SELECT * from department ORDER BY dnumber')

    id_list = []
    
    reg = r'<span class="number">(\d+)</span><div style="font-size:12px;">([^0-9]+)-([^0-9]+)考區</div></td>' #10206020,中部,彰化
    get_value = re.compile(reg)
    
    for dnum in department_list:
        print(dnum[1])
        print(dnum)
        if(('音樂'not in dnum[2])and (int(dnum[1])>= 35182 )):
            time.sleep(1)
            #學生及通過校系
            student = requests.get('http://freshman.tw/cross/106/'+ dnum[1])
            student_soup = BeautifulSoup(student.text, "html.parser")
            #准考證號,通過校系,校系數
            number = student_soup.findAll('span',{'class':'number'})
            department = student_soup.table.findAll('a',{'href':re.compile("^\d{6}") })
            count = student_soup.findAll('span',{'style':'display:none'})
            #含區域考生
            student_value = get_value.findall(student.content.decode("utf-8"))
            for s in student_value:
                #print(s[0],s[1],s[2])
                pass
 
            number_list = []
            for n in number:
                number_list.append(n.text)
            assert len(number_list)== len(count), '准考證號資料比數與清單不符'
            
            #通過校系及數目
            for d in department:
                #print(str(d)[9:15] + d.text.split(' ')[0] + d.text.split(' ')[1])
                pass
            all_count = 0
            for c in count:
                all_count = all_count + int(c.text)
            assert len(department) + len(number_list) == all_count, '總系所數目錯誤'

    #curs.execute('INSERT INTO student (id,area,place) VALUES(?,?,?)', (number,)) 
    
    curs.close()
    conn.close()