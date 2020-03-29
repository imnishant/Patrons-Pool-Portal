from flask import Flask, render_template, request, render_template, redirect, url_for, session

from app.models import user_exists, save_user
from app import app


@app.route('/')
def hello_world():
    return render_template('landing.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['pass']
        result = user_exists(username)

        if result:
            if result['password'] != password:
                return render_template('access_denied.html',
                                       error_msg="Password doesn't match. Go back and re-renter the password")

            session['username'] = username
            # session['c_type'] = result['c_type']
            return render_template('home.html')
        return render_template('access_denied.html', error_msg="Username doesn't exist")
    return render_template('landing.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_info = {}
        user_info['fname'] = request.form['fname']
        user_info['lname'] = request.form['lname']
        user_info['gender'] = request.form['gender']
        user_info['age'] = request.form['age']
        user_info['password'] = request.form['password1']
        user_info['email'] = request.form['email']
        user_info['occupation'] = request.form['occupation']
        user_info['organization'] = request.form['organization']
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


@app.errorhandler(404)
def not_found():
    return render_template('access_denied.html', error_msg="Page Not Found")

@app.errorhandler(400)
def bad_request():
    return render_template('access_denied.html', error_msg="Bad Request")


@app.errorhandler(500)
def server_error():
    return render_template('access_denied.html', error_msg="Internal Server Error")


#if __name__ == '__main__':
#   app.run(debug=True)
