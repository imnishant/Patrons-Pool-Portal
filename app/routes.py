from flask import Flask, send_from_directory, render_template, request, render_template, redirect, url_for, session, flash, make_response
import os

from app.models import user_exists, save_user, store_posts, get_profile, update_basic, update_work, update_password, get_password, update_language, update_interest, get_posts, get_sponser_timeline, prof_img_upd, mail_sponsers_when_a_post_is_added, email_bid_status_to_other_sponsers

from app import app, BLOB, db
from app.utils import signup_util, login_util, allowed_file, edit_basic_util, edit_work_util, edit_pass_util, edit_lan_int_util
from werkzeug.utils import secure_filename
import datetime

my_path = os.path.abspath(os.path.dirname(__file__))

@app.route('/', methods=['POST', 'GET'])
def hello_world():
    return render_template('landing.html')

@app.route('/update_transaction', methods=['POST'])
def update_transaction():
    if request.method == 'POST':
        hash_value = request.form['hash']

        query = {"email": request.form['username'], "posts.post_headline": request.form['headline']}
        result = db['user'].find_one(query)
        if bool(result):
            res = db['user'].update_one(query, {"$set": {"posts.$.transaction_hash": hash_value}})
        else:
            return render_template('access_denied.html', error_msg="Some Error is there!")

        posts = get_sponser_timeline()
        return render_template('sponsor.html', posts=posts)
    return render_template('access_denied.html', error_msg="Method is not get")
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        result, password, username, wallet_address= login_util(request)
        if result:
            if result['password'] != password:
                return render_template('access_denied.html', error_msg="Password doesn't match. Go back and re-renter the password")

            session['username'] = username
            session['wallet_address'] = wallet_address

            res = get_profile(session['username'])
            if not res:
                return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details")
            if result['isSponsor'] == 1:
                session['isSponsor'] = 1
                posts = get_sponser_timeline()
                return render_template('sponsor.html', posts=posts)
            else:
                session['isSponsor'] = 0
                posts = get_posts(username)
                return render_template('home.html', posts=posts, profile=res)
        return render_template('access_denied.html', error_msg="Mail Doesn't exists!")
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
        session['wallet_address'] = user_info['wallet_address']

        res = get_profile(session['username'])
        if not res:
            return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details")
        #session['useremail'] = user_info['email']
        posts = get_posts(session['username'])
        if user_info['isSponsor'] == 1:
            session['isSponsor'] = 1
            posts = get_sponser_timeline()
            return render_template('sponsor.html', posts=posts)
        else:
            session['isSponsor'] = 0
            posts = get_posts(session['username'])
            return render_template('home.html', posts=posts, profile=res)

    return render_template('signup.html')

@app.route('/addpost', methods=["POST"])
def add_post():
    res = get_profile(session['username'])
    if not res:
        return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details")
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

            store_posts(post_info)
            posts = get_posts(session['username'])
            # searches for dockerfile in the extracted folder
            # call this function after the user presses on the submit button or so
            #mail_sponsers_when_a_post_is_added()
            
        else:
            return render_template("home.html", posts = posts, profile=res, msg='Allowed file types are mp4, mp3, png, jpg, jpeg, gif')
    return render_template("home.html", posts = posts, profile=res, msg='Added Successfully Bro! :-D')


@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    if session['isSponsor'] == 1:
        posts = get_sponser_timeline()
        return render_template('sponsor.html', posts=posts)
    else:
        res = get_profile(session['username'])
        posts = get_posts(session['username'])
        return render_template('home.html', posts=posts, profile=res)

@app.route('/profile', methods=['GET', 'POST'])
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


@app.route('/images', methods=['GET'])
def images():
    if request.method == 'GET':
        res = get_profile(session['username'])
        if not res:
            return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details")
        if os.path.exists(os.path.join(BLOB, session['username'], 'posts', 'images')):
            files = os.listdir(os.path.join(BLOB, session['username'], 'posts', 'images'))
        else:
            files = []
        return render_template('images.html', profile=res, title="Images", files=files, email=session['username'])
    return render_template('access_denied.html', error_msg="wrong method invocaton")


