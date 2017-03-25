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
    print(curs.fetchall()) ##(1, '國立臺灣大學')

    for school_num in school_list:
        #科系代號及名稱
        department_page = requests.get('http://freshman.tw/cross/106/' + str(school_num[0]))
        department_soup = BeautifulSoup(department_page.text, "html.parser")
        department_num = department_soup.findAll('a',{'class':'d-block'})
        for department in department_num:
            try: ##011412
                curs.execute('INSERT INTO department (snum,dnumber,dname) VALUES(?,?,?)', (int(school_num[0]),str(department)[25:31],department.text))            
            except:
                pass
    conn.commit() 
    curs.execute('SELECT * from department ORDER BY dnumber')
    print(curs.fetchall()) ##(153, '153172', '都市計畫與景觀學系')
    
    
if __name__ == '__main__':
    conn = sqlite3.connect('106.db')
    curs = conn.cursor()
    school_db()
    
    reg = r'<span class="number">(\d+)</span><div style="font-size:12px;">([^0-9]+)-([^0-9]+)考區</div></td>' ##10206020,中部,彰化
    get_value = re.compile(reg)
    curs.execute('CREATE TABLE person(pnumber INT, dnumber CHAR(6), pschool VARCHAR(20), pdepartment VARCHAR(50))')
    curs.execute('CREATE TABLE place(pnum INT, area CHAR(4),local CHAR(4))')
    curs.execute('SELECT * from department ORDER BY dnumber')
    department_list = curs.fetchall()
    id_list = []
    
    for dnum in department_list:
        print(dnum)
        page_id = dnum[1]
        if(('音樂'not in dnum[2]) and (int(page_id)>= 0 )):
            #學生及通過校系
            student = requests.get('http://freshman.tw/cross/106/'+ dnum[1])
            student_soup = BeautifulSoup(student.text, "html.parser")
            page_title = student_soup.title.text
            #准考證號,通過校系,校系數量
            number = student_soup.findAll('span',{'class':'number'})
            department = student_soup.table.findAll('a') #,{'href':re.compile("^\d{6}") }
            count = student_soup.findAll('span',{'style':'display:none'})
            
            #含區域資料學生
            student_value = get_value.findall(student.content.decode("utf-8"))
            for s in student_value:
                if(s[0] not in id_list):
                    ##('10006201', '北部', '台北')
                    curs.execute('INSERT INTO place (pnum,area,local) VALUES(?,?,?)', (int(s[0]), s[1], s[2]) )
 
            #准考證號
            number_list = []
            for n in number:
                number_list.append(n.text)
            assert len(number_list)== len(count), '准考證號資料比數與清單不符'
            #通過校系數目
            all_count = 0
            count_list = []
            for c in count:
                count_list.append(int(c.text))
                all_count = all_count + int(c.text)
            assert len(department) == all_count, '總系所數目錯誤'
            
            i = 0
            for d in department:
                count_list[i] = count_list[i] - 1
                #print(number_list[i], str(d)[9:15], d.text.split(' ')[0], d.text.split(' ')[1])
                if(number_list[i] not in id_list):
                    curs.execute('INSERT INTO person (pnumber,dnumber,pschool,pdepartment) VALUES(?,?,?,?)', (number_list[i], str(d)[9:15], d.text.split(' ')[0], d.text.split(' ')[1]) )
                    id_list.append(number_list[i])
                if(count_list[i] == 0):
                    i = i+1
            print(id_list)
            time.sleep(3)
        conn.commit()
    curs.close()
    conn.close()