from threading import Thread

import pyqrcode as pyqrcode
from flask import Flask, send_from_directory, render_template, request, render_template, redirect, url_for, session, flash, make_response
import os
import hashlib
import time
from pygments import BytesIO
from app.models import user_exists, save_user, store_posts, store_patent, get_profile, update_basic, update_work, update_password, get_password, update_language, update_interest, get_posts, get_sponser_timeline, prof_img_upd, mail_sponsers_when_a_post_is_added, email_bid_status_to_other_sponsers, get_otp_secret, get_details_using_search, update_transaction_table, get_transactions
from app import app, BLOB, db
from app.utils import signup_util, login_util, allowed_file, edit_basic_util, edit_work_util, edit_pass_util, \
    edit_lan_int_util, get_totp_uri, verify_totp, get_password_util
from werkzeug.utils import secure_filename
import datetime


my_path = os.path.abspath(os.path.dirname(__file__))
app.jinja_env.add_extension('jinja2.ext.loopcontrols')


@app.route('/', methods=['POST', 'GET'])
def hello_world():
    return render_template('landing.html')


@app.route('/update_transaction', methods=['POST'])
def update_transaction():
    if request.method == 'POST':
        hash_value = request.form['hash']

        query = {"email": request.form['username'], "posts.post_headline": request.form['headline']}
        result = db['user'].find_one(query)
        wallet_address = result['wallet_address']
        if bool(result):
            db['user'].update_one(query, {"$set": {"posts.$.transaction_hash": hash_value}})
        else:
            return render_template('access_denied.html', error_msg="Some Error is there!", title="Error")

        amount = 0
        for post in result['posts']:
            if post['post_headline'] == request.form['headline']:
                amount = post['bid_price'][-1]
                break

        url = "https://ropsten.etherscan.io/tx/" + hash_value
        user_transaction = {
            "idea": request.form['headline'],
            "amount": amount,
            "received_from": session['wallet_address'],
            "transaction_url": url

        }

        sponsor_transaction = {
            "idea": request.form['headline'],
            "amount": amount,
            "paid_to": wallet_address,
            "transaction_url": url
        }

        # update the transaction table for the user
        update_transaction_table(request.form['username'], user_transaction)

        # update the transaction table for the sponsoe
        update_transaction_table(session['username'], sponsor_transaction)

        query = {"headline": request.form['headline'], "product_owners.username": request.form['username']}
        result = db['patent'].find_one(query)
        if bool(result):
            res = db['patent'].update_one(query, {"$push": { "product_owners": {'type': 'sponsor', 'username': session['username']} }})

        posts, timer = get_sponser_timeline()

        return render_template('sponsor.html', search=False, posts=posts, title="Home", timer=timer)
    return render_template('access_denied.html', error_msg="Method is not get", title="Error")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        result, password, username, wallet_address= login_util(request)
        if result:
            otp_secret = get_otp_secret(username)
            if result['password'] != password:
                return render_template('access_denied.html', error_msg="Password doesn't match. Please go back and re-enter the password!", title="Error")

            if not verify_totp(request.form['token'], otp_secret):
                return render_template('access_denied.html', error_msg="MFA Failed, Please go back and Retry!", title="Error")

            session['username'] = username
            session['wallet_address'] = wallet_address

            res = get_profile(session['username'])
            if not res:
                return render_template('access_denied.html', error_msg="Error occurred while fetching Profile Details", title="Error")
            if result['isSponsor'] == 1:
                session['isSponsor'] = 1
                posts, timer = get_sponser_timeline()
                return render_template('sponsor.html', search=False, posts=posts, title="Home", timer=timer)
            else:
                session['isSponsor'] = 0
                posts = get_posts(username)
                return render_template('home.html', posts=posts, profile=res, search=False)
        return render_template('access_denied.html', error_msg="Mail Doesn't exists!", title="Error")
    return render_template('landing.html', title="Login Page")



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_info, password2 = signup_util(request)

        if user_exists(user_info['email']):
            return render_template('access_denied.html', error_msg="Username already exist", title="Error")

        if user_info['password'] != password2:
            return render_template('access_denied.html', error_msg="Password doesn't match. Please go back and re-enter the password!", title="Error")

        save_user(user_info)
        session['username'] = user_info['email']
        return render_template('two-factor-setup.html', title="MFA Authentication")
    return render_template('signup.html', title="Signup Page")


