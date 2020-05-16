from flask import Flask, send_from_directory, render_template, request, render_template, redirect, url_for, session, flash, make_response
import os

from app.models import user_exists, save_user, store_posts, get_profile, update_basic, update_work, update_password, get_password, update_language, update_interest, get_posts
from app import app, BLOB
from app.utils import signup_util, login_util, allowed_file, edit_basic_util, edit_work_util, edit_pass_util, edit_lan_int_util
from werkzeug.utils import secure_filename
import datetime

my_path = os.path.abspath(os.path.dirname(__file__))

@app.route('/')
def hello_world():
    return render_template('landing.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        result, password, username = login_util(request)
        if result:
            if result['password'] != password:
                return render_template('access_denied.html', error_msg="Password doesn't match. Go back and re-renter the password")

            session['username'] = username
            posts = get_posts(username)
            return render_template('home.html', posts=posts)
        return render_template('access_denied.html', error_msg=result)
    return render_template('landing.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_info = {}
        user_info, password2 = signup_util(request)

        if user_exists(user_info['email']):
            return render_template('access_denied.html', error_msg="Username already exist")

        if user_info['password'] != password2:
            return render_template('access_denied.html',
                                   error_msg="Password doesn't match. Go back and re-renter the password")

        save_user(user_info)
        session['username'] = user_info['email']
        #session['useremail'] = user_info['email']
        posts = get_posts(session['username'])
        return render_template('home.html', posts = posts)

    return render_template('signup.html')

@app.route('/addpost', methods=["POST"])
def add_post():
    if request.method == 'POST':
        # check if the post request has the file part
        post_headline = request.form.get('headline')
        multimedia = ''
        folder_name = ''
        posts = ''

        if 'image' in request.files and request.files['image'].filename != '':
            multimedia = 'image'
            folder_name = 'images'

        elif 'audio' in request.files and request.files['audio'].filename != '':
            multimedia = 'audio'
            folder_name = 'audios'

        elif 'video' in request.files and request.files['video'].filename != '':
            multimedia = 'video'
            folder_name = 'videos'
        elif 'document' in request.files and request.files['document'].filename != '': 
            multimedia = 'document'
            folder_name = 'documents'
        else:
            flash('No file selected for uploading')
            return redirect(request.url)

        file = request.files[multimedia]
        extension = file.filename.split('.')[-1]
        
        if file and allowed_file(extension):
            filename = secure_filename(file.filename)
            file.save(os.path.join(BLOB, session['username'], 'posts', folder_name, filename))

            post_info = {
                "post_type": multimedia,
                "post_name": filename,
                "post_headline": post_headline,
                "date_time_added": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            store_posts(post_info)
            posts = get_posts(session['username'])
            # searches for dockerfile in the extracted folder
            # call this function after the user presses on the submit button or so
            
        else:
            return render_template("home.html", posts = posts, msg='Allowed file types are mp4, mp3, png, jpg, jpeg, gif')
    return render_template("home.html", posts = posts, msg='Added Successfully Bro! :-D')

@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html')

@app.route('/home')
def home():
    posts = get_posts(session['username'])
    return render_template('home.html', posts = posts)

@app.route('/profile')
def profile():
    res = get_profile(session['username'])
    if not res:
        return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details")
    return render_template('profile.html',profile=res)

@app.route('/edit_basic', methods=['GET', 'POST'])
def edit_basic():
    if request.method == 'POST':
        prof = edit_basic_util(request)
        if update_basic(session['username'],prof):
            return redirect(url_for('profile'))
        else:
            return render_template('access_denied.html', error_msg="Error Occured while updating Profile Details")
    if request.method == 'GET':
        res = get_profile(session['username'])
        if not res:
            return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details")
        return render_template('edit-profile-basic.html',profile=res)
    return render_template('access_denied.html', error_msg="wrong method invocaton")

@app.route('/edit_work', methods=['GET', 'POST'])
def edit_work():
    if request.method == 'POST':
        prof = edit_work_util(request)
        if update_work(session['username'],prof):
            return redirect(url_for('profile'))
        else:
            return render_template('access_denied.html', error_msg="Error Occured while updating Profile Details")
    if request.method == 'GET':
        res = get_profile(session['username'])
        if not res:
            return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details")
        return render_template('edit-work-education.html',profile=res)
    return render_template('access_denied.html', error_msg="wrong method invocaton")

@app.route('/edit_interest', methods=['GET', 'POST'])
def edit_interest():
    if request.method == 'POST':
        interest = edit_lan_int_util(request)
        if update_interest(session['username'],interest):
            return redirect(url_for('profile'))
        else:
            return render_template('access_denied.html', error_msg="Error Occured while updating Interests")
    if request.method == 'GET':
        res = get_profile(session['username'])
        if not res:
            return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details")
        return render_template('edit-interest.html', profile=res)
    return render_template('access_denied.html', error_msg="wrong method invocaton")

@app.route('/edit_language', methods=['GET', 'POST'])
def edit_language():
    if request.method == 'POST':
        lan = edit_lan_int_util(request)
        if update_language(session['username'],lan):
            return redirect(url_for('profile'))
        else:
            return render_template('access_denied.html', error_msg="Error Occured while updating Languages")
    if request.method == 'GET':
        res = get_profile(session['username'])
        if not res:
            return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details")
        return render_template('edit-language.html',profile=res)
    return render_template('access_denied.html', error_msg="wrong method invocaton")

@app.route('/edit_password', methods=['GET', 'POST'])
def edit_password():
    if request.method == 'POST':
        prof = edit_pass_util(request)
        if prof['new_pass'] != prof['con_pass']:
            return render_template('access_denied.html', error_msg="Passwords Don't match!")
        if prof['cur_pass'] != get_password(session['username']):
            return render_template('access_denied.html', error_msg="Current Password entered is wrong!")
        if update_password(session['username'],prof['new_pass']):
            return redirect(url_for('profile'))
        else:
            return render_template('access_denied.html', error_msg="Error Occured while updating Password")
    if request.method == 'GET':
        res = get_profile(session['username'])
        if not res:
            return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details")
        return render_template('edit-password.html',profile=res)
    return render_template('access_denied.html', error_msg="wrong method invocaton")

@app.route('/inbox')
def inbox():
    return render_template('inbox.html')

@app.route('/followers')
def followers():
    return render_template('followers.html')

@app.route('/images')
def images():
    path = '../BLOB/' + session['username'] + '/posts'
    return render_template('images.html')

@app.route('/videos')
def videos():
    return render_template('videos.html')

@app.route('/messages')
def messages():
    return render_template('messages.html')

@app.route('/notifications')
def notifications():
    return render_template('notifications.html')

@app.route('/get_BLOB', methods=["GET"])
def get_BLOB():
    if request.method == 'GET':
        return send_from_directory(my_path, request.get.args('filename'))

@app.errorhandler(404)
def not_found():
    return render_template('access_denied.html', error_msg="Page Not Found")

@app.errorhandler(400)
def bad_request():
    return render_template('access_denied.html', error_msg="Bad Request")

@app.errorhandler(500)
def server_error():
    return render_template('access_denied.html', error_msg="Internal Server Error")


