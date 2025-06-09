# pi4_app.py

from flask import Flask, render_template, request, make_response, Response, url_for
import pymysql
import math

app = Flask(__name__)

def get_db_connection():
    return pymysql.connect(
        host='mariadb',
        user='piuser',
        password='password',
        db='sportsdb',
        port=3306,
        cursorclass=pymysql.cursors.DictCursor  # So fetchone()/fetchall() return dicts
    )

@app.route('/')
def index():
    # 1) Fetch the "classified_only" flag from query parameters
    classified_only = (request.args.get('classified_only', '0') == '1')

    # 2) Open a fresh DB connection & cursor
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if classified_only:
                cursor.execute(
                    "SELECT id, classification FROM images WHERE classification <> 'skipped'"
                )
            else:
                cursor.execute(
                    "SELECT id, classification FROM images"
                )
            rows = cursor.fetchall()  # list of dicts: [{'id': ..., 'classification': ...}, ...]
    finally:
        conn.close()

    # 3) Paginate (20 images per page)
    IMAGES_PER_PAGE = 20
    page = int(request.args.get('page', 1))
    total_pages = math.ceil(len(rows) / IMAGES_PER_PAGE)
    start = (page - 1) * IMAGES_PER_PAGE
    end = page * IMAGES_PER_PAGE
    paginated_rows = rows[start:end]

    # 4) Render the template, then add HTTP headers to prevent browser caching
    rendered = render_template(
        "index.html",
        images=paginated_rows,      # each item has 'id' and 'classification'
        page=page,
        total_pages=total_pages,
        classified_only=classified_only
    )
    response = make_response(rendered)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/images/<int:image_id>')
def serve_image(image_id):
    """
    Fetch the raw image bytes (BLOB) from MariaDB by its auto-increment ID,
    then return it with the correct mimetype.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT image_blob FROM images WHERE id = %s",
                (image_id,)
            )
            row = cursor.fetchone()
    finally:
        conn.close()

    if not row:
        return "Not found", 404

    blob = row['image_blob']
    # Assuming all stored images are JPEG; if you store mixed types, you could add a 'mime_type' column
    return Response(blob, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
