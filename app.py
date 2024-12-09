from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2
from psycopg2 import sql

app = Flask(__name__)
app.secret_key = "secret_key"

# إعداد الاتصال بقاعدة البيانات
def get_db_connection():
    conn = psycopg2.connect(
        host="host.docker.internal",  # تأكد من أن Docker يسمح بالاتصال بـ `host.docker.internal`
        database="warehouse_sys",
        user="admin",
        password="12345",
        port=5433
    )
    return conn

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                sql.SQL("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"),
                (username, email, password)
            )
            conn.commit()
            flash('تم التسجيل بنجاح! يمكنك الآن تسجيل الدخول.', 'success')
            return redirect(url_for('login'))
        except psycopg2.Error as e:
            flash('حدث خطأ أثناء التسجيل: {}'.format(e), 'danger')
        finally:
            cursor.close()
            conn.close()
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            sql.SQL("SELECT * FROM users WHERE email = %s AND password = %s"),
            (email, password)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            session['user_id'] = user[0]
            flash('مرحبًا {}! تم تسجيل الدخول بنجاح.'.format(user[1]), 'success')
            return redirect(url_for('home'))
        else:
            flash('البريد الإلكتروني أو كلمة المرور غير صحيحة.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('تم تسجيل الخروج بنجاح.', 'success')
    return redirect(url_for('home'))

if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(host="localhost", port=5000, debug=True)
