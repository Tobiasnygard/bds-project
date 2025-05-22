#1. 사용자 웹브라우저에서 접속 (http://localhost:5000)
#2. Flask가 MariaDB에서 이미지 목록 가져옴
#3. 이미지 썸네일 + 라벨 정보 테이블로 출력
#4. 이미지 미리보기도 가능 (static 폴더 또는 직접 경로에서 읽음)

from flask import Flask, render_template
import pymysql
import os

app = Flask(__name__)

# DB 연결 설정
db = pymysql.connect(
    host="localhost",
    user="root",
    password="bigdata+",
    database="webscrap",
    charset="utf8"
)

@app.route("/")
def index():
    cursor = db.cursor()
    sql = "SELECT filename, label, saved_path, timestamp FROM image_results ORDER BY timestamp DESC"
    cursor.execute(sql)
    results = cursor.fetchall()

    images = []
    for row in results:
        filename, label, saved_path, timestamp = row

        # 실제 저장 경로
        saved_path = os.path.join("static", "classified_images", label, filename)

        # 웹에서 접근 가능한 경로
        if os.path.exists(saved_path):
            web_path = f"/static/classified_images/{label}/{filename}"
        else:
            web_path = None

        images.append({
            "filename": filename,
            "label": label,
            "path": web_path,
            "timestamp": timestamp
        })


    return render_template("gallery.html", images=images)



if __name__ == "__main__":
    app.run(debug=True)

