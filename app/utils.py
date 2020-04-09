from app.models import user_exists
import os
from flask import request, session

ALLOWED_EXTENSIONS = {'mpeg', 'mp4', 'mp3', 'm4a', 'png', 'jpg', 'jpeg', 'gif', 'pdf', 'xls', 'txt', 'mkv', 'x-matroska', 'webm', 'wav', 'avi', 'flv', 'doc', 'docx', 'odt', 'pdf', 'wpd'}

my_path = os.path.abspath(os.path.dirname(__file__))

def allowed_file(filetype):
    for allowed_ext in ALLOWED_EXTENSIONS:
        if allowed_ext in filetype.lower():
            return True
    return False

def signup_util(obj):
    user_info = {}
    user_info['email'] = request.form['email']
    user_info['password'] = request.form['password1']
    if (request.form['isSponsor'] == "Sponsor"):
        user_info['isSponsor'] = 1
    else:
        user_info['isSponsor'] = 0

    user_info['profile'] = {}
    user_info['profile']['fname'] = request.form['fname']
    user_info['profile']['lname'] = request.form['lname']
    user_info['profile']['email'] = request.form['email']
    user_info['profile']['gender'] = request.form['gender']
    user_info['profile']['age'] = request.form['age']
    user_info['profile']['occupation'] = request.form['occupation']
    user_info['profile']['organization'] = request.form['organization']

    user_info['profile']['phone'] = ""
    user_info['profile']['website'] = ""
    user_info['profile']['about'] = ""

    user_info['profile']['address'] = {}
    user_info['profile']['address']['line'] = ""
    user_info['profile']['address']['city'] = ""
    user_info['profile']['address']['country'] = ""

    user_info['profile']['education'] = ""
    user_info['profile']['interest'] = []
    user_info['profile']['language'] = []

    user_info['posts'] = []

    password2 = request.form['password2']

    #Creating a directory for the user so that his/her posts will be available
    directory_path = os.path.join(my_path, '../BLOB', obj.form['email'])
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)

    posts_path = os.path.join(my_path, '../BLOB', obj.form['email'], 'posts')
    if not os.path.exists(posts_path):
        os.mkdir(posts_path)
        
    posts_path = os.path.join(my_path, '../BLOB', obj.form['email'], 'posts', 'images')
    if not os.path.exists(posts_path):
        os.mkdir(posts_path)
        
    posts_path = os.path.join(my_path, '../BLOB', obj.form['email'], 'posts', 'audios')
    if not os.path.exists(posts_path):
        os.mkdir(posts_path)
        
    posts_path = os.path.join(my_path, '../BLOB', obj.form['email'], 'posts', 'videos')
    if not os.path.exists(posts_path):
        os.mkdir(posts_path)
        
    posts_path = os.path.join(my_path, '../BLOB', obj.form['email'], 'posts', 'documents')
    if not os.path.exists(posts_path):
        os.mkdir(posts_path)
        
    return user_info, password2

def login_util(request):
    username = request.form['email']
    password = request.form['pass']
    result = user_exists(username)
    session['name'] = result['profile']['fname'] + " " + result['profile']['lname']
    return result, password, username

def edit_basic_util(request):
    prof = {}
    prof['fname'] = request.form['fname']
    prof['lname'] = request.form['lname']
    prof['phone'] = request.form['phone']
    prof['website'] = request.form['website']
    prof['address'] = request.form['address']
    prof['city'] = request.form['city']
    prof['country'] = request.form['country']
    prof['about'] = request.form['about']
    return prof

def edit_work_util(request):
    prof = {}
    prof['course'] = request.form['course']
    prof['institution'] = request.form['institution']
    prof['occupation'] = request.form['occupation']
    prof['organization'] = request.form['organization']
    return prof

def edit_pass_util(request):
    prof = {}
    prof['new_pass'] = request.form['new_pass']
    prof['con_pass'] = request.form['con_pass']
    prof['cur_pass'] = request.form['cur_pass']
    return prof    

def edit_lan_int_util(request):
    string = request.form['arrval']
    return list(string.split())