from app.models import user_exists
import os
import shutil
from flask import request, session
import base64
import onetimepass

ALLOWED_EXTENSIONS = {'mpeg', 'mp4', 'mp3', 'm4a', 'png', 'jpg', 'jpeg', 'gif', 'pdf', 'xls', 'xlsx', 'txt', 'mkv', 'x-matroska', 'webm', 'wav', 'avi', 'flv', 'doc', 'docx', 'odt', 'wpd'}

my_path = os.path.abspath(os.path.dirname(__file__))


def allowed_file(filetype):
    for allowed_ext in ALLOWED_EXTENSIONS:
        if allowed_ext in filetype.lower():
            return True
    return False


def signup_util(obj):
    user_info = {}
    user_info['email'] = request.form['email']
    password = request.form['password1']
    user_info['password'] = base64.b64encode(password.encode('ascii')).decode('ascii')
    user_info['wallet_address'] = request.form['wallet_address']
    user_info['otp_secret'] = base64.b32encode(os.urandom(10)).decode('utf-8')

    if (request.form['isSponsor'] == 'sponsor'):
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
    user_info['profile']['cover'] = 'cover.jpg'
    user_info['profile']['display'] = 'display.png'

    user_info['posts'] = []

    password2 = base64.b64encode((request.form['password2']).encode('ascii')).decode('ascii')

    #Creating a directory for the user so that his/her posts will be available
    directory_path = os.path.join(my_path, 'static/BLOB')
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)

    directory_path = os.path.join(my_path, 'static/BLOB', obj.form['email'])
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)

    posts_path = os.path.join(my_path, 'static/BLOB', obj.form['email'], 'posts')
    if not os.path.exists(posts_path):
        os.mkdir(posts_path)
        
    posts_path = os.path.join(my_path, 'static/BLOB', obj.form['email'], 'posts', 'images')
    if not os.path.exists(posts_path):
        os.mkdir(posts_path)
        
    posts_path = os.path.join(my_path, 'static/BLOB', obj.form['email'], 'posts', 'audios')
    if not os.path.exists(posts_path):
        os.mkdir(posts_path)
        
    posts_path = os.path.join(my_path, 'static/BLOB', obj.form['email'], 'posts', 'videos')
    if not os.path.exists(posts_path):
        os.mkdir(posts_path)
        
    posts_path = os.path.join(my_path, 'static/BLOB', obj.form['email'], 'posts', 'documents')
    if not os.path.exists(posts_path):
        os.mkdir(posts_path)

    posts_path = os.path.join(my_path, 'static/BLOB', obj.form['email'], 'images')
    if not os.path.exists(posts_path):
        os.mkdir(posts_path)
    shutil.copy(os.path.join(my_path, 'static/images/resources/cover.jpg'), os.path.join(my_path, 'static/BLOB', user_info['email'], 'images', 'cover.jpg'))
    shutil.copy(os.path.join(my_path, 'static/images/resources/display.png'), os.path.join(my_path, 'static/BLOB', user_info['email'], 'images', 'display.png'))
    return user_info, password2


def get_totp_uri(email, otp_secret):
    return 'otpauth://totp/MFA-Code:{0}?secret={1}&issuer=Patrons Pool'.format(email, otp_secret)


def verify_totp(token, otp_secret):
    return onetimepass.valid_totp(token, otp_secret)


def login_util(request):
    username = request.form['email']
    password = base64.b64encode((request.form['pass']).encode('ascii')).decode('ascii')
    result = user_exists(username)
    if result:
        session['name'] = result['profile']['fname'] + " " + result['profile']['lname']
        if result['isSponsor'] == 0:
            session['isSponser'] = 0
        else:
            session['isSponser'] = 1
    return result, password, username, result['wallet_address']


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