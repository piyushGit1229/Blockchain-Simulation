from flask import Flask,redirect,request,render_template,url_for,flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'secretkey'

def init_db():
    conn=sqlite3.connnect("database.db")
    cursor=conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


    @app.route('/')
    def intro():
        return render_template('intro.html')
    
    @app.route('/signup',methods=['GET','POST'])
    def signup():
      if request.method=='POST':
         username=request.form['username']
         password=request.form['password']

         try:
            conn=sqlite3.connect("database.db")
            cursor=conn.cursor()
            cursor.execute("INSERT INTO users (username,password) VALUES (?,?)",(username,password))
            conn.commit()
            conn.close()
            flash("ACCOUNT CREATED SUCCESSFULLY,PLEASE LOGIN","success")
            return(redirect(url_for('login')))
         except sqlite3.IntegrityError:
            flash("USERNAME ALREADY EXISTS","error")

    return render_template(url_for('signup.html'))
 
       


    
@app.route('/login',methods=['GET','POST'])
def login():
      if request.method=='POST':
         username=request.form['username']
         password=request.form['password']


         conn=sqlite3.connect("database.db")
         cursor=conn.cursor()
         cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
         user = cursor.fetchone()
         conn.close()
         conn.close()

         if user:
            flash("Login successful!", "success")
            return redirect(url_for('index'))
         else:
            flash("Invalid username or password. Please try again.", "error")

      return render_template('login.html')
       
@app.route('/main')
def main():
   return render_template('index.html')


if __name__=="__main__":
   init_db
   app.run(debug=True)