@app.route('/qrcode')
def qrcode():
    # render qrcode for Google Authenticator
    time.sleep(2)
    otp_secret = get_otp_secret(session['username'])
    url = pyqrcode.create(get_totp_uri(session['username'], otp_secret))
    stream = BytesIO()
    url.svg(stream, scale=5)
    del session['username']
    session.clear()
    return stream.getvalue(), 200, {'Content-Type': 'image/svg+xml'}


@app.route('/addpost', methods=["POST"])
def add_post():
    res = get_profile(session['username'])
    if not res:
        return render_template('access_denied.html', error_msg="Error Occurred while fetching Profile Details", title="Error")
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
                "base_price": request.form.get('base_price'),
                "bid_price": [],
                "bidding_person": [],
                "first_bidding_time": "N/A",
                "bidding_status": "open",
                "date_time_added": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "transaction_hash": "N/A"
            }

            str = session['username'] + "Patrons Pool Portal" + post_headline
            vpn = hashlib.sha256(str.encode())

            patent_info = {
                "vpn": vpn.hexdigest(),
                "headline": post_headline,
                "product_owners": []
            }

            patent_info['product_owners'].append({'type': 'user', 'username': session['username']})

            store_posts(post_info)
            store_patent(patent_info)
            posts = get_posts(session['username'])
            # searches for dockerfile in the extracted folder
            # call this function after the user presses on the submit button or so

            # The below mentioned is the mailing functionality, Creates a separate thread and triggers the emails to all the sponsors
            thread = Thread(target=mail_sponsers_when_a_post_is_added, args=[app, session['username']])
            thread.start()
            
        else:
            return render_template("home.html", search=False, posts=posts, profile=res, msg='Allowed file types are mp4, mp3, png, jpg, jpeg, gif', title="Home")
    return render_template("home.html", search=False, posts=posts, profile=res, msg='Added Successfully! :-D', title="Home")



@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html', title="Logout")


@app.route('/home', methods=['GET', 'POST'])
def home():
    if session['isSponsor'] == 1:
        posts, timer = get_sponser_timeline()
        return render_template('sponsor.html', search=False, posts=posts, title="Home", timer=timer)
    else:
        res = get_profile(session['username'])
        posts = get_posts(session['username'])
        return render_template('home.html', posts=posts, profile=res, search=False, title="Home")


@app.route('/filters', methods=['GET', 'POST'])
def filters():
    val = request.args.get('val')
    if session['isSponsor'] == 1:
        posts, timer = get_sponser_timeline()
        return render_template('sponsor.html', search=False, posts=posts, title="Home", filters=val, timer=timer)
    else:
        res = get_profile(session['username'])
        posts = get_posts(session['username'])
        return render_template('home.html', posts=posts, profile=res, search=False, title="Home", filters=val)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    res = get_profile(session['username'])
    if not res:
        return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details", title="Error")
    return render_template('profile.html', profile=res, title="Profile")


@app.route('/edit_basic', methods=['GET', 'POST'])
def edit_basic():
    if request.method == 'POST':
        prof = edit_basic_util(request)
        if update_basic(session['username'],prof):
            return redirect(url_for('profile'))
        else:
            return render_template('access_denied.html', error_msg="Error Occurred while updating Profile Details", title="Error")
    if request.method == 'GET':
        res = get_profile(session['username'])
        if not res:
            return render_template('access_denied.html', error_msg="Error Occurred while fetching Profile Details", title="Error")
        return render_template('edit-profile-basic.html',profile=res, title="Edit Profile")
    return render_template('access_denied.html', error_msg="wrong method Invocation", title="Error")


@app.route('/edit_work', methods=['GET', 'POST'])
def edit_work():
    if request.method == 'POST':
        prof = edit_work_util(request)
        if update_work(session['username'],prof):
            return redirect(url_for('profile'))
        else:
            return render_template('access_denied.html', error_msg="Error Occurred while updating Profile Details", title="Error")
    if request.method == 'GET':
        res = get_profile(session['username'])
        if not res:
            return render_template('access_denied.html', error_msg="Error Occurred while fetching Profile Details", title="Error")
        return render_template('edit-work-education.html',profile=res, title="Edit Profile")
    return render_template('access_denied.html', error_msg="wrong method Invocation", title="Error")


