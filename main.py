from flask import Flask, render_template, flash, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_socketio import SocketIO, emit
import MySQLdb.cursors 
import re
import os
from werkzeug.utils import secure_filename
  
  
app = Flask(__name__)


app.secret_key = 'asdasdas'
  
app.config['MYSQL_HOST'] = 'localhost' 
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'rootroot'
app.config['MYSQL_DB'] = 'pythonlogin'

UPLOAD_FOLDER = 'static/uploads/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED = set(['png', 'jpg', 'jpeg', 'gif','pdf','docx'])
 
def control_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED

@app.route('/upload', methods=['POST'])
def upload_image():

    file = request.files['file']  
    if file.filename == '': 
        return redirect(request.url)
    if file and control_file(file.filename):  
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Your file successfully uploaded. You can copy the url from the textarea below.')
        return render_template('image.html', filename=filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif,pdf,docx')
        return redirect(request.url)
 

mysql = MySQL(app)
  
@app.route('/')
@app.route('/chatAppPage', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form: 
        username = request.form['username'] 
        password = request.form['password'] 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, )) 
        account = cursor.fetchone() 
        if account: 
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('chatAppPage.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)
  
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
  
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    
    return render_template('register.html', msg = msg)



socketio = SocketIO( app )


@app.route( '/image' )
def image():
  return render_template( './image.html' )


@socketio.on( 'my event' )
def handle_my_custom_event( json ):
  print( 'recived my event: ' + str( json ) )
  socketio.emit( 'my response', json)

  
if __name__ == '__main__':
  socketio.run( app, debug = True )


if __name__ =='__main__':
	app.run(debug=True)