# coding=utf-8
import sqlite3
## Copyright (C) 2017 Leo Sheu. <loli>

def student_part():
    cursor = curs.execute('SELECT area , COUNT(*) from place GROUP BY area')
    ##[('中部', 14086), ('北部', 28364), ('南部', 14355), ('東部', 2339), ('離島', 509)]
    all_student = 0
    part_list = []
    for i in cursor:
        part_list.append([i[0], str(i[1])])
        all_student = all_student + i[1]
    for i in part_list:
        print(i[0] + ': '+str(i[1])+'人, '+ str(int(i[1])/all_student) )
    print('總考生人數: '+ str(all_student))    
    
    
    
if __name__ == '__main__':
    #school, department, person, place
    conn = sqlite3.connect('106.db')
    curs = conn.cursor()
    student_part()
    
    curs.close()
    conn.close()
    