@app.route('/edit_interest', methods=['GET', 'POST'])
def edit_interest():
    if request.method == 'POST':
        interest = edit_lan_int_util(request)
        if update_interest(session['username'],interest):
            return redirect(url_for('profile'))
        else:
            return render_template('access_denied.html', error_msg="Error Occurred while updating Interests", title="Error")
    if request.method == 'GET':
        res = get_profile(session['username'])
        if not res:
            return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details", title="Error")
        return render_template('edit-interest.html', profile=res, title="Edit Profile")
    return render_template('access_denied.html', error_msg="wrong method invocation", title="Error")



@app.route('/edit_language', methods=['GET', 'POST'])
def edit_language():
    if request.method == 'POST':
        lan = edit_lan_int_util(request)
        if update_language(session['username'],lan):
            return redirect(url_for('profile'))
        else:
            return render_template('access_denied.html', error_msg="Error Occurred while updating Languages", title="Error")
    if request.method == 'GET':
        res = get_profile(session['username'])
        if not res:
            return render_template('access_denied.html', error_msg="Error Occurred while fetching Profile Details", title="Error")
        return render_template('edit-language.html',profile=res, title="Edit Profile")
    return render_template('access_denied.html', error_msg="wrong method Invocation", title="Error")


@app.route('/edit_password', methods=['GET', 'POST'])
def edit_password():
    if request.method == 'POST':
        prof = edit_pass_util(request)
        if prof['new_pass'] != prof['con_pass']:
            return render_template('access_denied.html', error_msg="Passwords Don't match!", title="Error")
        if prof['cur_pass'] != get_password(session['username']):
            return render_template('access_denied.html', error_msg="Current Password entered is wrong!", title="Error")
        if update_password(session['username'],prof['new_pass']):
            return redirect(url_for('profile'))
        else:
            return render_template('access_denied.html', error_msg="Error Occurred while updating Password", title="Error")
    if request.method == 'GET':
        res = get_profile(session['username'])
        if not res:
            return render_template('access_denied.html', error_msg="Error Occurred while fetching Profile Details", title="Error")
        return render_template('edit-password.html',profile=res, title="Edit Profile")
    return render_template('access_denied.html', error_msg="wrong method Invocation", title="Error")


@app.route('/images', methods=['GET'])
def images():
    if request.method == 'GET':
        res = get_profile(session['username'])
        if not res:
            return render_template('access_denied.html', error_msg="Error Occurred while fetching Profile Details", title="Error")
        if os.path.exists(os.path.join(BLOB, session['username'], 'posts', 'images')):
            files = os.listdir(os.path.join(BLOB, session['username'], 'posts', 'images'))
        else:
            files = []
        return render_template('images.html', profile=res, title="Images", files=files, email=session['username'])
    return render_template('access_denied.html', error_msg="wrong method Invocation", title="Error")


@app.route('/videos', methods=['GET'])
def videos():
    if request.method == 'GET':
        res = get_profile(session['username'])
        if not res:
            return render_template('access_denied.html', error_msg="Error Occurred while fetching Profile Details", title="Error")
        if os.path.exists(os.path.join(BLOB, session['username'], 'posts', 'videos')):
            files = os.listdir(os.path.join(BLOB, session['username'], 'posts', 'videos'))
        else:
            files = []
        return render_template('videos.html', profile=res, title="Videos", files=files, email=session['username'])
    return render_template('access_denied.html', error_msg="wrong method Invocation", title="Error")


@app.route('/audios', methods=['GET'])
def audios():
    if request.method == 'GET':
        res = get_profile(session['username'])
        if not res:
            return render_template('access_denied.html', error_msg="Error Occurred while fetching Profile Details", title="Error")
        if os.path.exists(os.path.join(BLOB, session['username'], 'posts', 'audios')):
            files = os.listdir(os.path.join(BLOB, session['username'], 'posts', 'audios'))
        else:
            files = []
        return render_template('audios.html', profile=res, title="Audios", files=files, email=session['username'])
    return render_template('access_denied.html', error_msg="wrong method Invocation", title="Error")


@app.route('/documents', methods=['GET'])
def documents():
    if request.method == 'GET':
        res = get_profile(session['username'])
        if not res:
            return render_template('access_denied.html', error_msg="Error Occurred while fetching Profile Details", title="Error")
        if os.path.exists(os.path.join(BLOB, session['username'], 'posts', 'documents')):
            files = os.listdir(os.path.join(BLOB, session['username'], 'posts', 'documents'))
        else:
            files = []
        return render_template('documents.html', profile=res, title="Documents", files=files, email=session['username'])
    return render_template('access_denied.html', error_msg="wrong method Invocation", title="Error")


