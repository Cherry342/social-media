import pymysql.cursors
import pymysql
from flask import Flask, render_template,request

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
    return render_template("feed.html.jinja")


@app.route('/feed')
def post_feed():

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM `post` JOIN `users` ON `post`.`user_id`= `users`.`id` ORDER BY `timestamp` DESC;")
    results = cursor.fetchall()

    return render_template(
        "feed.html.jinja",
        posts=results
    )
@app.route('/sign-in')
def sign_in():
    return render_template ("sign_in.html.jinja")
@app.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    if request.method=='POST':
        #Handle signup
        cursor= connection.cursor()
        cursor.execute("""
           INSERT INTO `users` (`id`, `display_name`, `password`, `banned`)
           VALUES(%s,%s,%s, %s, %s, %s)
        """(request))
        return request.form

    elif request.method=='GET':
        return render_template("sign_up.html.jinja")

    return render_template("sign_up.html.jinja")
"""
<input type="file" name= "avatar">
"""
if __name__ == '__main__':
    app.run(debug=True)