@app.route('/videos', methods=['GET'])
def videos():
    if request.method == 'GET':
        res = get_profile(session['username'])
        if not res:
            return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details")
        if os.path.exists(os.path.join(BLOB, session['username'], 'posts', 'videos')):
            files = os.listdir(os.path.join(BLOB, session['username'], 'posts', 'videos'))
        else:
            files = []
        return render_template('videos.html', profile=res, title="Videos", files=files, email=session['username'])
    return render_template('access_denied.html', error_msg="wrong method invocaton")


@app.route('/audios', methods=['GET'])
def audios():
    if request.method == 'GET':
        res = get_profile(session['username'])
        if not res:
            return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details")
        if os.path.exists(os.path.join(BLOB, session['username'], 'posts', 'audios')):
            files = os.listdir(os.path.join(BLOB, session['username'], 'posts', 'audios'))
        else:
            files = []
        return render_template('audios.html', profile=res, title="Audios", files=files, email=session['username'])
    return render_template('access_denied.html', error_msg="wrong method invocaton")


@app.route('/documents', methods=['GET'])
def documents():
    if request.method == 'GET':
        res = get_profile(session['username'])
        if not res:
            return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details")
        if os.path.exists(os.path.join(BLOB, session['username'], 'posts', 'documents')):
            files = os.listdir(os.path.join(BLOB, session['username'], 'posts', 'documents'))
        else:
            files = []
        return render_template('documents.html', profile=res, title="Documents", files=files, email=session['username'])
    return render_template('access_denied.html', error_msg="wrong method invocaton")

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
            return render_template('access_denied.html', error_msg="File does not exist locally")

        query = {"email": session['username']}
        result = db['user'].find_one(query)

        if bool(result):
            res = db['user'].update_one(
                {"email": session['username']},
                {"$pull": {"posts": {'post_name': filename}}}
            )
        else:
            return render_template('access_denied.html', error_msg="File does not exist in mongodb database")

        posts = get_posts(session['username'])

        res = get_profile(session['username'])
        if not res:
            return render_template('access_denied.html', error_msg="Error Occured while fetching Profile Details")
        return render_template('home.html', posts=posts, profile=res, msg="Post Successfully deleted!")
    return render_template('access_denied.html', error_msg="Delete Post Method is not POST")

@app.route('/update_bid', methods=["POST"])
def update_bid():
    if request.method == 'POST':

        # 600 seconds means 10 minutes bidding time
        # if you update window time here than also update in models.py get_sponser_timeline()
        window_in_seconds = 600
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

                #Uncomment it to resume message functionality
                #email_bid_status_to_other_sponsers(request.form['email'], request.form['post_headline'])

            elif int(new_sponser_bid_price) <= earlier_bid_price:
                posts = get_sponser_timeline()
                return render_template("sponsor.html", posts=posts,msg='Please enter amount greater than the current bid amount!')

            else:
                # display time window is over you cannot bid anymore
                posts = get_sponser_timeline()
                return render_template("sponsor.html", posts=posts,
                                       msg='You cannot bid anymore because Bidding Time is Over')

            posts = get_sponser_timeline()
            return render_template("sponsor.html", posts=posts, msg='Your Bid Placed Successfully Bro! ATB! :)')
        else:
            return render_template('access_denied.html', error_msg="File does not exist in mongodb database")
    return render_template('access_denied.html', error_msg="Delete Post Method is not POST")

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
        return render_template('access_denied.html', error_msg="Error Occured!")

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
            return render_template('access_denied.html', error_msg="Error Occured!")

    return redirect(url_for('profile'))

@app.errorhandler(404)
def not_found():
    return render_template('access_denied.html', error_msg="Page Not Found")

@app.errorhandler(400)
def bad_request():
    return render_template('access_denied.html', error_msg="Bad Request")

@app.errorhandler(500)
def server_error():
    return render_template('access_denied.html', error_msg="Internal Server Error")


