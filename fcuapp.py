# coding=utf-8
from flask import Flask,url_for,request,render_template,session,redirect,escape,send_from_directory
import sqlite3
import requests
import json
import os

## http://逢甲資訊.台灣/ Copyright (C) 2017 Leo Sheu.

UPLOAD_FOLDER = 'classtable'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

secretkey = 'Google reCAPTCHA key'

google = {
    'secret' : secretkey,
    'response' : ''
}

@app.route('/' , methods = ['GET', 'POST'])
def index():
    if ('username' in session) : 
        if  request.method == 'POST' : 
            fcu = {
                'Account' : '',
                'Password' : ''
            }
            nid = request.form['nid']
            fcu['Account'] = nid
            fcu['Password'] = request.form['pwd']
            classtable = requests.post("https://service206-sds.fcu.edu.tw/mobileservice/CourseService.svc/Timetable", json = fcu)
            if 'true' in classtable.text:
                table = classtable.json()['TimetableTw']
                creattable(nid, classtable.json())
                filename = nid+'.html'
                return send_from_directory(app.config['UPLOAD_FOLDER'],filename,as_attachment=True)
            
        return 'Logged in as %s ' % escape(session['username']) + '''
            <form action="" method="post"> 
                <p><label>逢甲課表產生器</label>
                <p><label>學號：</label>
                <input type=text name=nid> 
                <p><label>密碼：</label>
                <input type=password name=pwd> 
                <p><input type=submit value= 下載> 
                <label>本系統使用NID驗證登入</label>
                <img src="http://myweb.fcu.edu.tw/~d0381718/img/nid.gif" style="border-width:0px;" />
        '''
    else:
        return redirect(url_for('login'))
    
@app.route ( '/about' ) 
def about(): 
    return 'The about page'
    
@app.route ( '/login', methods = ['GET', 'POST']) 
def  login (): 
    if  request.method == 'POST' : 
        google['response'] = request.form['g-recaptcha-response']
        captcha = requests.post("https://www.google.com/recaptcha/api/siteverify", data = google)
        if (True): #'true' in captcha.text
            session['username']  =  request.form['username'] 
            request.form['password']
        return redirect(url_for('index')) 
    return  ''' 
        <form action="" method="post"> 
            <p><label>帳號：</label>
            <input type=text name=username> 
            <p><label>密碼：</label>
            <input type=password name=password> 
            <script src='https://www.google.com/recaptcha/api.js' async defer></script>
            <div class=g-recaptcha data-sitekey='6LdGuRwUAAAAAGZmBJNNiYYaofqOO9I45e-LP8c_' data-theme=dark ></div>
            <p><input type=submit value= Login> 
    '''

    
@app.route ( '/logout' ) 
def  logout (): 
    session.pop('username', None) 
    return redirect(url_for('index'))
    
def db_search (id, password):
    pass
    
    
def db_add (id, password):
    pass

    
def creattable (name, json):
    timetable = json['TimetableTw']
    row = ['                <tr class="row1">\n', '                <tr class="row2">\n']
    number = [
        '                    <td>第1節<br>08:10~09:00</td>\n',
        '                    <td>第2節<br>09:10~10:00</td>\n',
        '                    <td>第3節<br>10:10~11:00</td>\n',
        '                    <td>第4節<br>11:10~12:00</td>\n',
        '                    <td>第5節<br>12:10~13:00</td>\n',
        '                    <td>第6節<br>13:10~14:00</td>\n',
        '                    <td>第7節<br>14:10~15:00</td>\n',
        '                    <td>第8節<br>15:10~16:00</td>\n',
        '                    <td>第9節<br>16:10~17:00</td>\n',
        '                    <td>第10節<br>17:10~18:00</td>\n',
        '                    <td>第11節<br>18:10~19:00</td>\n',
        '                    <td>第12節<br>19:10~20:00</td>\n',
        '                    <td>第13節<br>20:10~21:00</td>\n',
        '                    <td>第14節<br>21:10~22:00</td>\n'
    ]
    f = open('classtable/'+name+'.html', 'w', encoding = 'utf-8')
    f.write('''<!DOCTYPE>
    <html>
    <head>
        <meta charset="UTF8">
        <title>Course</title>
        <style>
            body { text-align: center; margin: auto; padding-top: 20px;}
            table { text-align: center; margin: auto; border: 2px #FFE9AC solid; width: 90%;}
            tr.row0 { background-color: #760000; color: #EEEEEE}
            tr.row1 { background-color: #FFE9AC; color: #760000}
            tr.row2 { background-color: #FDF0CD; color: #760000}
        </style><style type=text/css> 
        body { font-family: 微軟正黑體; }
        </style>
    </head>
    <body>
        <h1>105學年度第2學期課程資訊(課表)</h1>
        <table>
            <thead>
                <tr class="row0">
                    <th>節次</th>
                    <th>週一</th>
                    <th>週二</th>
                    <th>週三</th>
                    <th>週四</th>
                    <th>週五</th>
                </tr>
            </thead>
            <tbody>
    ''')

    for num in range(1,15):
        f.write(row[num%2])
        f.write(number[num-1])
        for day in range(1,6):
            flag = 0
            for t in timetable:
                if (t['SctWeek'] == day) and (t['SctPeriod'] == num):
                    f.write('                    <td>' + t['SubName'] + '<br>')
                    f.write(t['RomName'])
                    f.write('</td>\n')
                    flag = 1
            if (flag != 1):
                f.write('                    <td></td>\n')
    f.write('                </tr>\n')
    f.write('''
            </tbody>
        </table>
    </body>
    </html>''')
    f.close()


    
if __name__ == '__main__':
    conn = sqlite3.connect('user.db')
    curs = conn.cursor()
    #curs.execute('CREATE TABLE user(id VARCHAR(20) PRIMARY KEY, pass VARCHAR(20))')
    
    app.secret_key = '4g^gE)5G-/g{qagby@Ug+sC<'
    app.debug = True 
    app.run(host = '0.0.0.0')