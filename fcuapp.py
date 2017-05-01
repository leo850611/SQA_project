# coding=utf-8
from flask import Flask,url_for,request,render_template,session,redirect,escape,send_from_directory,flash
import sqlite3
import requests
import json
import re
import time
import datetime
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.header import Header

## 逢甲資訊.台灣 Copyright (C) 2017 Leo Sheu.

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'download'

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
appkey = ''
secretkey = 'Google reCAPTCHA key' 
mailpassword = ''


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


@app.route('/course' , methods = ['GET', 'POST'])
def course():
    if ('username' in session) : 
        if  request.method == 'POST' : 
            return alertmsg('尚未開放，敬請期待~')
        return 'Username : %s ' % escape(session['username']) + render_template('course.html')
    else:
        return redirect(url_for('login'))


@app.route('/library' , methods = ['GET', 'POST'])
def library():
    if ('username' in session) : 
        if  request.method == 'POST' : 
            nid = request.form['nid']
            password = request.form['pwd']
            if (len(nid)>5):
                flash(autorenew(nid, password))
                return redirect(url_for('library'))
            else:
                flash('帳號或密碼錯誤')
                return redirect(url_for('library'))
        return 'Username : %s ' % escape(session['username']) + render_template('library.html')
    else:
        return redirect(url_for('login'))


@app.route('/about') 
def about(): 
    return render_template('about.html')


@app.route('/login', methods = ['GET', 'POST']) 
def login(): 
    if  request.method == 'POST' : 
        username = request.form['username'] 
        password = request.form['password']
        print(username +' '+ password)
        if (20>=len(username)>=5) and (20>=len(password)>=5):
            conn = sqlite3.connect('iecs.db')
            curs = conn.cursor()
            curs.execute("SELECT pwd FROM user WHERE id=:id ", {"id": username})
            pwddata = curs.fetchall()
            try:
                pwd = str(pwddata[0])[2:-3]
                if pwd == password:
                    session['username'] = username
                    return redirect(url_for('index'))
            except:
                pass
            
    return render_template('login.html')


@app.route('/logout') 
def logout(): 
    session.pop('username', None) 
    return redirect(url_for('login'))


@app.route('/register', methods = ['GET', 'POST'])    
def register():
    if request.method == 'POST' : 
        if (recaptcha(request.form['g-recaptcha-response'])): #True
            id = request.form['username']
            mail = request.form['email']
            pwd1 = request.form['password1']
            pwd2 = request.form['password2']
            
            if (pwd1 != pwd2):
                flash('Error：兩次輸入密碼不一致')
                return redirect(url_for('register'))
            if (len(id)<5) or (len(id)>20) or (len(pwd1)<5) or (len(pwd1)>20):
                flash('Error：使用者名稱或密碼長度錯誤')
                return redirect(url_for('register'))
            if (len(mail)<6) or (len(mail)>40):
                flash('Error：email長度錯誤')
                return redirect(url_for('register'))
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", mail) == None:
                flash('Error：無效的email格式')
                return redirect(url_for('register'))
            
            conn = sqlite3.connect('iecs.db')
            curs = conn.cursor()
            try:
                curs.execute('INSERT INTO user(id,mail,pwd) VALUES(?,?,?)', (id,mail,pwd1) )
            except:
                flash('ERROR：使用者名稱已存在')
                return redirect(url_for('register'))
            conn.commit()
            curs.execute('SELECT * from user')
            print(curs.fetchall())
            flash('註冊成功，請回登入頁面開始使用！')
            return redirect(url_for('register'))
        else:
            flash('你是機器人？')
            return redirect(url_for('register'))
    return render_template ( 'register.html')


@app.route('/forget', methods = ['GET', 'POST'])    
def forget():
    if request.method == 'POST' : 
        if (recaptcha(request.form['g-recaptcha-response'])): #True
            username = request.form['username']
            if (20>=len(username)>=5):
                conn = sqlite3.connect('iecs.db')
                curs = conn.cursor()
                curs.execute("SELECT pwd FROM user WHERE id=:id ", {"id": username})
                pwddata = curs.fetchall()
                try:
                    pwd = str(pwddata[0])[2:-3]
                    curs.execute("SELECT mail FROM user WHERE id=:id ", {"id": username})
                    mail = curs.fetchall()
                    email = str(mail[0])[2:-3]
                    sendmail(email, pwd)
                except:
                    pass
                flash('已寄出，請檢查信箱！')
                return redirect(url_for('forget'))
        else:
            flash('你是機器人？')
            return redirect(url_for('forget'))
    return render_template('forget.html')


