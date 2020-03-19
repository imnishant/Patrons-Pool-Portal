from flask import Flask, render_template, request, render_template, redirect, url_for, session
from app.models import user_exists, save_user
from app import app


@app.route('/')
def hello_world():
    return render_template('index.html')


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
            return render_template('home.html', username=username)
        return render_template('access_denied.html', error_msg="Username doesn't exist")
    return render_template('home.html')


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
    return render_template('index.html')


@app.route('/home')
def home():
    return "Welcome"

#if __name__ == '__main__':
#    app.run(debug=True)