@app.route('/get_BLOB', methods=["GET"])
def get_BLOB():
    if request.method == 'GET':
        return send_from_directory(my_path, request.get.args('filename'))


@app.route('/delete_post', methods=["POST"])
def delete_post():
    if request.method == 'POST':
        folder = request.form['folder']
        filename = request.form['filename']

        if os.path.exists(os.path.join(BLOB, session['username'], 'posts', folder + 's', filename)):
            os.remove(os.path.join(BLOB, session['username'], 'posts', folder + 's', filename))
        else:
            return render_template('access_denied.html', error_msg="File does not exist locally", title="Error")

        query = {"email": session['username']}
        result = db['user'].find_one(query)

        if bool(result):
            res = db['user'].update_one(
                {"email": session['username']},
                {"$pull": {"posts": {'post_name': filename}}}
            )
        else:
            return render_template('access_denied.html', error_msg="File does not exist in mongodb database", title="Error")

        posts = get_posts(session['username'])

        res = get_profile(session['username'])
        if not res:
            return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details", title="Error")
        return render_template('home.html', posts=posts, profile=res, msg="Post Successfully deleted!", search=False, title="Home")
    return render_template('access_denied.html', error_msg="Delete Post Method is not POST", title="Error")



@app.route('/update_bid', methods=["POST"])
def update_bid():
    if request.method == 'POST':

        # 600 seconds means 10 minutes bidding time
        # if you update window time here than also update in models.py get_sponser_timeline()
        window_in_seconds = 120
        current_bid_time = int(datetime.datetime.now().timestamp())


        query = {"email": request.form['email']}
        update_query = {"email": request.form['email'], "posts.post_headline": request.form['post_headline']}
        result = db['user'].find_one(query)
        target_post = {}

        for post in result["posts"]:
            if post['post_headline'] == request.form['post_headline']:
                target_post['bid_price'] = post['bid_price']
                target_post['base_price'] = post['base_price']
                target_post['first_bidding_time'] = post['first_bidding_time']
                target_post['bidding_status'] = post['bidding_status']
                target_post['bidding_person'] = post['bidding_person']
                # target_post['bid_price'] = post['bid_price']
                # target_post['bid_price'] = post['bid_price']
                break

        if bool(target_post):
            new_sponser_bid_price = int(request.form['bid_price'])
            new_sponser_email = session['username']
            base_price = int(target_post['base_price'])
            bid_price = target_post['bid_price']
            if not bid_price:
                earlier = False
                earlier_bid_price = base_price
            else:
                earlier = True
                earlier_bid_price = bid_price[-1]
            first_bidding_time = target_post['first_bidding_time']
            bidding_person = target_post['bidding_person']

            if not earlier and new_sponser_bid_price > base_price:
                # retrieve the bid price for the post and check if the bid price equals N/A then set the bid_price then perform the below step
                bid_price.append(int(new_sponser_bid_price))
                bidding_person.append(request.form['bidding_person'])
                db['user'].update_one(update_query, {"$set": {"posts.$.bid_price": bid_price, "posts.$.bidding_person": bidding_person, "posts.$.first_bidding_time": int(datetime.datetime.now().timestamp())}})

            elif new_sponser_bid_price > earlier_bid_price and current_bid_time - first_bidding_time < window_in_seconds:
                # else check if the bid price is > previous bid price and also the time when performing this step falls under the window time
                bid_price.append(int(new_sponser_bid_price))
                bidding_person.append(request.form['bidding_person'])
                db['user'].update_one(update_query, {"$set": {"posts.$.bid_price": bid_price, "posts.$.bidding_person": bidding_person}})

                # Uncomment it to resume message functionality
                # The below mentioned is the mailing functionality, Creates a separate thread and triggers the emails to all the sponsors participating in the bid
                thread = Thread(target=email_bid_status_to_other_sponsers, args=[app, request.form['email'], request.form['post_headline'], session['username']])
                thread.start()


            elif int(new_sponser_bid_price) <= earlier_bid_price:
                posts, timer = get_sponser_timeline()
                return render_template("sponsor.html", search=False, posts=posts,msg='Please enter amount greater than the current bid amount!', title="Home", timer=timer)

            else:
                # display time window is over you cannot bid anymore
                posts, timer = get_sponser_timeline()

                return render_template("sponsor.html", search=False, posts=posts, msg='You cannot bid anymore because Bidding Time is Over', title="Home", timer=timer)

            posts, timer = get_sponser_timeline()
            return render_template("sponsor.html", search=False, posts=posts, msg='Your Bid Placed Successfully ! ATB! :)', title="Home", timer=timer)
        else:
            return render_template('access_denied.html', error_msg="File does not exist in mongodb database", title="Error")
    return render_template('access_denied.html', error_msg="Delete Post Method is not POST", title="Error")


