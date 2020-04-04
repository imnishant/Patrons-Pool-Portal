from flask import Flask, render_template, request, render_template, redirect, url_for, session, flash, make_response
import os

from app.models import user_exists, save_user, store_posts, get_profile
from app import app, BLOB
from app.utils import signup_util, login_util, allowed_file
from werkzeug.utils import secure_filename
import datetime

@app.route('/')
def hello_world():
    return render_template('landing.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        useremail = request.form['email']
        password = request.form['pass']
        result = user_exists(useremail)
        result, password, username = login_util(request)
        if result:
            if result['password'] != password:
                return render_template('access_denied.html',
                                       error_msg="Password doesn't match. Go back and re-renter the password")
            session['useremail'] = useremail
            # session['c_type'] = result['c_type']
            session['username'] = username
            return render_template('home.html')
        return render_template('access_denied.html', error_msg="Username doesn't exist")
    return render_template('landing.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
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

        password2 = request.form['password2']

        if user_exists(user_info['email']):
            return render_template('access_denied.html', error_msg="Username already exist")

        if user_info['password'] != password2:
            return render_template('access_denied.html',
                                   error_msg="Password doesn't match. Go back and re-renter the password")

        save_user(user_info)
        session['username'] = user_info['email']
        session['useremail'] = user_info['email']
        return render_template('home.html')

    return render_template('signup.html')

@app.route('/addpost', methods=["POST"])
def add_post():
    if request.method == 'POST':
        # check if the post request has the file part
        post_headline = request.form.get('headline')
        multimedia = ''

        if 'image' in request.files and request.files['image'].filename != '':
            multimedia = 'image'

        elif 'audio' in request.files and request.files['audio'].filename != '':
            multimedia = 'audio'

        elif 'video' in request.files and request.files['video'].filename != '':
            multimedia = 'video'
        else:
            flash('No file selected for uploading')
            return redirect(request.url)

        """if multimedia not in request.files:
            flash('No file part')
            return redirect(request.url)
        """
        
        file = request.files[multimedia]
        """if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        """
        if file and allowed_file(file.content_type):
            filename = secure_filename(file.filename)
            file.save(os.path.join(BLOB, session['username'], 'posts', filename))
            flash('File successfully uploaded')

            post_info = {
                "username": session['username'],
                "post_type": multimedia,
                "post_name": filename,
                "post_headline": post_headline,
                "date_time_added": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            store_posts(post_info)
            # searches for dockerfile in the extracted folder
            # call this function after the user presses on the submit button or so
            return render_template("home.html", msg="Post Added Successfully")
        else:
            flash('Allowed file types are mp4, mp3, png, jpg, jpeg, gif')
            return redirect(request.url)
    print("Response came")
    return make_response(('ok', 200))

@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/profile')
def profile():
    res = get_profile(session['useremail'])
    if not res:
        return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details")
    return render_template('profile.html',profile=res)

@app.route('/edit_basic')
def edit_basic():
    res = get_profile(session['useremail'])
    if not res:
        return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details")
    return render_template('edit-profile-basic.html',profile=res)

@app.route('/edit_work')
def edit_work():
    res = get_profile(session['useremail'])
    if not res:
        return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details")
    return render_template('edit-work-education.html',profile=res)

@app.route('/edit_interest')
def edit_interest():
    res = get_profile(session['useremail'])
    if not res:
        return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details")
    return render_template('edit-interest.html',profile=res)

@app.route('/edit_language')
def edit_language():
    res = get_profile(session['useremail'])
    if not res:
        return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details")
    return render_template('edit-language.html',profile=res)

@app.route('/edit_password')
def edit_password():
    res = get_profile(session['useremail'])
    if not res:
        return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details")
    return render_template('edit-password.html',profile=res)

@app.route('/inbox')
def inbox():
    return render_template('inbox.html')

@app.route('/followers')
def followers():
    return render_template('followers.html')

@app.route('/images')
def images():
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

@app.errorhandler(404)
def not_found():
    return render_template('access_denied.html', error_msg="Page Not Found")

@app.errorhandler(400)
def bad_request():
    return render_template('access_denied.html', error_msg="Bad Request")

@app.errorhandler(500)
def server_error():
    return render_template('access_denied.html', error_msg="Internal Server Error")


