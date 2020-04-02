from app import db
from app.models import user_exists, save_user

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
    return user_info

def login_util(request):
    username = request.form['email']
    password = request.form['pass']
    result = user_exists(username)
    return result