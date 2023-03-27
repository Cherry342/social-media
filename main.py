import pymysql.cursors
import pymysql
from flask import Flask, render_template

app = Flask(__name__)

connection = pymysql.connect(
    host="10.100.33.60",
    user="aokagejasmin",
    password="220221337",
    database="aokagejasmin_social_media",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)


@app.route('/')
def index():
    return render_template("home.html.jinja")


@app.route('/feed')
def post_feed():

    cursor = connection.cursor()
    cursor.exectute("SELECT  * FROM `posts` ORDER BY `timesstamp`")
    results = cursor.fetchall()

    return render_template(
        "feed.html.jinja",
        posts=results
    )

if __name__ == '__main__':
    app.run(debug=True)
