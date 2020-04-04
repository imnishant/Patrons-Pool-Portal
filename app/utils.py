from app.models import user_exists
import os

ALLOWED_EXTENSIONS = {'mpeg', 'mp4', 'mp3', 'm4a', 'png', 'jpg', 'jpeg', 'gif', 'pdf', 'xls', 'txt', 'mkv', 'x-matroska', 'webm'}

my_path = os.path.abspath(os.path.dirname(__file__))

def allowed_file(filetype):
    for allowed_ext in ALLOWED_EXTENSIONS:
        if allowed_ext in filetype.lower():
            return True
    return False

def signup_util(obj):
    user_info = {}
    user_info['fname'] = obj.form['fname']
    user_info['lname'] = obj.form['lname']
    user_info['gender'] = obj.form['gender']
    user_info['age'] = obj.form['age']
    user_info['password'] = obj.form['password1']
    user_info['email'] = obj.form['email']
    user_info['occupation'] = obj.form['occupation']
    user_info['organization'] = obj.form['organization']

    #Creating a directory for the user so that his/her posts will be available
    directory_path = os.path.join(my_path, '../BLOB', obj.form['email'])
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)

    posts_path = os.path.join(my_path, '../BLOB', obj.form['email'], 'posts')
    if not os.path.exists(posts_path):
        os.mkdir(posts_path)

    return user_info

def login_util(request):
    username = request.form['email']
    password = request.form['pass']
    result = user_exists(username)
    return result, password, username
