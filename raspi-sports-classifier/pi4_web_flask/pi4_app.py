from flask import Flask, render_template
import pymysql

app = Flask(__name__)

def get_data():
    conn = pymysql.connect(host='<pi2_ip>', user='piuser', password='password', db='sportsdb')
    cursor = conn.cursor()
    cursor.execute("SELECT url, source, classification, timestamp FROM images ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

@app.route('/')
def index():
    data = get_data()
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