@app.route('/add_profile_photos', methods=['POST'] )
def add_profile_photos():
    multimedia = ''

    if 'myfile' in request.files and request.files['myfile'].filename != '':
        multimedia = 'myfile'
        rem = 'cover'

    elif 'myfile1' in request.files and request.files['myfile1'].filename != '':
        multimedia = 'myfile1'
        rem = 'display'

    else:
        return render_template('access_denied.html', error_msg="Error Occurred!", title="Error")

    file = request.files[multimedia]
    extension = file.filename.split('.')[-1]

    if file and allowed_file(extension):
        filename = secure_filename(file.filename)
        file.save(os.path.join(BLOB, session['username'], 'images', filename))
        prof = get_profile(session['username'])
        if os.path.exists(os.path.join(BLOB, session['username'], 'images', prof[rem])):
            os.remove(os.path.join(BLOB, session['username'], 'images', prof[rem]))
        res = prof_img_upd(session['username'], filename, rem)
        if not res:
            return render_template('access_denied.html', error_msg="Error Occurred!", title="Error")

    return redirect(url_for('profile'))


@app.route('/search', methods=["GET"])
def search():
    query = request.args.get('query')
    # We'll get a result object
    result = get_details_using_search(query)
    msg = 'Search results for Query: ' + query

    if session['isSponser'] == 0:
        if not result:
            return render_template('home.html', search=True, error_msg="Oops! No Search Result Found for Query: ", found="no", username="None", query=query, title="Search")
        return render_template('home.html', search=True, result=result, found="yes", msg=msg, title="Search")

    if session['isSponser'] == 1:
        posts, timer = get_sponser_timeline()
        if not result:
            return render_template('sponsor.html', posts=posts, search=True, error_msg="Oops! No Search Result Found for Query: ", found="no", username="None", query=query, title="Search", timer=timer)
        return render_template('sponsor.html', posts=posts, search=True, result=result, found="yes", msg=msg, title="Search", timer=timer)
    return


@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    transactions = get_transactions(session['username'])
    if transactions == []:
        return render_template('transaction.html', title="Transaction", msg="No Transactions done yet!")
    return render_template('transaction.html', title="Transaction", transactions=transactions)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    return render_template('password.html', title="Forgot Password")


@app.route('/forgot_password_check', methods=['GET', 'POST'])
def forgot_password_check():
    username = request.form['email']
    otp_secret = get_otp_secret(username)
    if not verify_totp(request.form['token'], otp_secret):
        return render_template('access_denied.html', error_msg="MFA Failed, Please go back and Retry!", title="Error")
    return render_template('change_password.html', title="Forgot Password", email=username)


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    username, password = get_password_util(request)
    if password == 0:
        return render_template('access_denied.html', error_msg="Passwords Don't Match", title="Error")
    if update_password(username, password):
        return redirect(url_for('hello_world'))
    else:
        return render_template('access_denied.html', error_msg="Error Occurred while updating Password", title="Error")


@app.route('/display_profile', methods=['GET', 'POST'])
def display_profile():
    username = request.args.get('username')
    res = get_profile(username)
    msg = "User Profile: " + username
    res['interest'] = ', '.join(res['interest'])
    res['language'] = ', '.join(res['language'])
    if not res:
        return render_template('access_denied.html', error_msg="Error Occurred while fetching Profile Details", title="Error")
    return render_template('display_profile.html', profile=res, title="Display Profile", msg=msg)


@app.errorhandler(404)
def not_found():
    return render_template('access_denied.html', error_msg="Page Not Found", title="Not Found")


@app.errorhandler(400)
def bad_request():
    return render_template('access_denied.html', error_msg="Bad Request", title="Bad Request")


@app.errorhandler(500)
def server_error():
    return render_template('access_denied.html', error_msg="Internal Server Error", title="Internal Server Error")


