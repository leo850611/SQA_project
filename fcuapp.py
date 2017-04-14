# coding=utf-8
from flask import Flask,url_for,request,render_template,session,redirect,escape,send_from_directory
import sqlite3
import requests
import json
import re

## http://逢甲資訊.台灣/ Copyright (C) 2017 Leo Sheu.

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'download'
secretkey = 'Google reCAPTCHA key'


@app.route('/' , methods = ['GET', 'POST'])
def index():
    if ('username' in session) : 
        if  request.method == 'POST' : 
            fcu = {
                'Account' : '',
                'Password' : ''
            }
            nid = request.form['nid'].upper()
            password = request.form['pwd']
            if (len(nid)>5) and (len(password)>5):
                header = {
                    'Connection' : 'keep-alive',
                    'Content-Type' : 'text/json',
                    'Host' : 'service206-sds.fcu.edu.tw',
                    'User-Agent' : 'Mozilla/5.0 (Linux; Android 5.1.1; D6653 Build/23.4.A.1.232; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 Mobile Safari/537.36'
                }
                fcu['Account'] = nid
                fcu['Password'] = password
                classtable = requests.post("https://service206-sds.fcu.edu.tw/mobileservice/CourseService.svc/Timetable", json = fcu, headers = header)
                if 'true' in classtable.text:
                    table = classtable.json()['TimetableTw']
                    language = 0
                    if request.form['language'] != '1':
                        language = 1
                    creattable(nid, classtable.json(), language)
                    filename = nid+'.html'
                    return send_from_directory(app.config['UPLOAD_FOLDER'],filename,as_attachment=True)
                else:
                    return alertmsg('不要亂填害林杯被查水表好嗎(┛`д´)┛')

        return 'Username : %s ' % escape(session['username']) + render_template('classtable.html')
    else:
        return redirect(url_for('login'))
    
@app.route ( '/about' ) 
def about(): 
    return 'The about page'
    
@app.route ( '/login', methods = ['GET', 'POST']) 
def  login (): 
    if  request.method == 'POST' : 
        username = request.form['username'] 
        password = request.form['password']
        if (20>=len(username)>=5) and (20>=len(password)>=5):
            conn = sqlite3.connect('iecs.db')
            curs = conn.cursor()

            curs.execute("SELECT pwd FROM user WHERE id=:id ", {"id": username})
            
            pwddata = curs.fetchall()
            try:
                pwd = str(pwddata[0])[2:-3]
            except:
                pwd = ''
            if pwd == password:
                session['username'] = username
                return redirect(url_for('index'))
    return render_template ('login.html')

    
@app.route ( '/logout' ) 
def logout (): 
    session.pop('username', None) 
    return redirect(url_for('login'))

@app.route ( '/register', methods = ['GET', 'POST'])    
def register():
    google = {
        'secret' : secretkey,
        'response' : ''
    }
    if  request.method == 'POST' : 
        google['response'] = request.form['g-recaptcha-response']
        captcha = requests.post("https://www.google.com/recaptcha/api/siteverify", data = google)
        if ('true' in captcha.text): #True
            id = request.form['username']
            mail = request.form['email']
            pwd1 = request.form['password1']
            pwd2 = request.form['password2']
            
            if (pwd1 != pwd2):
                return alertmsg('Error：兩次輸入密碼不一致')
            if (len(id)<5) or (len(id)>20) or (len(pwd1)<5) or (len(pwd1)>20):
                return alertmsg('Error：使用者名稱或密碼長度錯誤')
            if (len(mail)<6) or (len(mail)>40):
                return alertmsg('Error：email長度錯誤')
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", mail) == None:
                return alertmsg('Error：email格式錯誤')
            
            conn = sqlite3.connect('iecs.db')
            curs = conn.cursor()
            try:
                curs.execute('INSERT INTO user(id,mail,pwd) VALUES(?,?,?)', (id,mail,pwd1) )
            except:
                return alertmsg('ERROR：使用者名稱已存在')
            conn.commit()
            curs.execute('SELECT * from user')
            print(curs.fetchall())
            return alertmsg('註冊成功，請回登入頁面開始使用！')
        else:
            return alertmsg('你是機器人？')
    return  render_template ( 'register.html')


@app.route ( '/forget', methods = ['GET', 'POST'])    
def forget():
    google = {
        'secret' : secretkey,
        'response' : ''
    }
    return ""    
    
    
def alertmsg(msg):
    return '''
    <script>
        alert(' ''' + msg + ''' ');
        window.history.go(-1);
    </script>'''

def db_search (id, password):
    pass
    
    
def creattable (name, json, language):
    if language is 0:
        timetable = json['TimetableTw']
    else:
        timetable = json['TimetableEn']
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
    f = open('download\\'+name+'.html', 'w', encoding = 'utf-8')
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
        <h1>105學年度第2學期課程資訊</h1>
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
                    try:
                        f.write(t['RomName'])
                    except:
                        pass
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
    #curs.execute('CREATE TABLE user(id VARCHAR(20) PRIMARY KEY, mail VARCHAR(40), pwd VARCHAR(20))')
    app.secret_key = '4g^gE)5G-/g{qagby@Ug+sC<'
    app.debug = True 
    app.run(host = '0.0.0.0')