from flask import Flask, render_template, request, session, redirect, url_for, g, flash
import sqlite3 as sql
import requests
import os
import flask_sijax
from passlib.hash import sha256_crypt
from wtforms import Form, BooleanField, TextField, PasswordField, validators
path = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')

app = Flask(__name__)
app.config['SIJAX_STATIC_PATH'] = path
app.config['SIJAX_JSON_URI'] = '/static/js/sijax/json2.js'
flask_sijax.Sijax(app)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/register', methods=["GET","POST"])
def register_page():
    try:
        form = request.form
        if request.method == "POST":
            username  = form['inputName']
            email = '"' + form['inputEmail'] + '"'
            password = '"' + sha256_crypt.hash((str(form['inputPassword']))) + '"'
            con = sql.connect("eComDB.db")
            con.row_factory = sql.Row
            cur = con.cursor()

            username = '"' + username + '"'
            app.logger.debug(username + ' ' + password + ' ' + email)
            cur.execute("SELECT * FROM username WHERE username = %s" % username)
            x = cur.fetchone()
            if x is not None:
                return 'existing'

            else:
                cur.execute("INSERT INTO username (username, password, email) VALUES (" + username + ", " + password + ", " + email + ')')                       
                
                con.commit()
                flash("Thanks for registering!")
                con.close()

                return redirect(url_for('home'))

        return render_template("register.html")

    except Exception as e:
        return(str(e))

@app.route('/')
def loginpage():
    if 'username' in session:
        return redirect(url_for('home'))
    else:
        if 'flag' in request.args:
            return render_template('loginpage.html',  flag='true')
        else:
            return render_template('loginpage.html')

@app.route('/userData')
def userData():
    con = sql.connect("eComDB.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select ud.Iid,  i.title, i.ingredients   from items as i  join userData as ud on ud.Iid = i.id where ud.Uid = %i"% int(session['id']))
    rows = cur.fetchall()
    if(len(rows) == 0):
        return render_template('userData.html', flag='true', user=session["username"], rows=rows)
    else:
        return render_template('userData.html', user=session["username"], rows=rows)
        

@app.route('/recommended')
def recommended():
    return '333'


@flask_sijax.route(app, '/home')
def home():
    if 'username' in session:
        con = sql.connect("eComDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("select * from items order by RANDOM() limit 100")
        rows = cur.fetchall()
        cur.execute('select Iid from userData where Uid = %i' % int(session['id']))
        items = cur.fetchall()

        p = 'http://127.0.0.1:5000/buildAlgorithm?flag=related'
        r = requests.get(p)
        items = [item['Iid'] for item in items]
        [rows.remove(row) for row in rows if(row['id'] in items)]
        username = session["username"]

        def userChoose(obj_response, arg1):
                con = sql.connect("eComDB.db")
                con.row_factory = sql.Row
                cur = con.cursor()
                cur.execute("INSERT INTO userData (Uid, Iid) VALUES (?,?)",(session['id'], arg1))
                con.commit()
                
                cur.execute("select title from items where id = %a" % int(arg1))
                row = cur.fetchone()
                
                con.close()
                
        if g.sijax.is_sijax_request:
                # Sijax request detected - let Sijax handle it
                g.sijax.register_callback('userChoose', userChoose)
                return g.sijax.process_request()
        con.close()
        return render_template('chooseFood.html', user=username, items=rows)
    else:
        if 'flag' in request.args:
            return render_template('loginpage.html',  flag='true')
        else:
            return render_template('loginpage.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == "POST":
        credentials = request.form
        con = sql.connect("eComDB.db")
        con.row_factory = sql.Row

        cur = con.cursor()
        sqlQ = "select * from username where username={} limit 1"
        sqlQ = sqlQ.format('"' + credentials['user'] + '"') 
        cur.execute(sqlQ)
        rows = cur.fetchone()
        if(rows is None):
            return redirect(url_for('loginpage', flag='true'))
        else:
            if sha256_crypt.verify(credentials['pass'], rows['password']):
                session['username'] = credentials['user']
                session['id'] = rows['id']
                return redirect(url_for('home'))
            else:
                return redirect(url_for('loginpage', flag='true'))
    else:
        return redirect(url_for('loginpage'))

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('id', None)
    return redirect(url_for('loginpage'))

@app.route('/list')
def list():
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("select * from students")
   
   rows = cur.fetchall()
   return render_template("list.html",rows = rows)

if __name__ == '__main__':
   app.run(debug = True, port=80)