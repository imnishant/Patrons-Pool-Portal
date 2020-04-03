from flask import Flask, render_template, request, render_template, redirect, url_for, session, flash, make_response
import os

from app.models import user_exists, save_user, store_posts
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
        result, password, username = login_util(request)

        if result:
            if result['password'] != password:
                return render_template('access_denied.html',
                                       error_msg="Password doesn't match. Go back and re-renter the password")

            session['username'] = username

            return render_template('home.html')
        return render_template('access_denied.html', error_msg="Username doesn't exist")
    return render_template('landing.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        
        user_info = signup_util(request)
        
        if (request.form['isSponsor'] == "Sponsor"):
            user_info['isSponsor'] = 1
        else:
            user_info['isSponsor'] = 0

        password2 = request.form['password2']

        if user_exists(user_info['email']):
            return render_template('access_denied.html', error_msg="Username already exist")

        if user_info['password'] != password2:
            return render_template('access_denied.html',
                                   error_msg="Password doesn't match. Go back and re-renter the password")

        save_user(user_info)
        return render_template('home.html')

    return render_template('signup.html')


@app.route('/addpost', methods=["POST"])
def add_post():
    if request.method == 'POST':
        # check if the post request has the file part
        post_headline = request.form.get('headline')
        multimedia = ''

        if 'image' in request.files:
            multimedia = 'image'

        elif 'audio' in request.files:
            multimedia = 'audio'

        elif 'video' in request.files:
            multimedia = 'video'

        if multimedia not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files[multimedia]
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)

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
            return "Post Added Successfully"
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
    return render_template('profile.html')


@app.route('/edit_basic')
def edit_basic():
    return render_template('edit-profile-basic.html')


@app.route('/edit_work')
def edit_work():
    return render_template('edit-work-eductation.html')


@app.route('/edit_interest')
def edit_interest():
    return render_template('edit-interest.html')


@app.route('/edit_account')
def edit_account():
    return render_template('edit-account-setting.html')


@app.route('/edit_password')
def edit_password():
    return render_template('edit-password.html')


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

