# coding=utf-8
import sqlite3
from matplotlib import pyplot as plt

## Copyright (C) 2017 Leo Sheu. <loli>

#school(snumber INT, sname)
#department(snum INT, dnumber, dname)
#person(pnumber INT, dnumber, pschool, pdepartment)
#place(pnum INT, area, local)
def student_part():   
    cursor = curs.execute('SELECT area , COUNT(*) from place GROUP BY area')
    ##[('中部', 14086), ('北部', 28364), ('南部', 14355), ('東部', 2339), ('離島', 509)]
    all_student = 0
    part_list = []
    for i in cursor:
        part_list.append([i[0], str(i[1])])
        all_student = all_student + i[1]
    for i in part_list:
        print(i[0] + ': '+str(i[1])+'人, '+ format(int(i[1])/all_student,'.2f'))
    print('總考生人數: '+ str(all_student))    
    plt.pie(
    (part_list[0][1],part_list[1][1],part_list[2][1],part_list[3][1],part_list[4][1]),
    labels=(part_list[0][0],part_list[1][0],part_list[2][0],part_list[3][0],part_list[4][0]),
    colors=('gold', 'yellowgreen', 'lightcoral', 'lightskyblue', 'magenta'),
    autopct='%1.2f%%',# display fraction as percentage
    )
    plt.title('考生區域分佈')
    plt.legend(fancybox=True)
    plt.axis('equal')     # plot pyplot as circle
    plt.tight_layout()
    plt.show()
    
def csie_part():
    cursor = curs.execute("SELECT DISTINCT * FROM person WHERE  pdepartment LIKE '%%資訊工程%%' ")
    print(curs.fetchall()) 
    for i in cursor:
        print(i)
        
def list_department():
    cursor = curs.execute('SELECT * from department')
    print(curs.fetchall()) 
    
def list_place():
    cursor = curs.execute('SELECT * from place')
    print(curs.fetchall())  
    
if __name__ == '__main__':
    #school, department, person, place
    conn = sqlite3.connect('106.db')
    curs = conn.cursor()
    #student_part()
    #list_department()
    csie_part()
    curs.close()
    conn.close()
    
# 解決matplotlib中文亂碼問題    
# import matplotlib
# print (matplotlib.matplotlib_fname())
#(matplotlibrc) font.family : Source Han Sans TWHK