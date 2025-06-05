from flask import Flask, render_template, send_from_directory, request
import os
import pymysql
import math

app = Flask(__name__)

CLASSIFIED_DIR = "/app/images/classified"

conn = pymysql.connect(
    host='mariadb',
    user='piuser',
    password='password',
    db='sportsdb',
    port=3306
)

cursor = conn.cursor()

@app.route('/')
def index():
    try:
        all_images = sorted([
            f for f in os.listdir(CLASSIFIED_DIR)
            if os.path.isfile(os.path.join(CLASSIFIED_DIR, f))
        ])
    except FileNotFoundError:
        all_images = []

    classified_only = request.args.get('classified_only', '0') == '1'
    result = []

    for img in all_images:
        cursor.execute("SELECT classification FROM images WHERE filename = %s", (img,))
        row = cursor.fetchone()
        label = row[0] if row else "skipped"
        result.append({"filename": img, "label": label})

    if classified_only:
        result = [item for item in result if item['label'] != 'skipped']

    IMAGES_PER_PAGE = 20
    page = int(request.args.get('page', 1))
    total_pages = math.ceil(len(result) / IMAGES_PER_PAGE)
    paginated_result = result[(page - 1) * IMAGES_PER_PAGE: page * IMAGES_PER_PAGE]

    return render_template("index.html", images=paginated_result, page=page, total_pages=total_pages, classified_only=classified_only)

@app.route('/images/<filename>')
def image(filename):
    return send_from_directory(CLASSIFIED_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
