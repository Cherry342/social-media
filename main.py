from flask import Flask, render_template,request, redirect, send_from_directory, abort, Blueprint, g

from flask_login import LoginManager, login_required, login_user, current_user,logout_user

import pymysql
import pymysql.cursors
login_manager= LoginManager()

app = Flask(__name__)
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'something_random'
class User:
    def __init__(self , id, username, banned):
       self.is_authenticated=True
       self.is_anonymous = False
       self.is_active= not banned

       self.username= username
       self.id = id

    def get_id(self):
        return str(self.id)


def connect_db():
    return pymysql.connect(
        host="10.100.33.60",
        user="aokagejasmin",
        password="220221337",
        database="aokagejasmin_social_media",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def get_db():
    '''Opens a new database connection per request.'''        
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db    

@app.teardown_appcontext
def close_db(error):
    '''Closes the database connection at the end of request.'''    
    if hasattr(g, 'db'):
        g.db.close() 

connection = pymysql.connect(
    host="10.100.33.60",
    user="aokagejasmin",
    password="220221337",
    database="aokagejasmin_social_media",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)
@app.get('/media/<path:path>')
def send_media(path):
    return send_from_directory('media', path)


@login_manager.user_loader
def user_loader(user_id):
    cursor = get_db().cursor()

    cursor.execute("SELECT * from `users` WHERE `id` = " + user_id)

    result= cursor.fetchone()

    if result is None:
        return None
    
    return User(result['id'], result['username'], result['banned'])
    

@app.route('/')
def index():
    return render_template("feed.html.jinja")


@app.route('/feed')
@login_required
def post_feed():

    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM `post` JOIN `users` ON `post`.`user_id`= `users`.`id` ORDER BY `timestamp` DESC;")
    results = cursor.fetchall()

    return render_template(
        "feed.html.jinja",
        posts=results
    )
@app.route('/post', methods=['POST'])
@login_required
def create_post():
    cursor = get_db().cursor()
    photo = request.files['post_image']

    file_name=photo.filename #my_photo.jpg

    file_extension= file_name.split ('.')[-1]

    if file_extension.lower() in ['jpg', 'jpeg', 'png', 'gif']:
        photo.save('media/posts/' + file_name)
    else:
        raise Exception('Invaild file type')
    
    user_id= current_user.id




    post_text_id=request.form["post_text"]
    
    cursor.execute("""INSERT INTO `post` (`post_text`, `post_image`, `user_id`) VALUES (%s, %s, %s)""",
                   (request.form['post_text'], file_name , user_id,))

    return redirect('/feed')
    
@app.route('/sign-out')
def sign_out():
    logout_user()
    return redirect('/sign_in')
@app.route('/sign-in', methods=['POST', 'GET'])
def sign_in():
    if current_user.is_authenticated:
        return redirect('/feed')
    
    if request.method =='POST':
        cursor = get_db().cursor()

        cursor.execute(f"SELECT * FROM `users` WHERE `username` = '{request.form['username']} '")

        result=cursor.fetchone()

        if result is None:
            return render_template("sign_in.html.jinja")
        if request.form['password'] == result['password']:
            user=User(result['id'], result['username'], result['banned'])
            login_user(user)

            return redirect('/feed')
            
        else:
            return render_template("sign_in.html.jinja")
        return request.form
        
           # do something
    elif request.method=='GET':

        return render_template ("sign_in.html.jinja")
        
        

@app.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    if current_user.is_authenticated:
        return redirect('/feed')
    if request.method=='POST':
        #Handle signup
        cursor = get_db().cursor()
        photo=request.files['photo']

        file_name= photo.filename #my_photo.jpg
        file_extentsion= file_name.split('.')[-1]
        if file_extentsion in ['jpg', 'jpeg', 'png' , 'gif']:
            photo.save('media/users/' + file_name)
        else:
            raise Exception('Invaild file type')

        cursor.execute("""
           INSERT INTO `users` (`username`, `email`, `display_name`, `password`, `bio`, `photo`)
           VALUES(%s, %s, %s, %s, %s, %s)
        """,(request.form['username'], request.form['email'] , request.form['display_name'], request.form['password'], request.form['bio'], file_name ))
        return redirect('/feed')
    elif request.method=='GET':
        return render_template("sign_up.html.jinja")
     

    return render_template("sign_up.html.jinja")
"""
<input type="file" name= "avatar">
"""

@app.route('/profile/<username>')
def user_profile(username):
    cursor = get_db().cursor()

    cursor.execute("SELECT * FROM `users` WHERE `username` = %s", (username))

    result= cursor.fetchone()
    if result is None:
        abort(404)
    cursor.close()
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM `post` WHERE `user_id` = %s  ORDER BY `timestamp`", (result['id']))

    post_result= cursor.fetchall()
    return render_template(
        "user_profile.html.jinja",
        user=result,
        posts=post_result
    )
   
@app.errorhandler(404)
def error_404(error):
    return render_template('404.html.jinja'), 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)