@app.route('/106') 
def analysis106():
    if ('username' in session) :
        return 'Username : %s ' % escape(session['username']) + render_template('106.html')
    else:
        return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def alertmsg(msg):
    return '''
    <script>
        alert(' ''' + msg + ''' ');
        window.history.go(-1);
    </script>'''

def recaptcha(response):
    google = {
        'secret' : secretkey,
        'response' : ''
    }
    google['response'] = response
    captcha = requests.post("https://www.google.com/recaptcha/api/siteverify", data = google)
    if ('true' in captcha.text):
        return True
    else:
        return False

        
def cleckday(datestr):
    m = datestr.split('-')[0]
    d = datestr.split('-')[1]
    y = datestr.split('-')[2]
    today = datetime.date.today()
    other_day = datetime.date(int(y)+2000,int(m),int(d))
    result = other_day - today
    return result.days
    
def autorenew(nid, password):
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4,ja;q=0.2',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
    }
    session = requests.Session()
    if len(nid) == 8:
        nid = nid + '0'
    logininfo = {
        'code': nid,
        'pin': password,
        'submit':'送出'
    }
    start = session.post("https://innopac.lib.fcu.edu.tw/patroninfo*cht", data = logininfo, headers = header)
    books = session.get("https://innopac.lib.fcu.edu.tw/patroninfo~S9*cht/1128531/items")
    if('請輸入密碼' in books.text):
        return ('帳號或密碼錯誤')
    else:
        booksoup = BeautifulSoup(books.text, "html.parser")
        day = booksoup.findAll('td',{'class':'patFuncStatus'})
        id = booksoup.findAll('input',{'type':'checkbox'})
        renew = {
            'currentsortorder':'current_checkout',
            'currentsortorder':'current_checkout',
            'requestRenewSome':'續借選取館藏'
        }
        if len(day) !=0 :
            flag = 0
            for i in range(len(day)):
                if cleckday(day[i].text.split(' ')[2]) <= 5:
                    renew.setdefault(id[i]['id'], id[i]['value'])
                    flag = flag +1
            if flag > 0:
                session.post("https://innopac.lib.fcu.edu.tw/patroninfo~S9*cht/1128531/items", data = renew, headers = header)
                renew.pop('requestRenewSome')  
                renew.setdefault('renewsome', '是')
                result = session.post("https://innopac.lib.fcu.edu.tw/patroninfo~S9*cht/1128531/items", data = renew, headers = header)
                if '<font color="red">' not in result.text:
                    return ('成功續借' + str(flag) +'本書')
                else:
                    return ('續借失敗，書籍將在5天內到期')
            else:
                return ('您的書籍還不需續借')
        else:
            return ('您沒有任何館藏借出')


def creattable(name, json, language):
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


def sendmail(recipient, password):
    smtpObj = smtplib.SMTP_SSL('mail.gandi.net', 465)
    smtpObj.ehlo()
    smtpObj.login('no-reply@fcu.com.tw', mailpassword)
    message = MIMEText('''
    此為自動回覆電子郵件，將協助您恢復您對帳號的存取權限。

    登入密碼：'''+ password + '''\n--
    逢甲小幫手 - https://逢甲資訊.台灣''', 'plain', 'utf-8')
    message['From'] = Header("no-reply@fcu.com.tw", 'utf-8')
    message['To'] =  Header(recipient, 'utf-8') 
    subject = '逢甲小幫手 忘記密碼'
    message['Subject'] = Header(subject, 'utf-8')
    smtpObj.sendmail('no-reply@fcu.com.tw', recipient, message.as_string() )
    print('send mail: '+ recipient)
    smtpObj.quit()


if __name__ == '__main__':
    conn = sqlite3.connect('iecs.db')
    curs = conn.cursor()
    #curs.execute('CREATE TABLE user(id VARCHAR(20) PRIMARY KEY, mail VARCHAR(40), pwd VARCHAR(20))')
    app.secret_key = appkey
    app.debug = True 
    app.run(host = '0.0.0.0')
    