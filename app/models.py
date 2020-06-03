from threading import Thread

from flask_mail import Message
from app import db, mail, app
from flask import session
import datetime


def user_exists(email):
    query = {"email": email}
    result = db['user'].find_one(query)
    if bool(result):
        return result
    return False


def save_user(user_info):
    db['user'].insert_one(user_info)


def get_password(email):
    query = {"email": email}
    result = db['user'].find_one(query)
    if bool(result):
        return result['password']
    return False


def get_profile(email):
    query = {"email": email}
    result = db['user'].find_one(query)
    if bool(result):
        return result['profile']
    return False


def get_otp_secret(email):
    query = {"email": email}
    result = db['user'].find_one(query)
    if bool(result):
        return result['otp_secret']
    return False


def get_posts(email):
   query = {"email": email}
   result = db['user'].find_one(query)
   if bool(result):
       return result['posts']
   return False


def get_details_using_search(query):
    mongo_query = {"$text": {"$search": query}}
    cursor = db['user'].find(mongo_query)
    result = []
    if cursor:
        for doc in cursor:
            result.append(doc)
    return result


def get_sponser_timeline():
    query = {"isSponsor" : 0}
    users = list(db['user'].find(query))
    posts = []

    for user in users:
        username = user['email']
        wallet_address = user['wallet_address']
        userposts = user['posts']
        for post in userposts:
            post['username'] = username
            post['name'] = user['profile']['fname'] + " " + user['profile']['lname']
            post['wallet_address'] = wallet_address
            post['display'] = user['profile']['display']

            current_time = int(datetime.datetime.now().timestamp())
            window_in_seconds = 120

            first_bidding_time = post['first_bidding_time']
            if first_bidding_time == "N/A":
                post['bidding_status'] = "open"
            elif current_time - int(first_bidding_time) < window_in_seconds:
                post['bidding_status'] = "open"
            else:
                post['bidding_status'] = "closed"

            #set_new_bid_update_status(post['username'], post['post_headline'], post['bidding_status'])
            posts.append(post)
    print(posts)
    #  return result
    return posts


def set_new_bid_update_status(email, headline, get_new_update):
    update_query = {"email": email, "posts.post_headline": headline}
    db['user'].update_one(update_query, {"$set": {"posts.$.bidding_status": get_new_update}})
    return


def update_basic(email, profile):
    res = db['user'].update_one(
        { "email": email},
        {
            "$set": {
                "profile.fname": profile['fname'],
                "profile.lname": profile['lname'],
                "profile.phone": profile['phone'],
                "profile.website": profile['website'],
                "profile.address.line": profile['address'],
                "profile.address.city": profile['city'],
                "profile.address.country": profile['country'],
                "profile.about": profile['about']
            }
        }
    )
    return res.matched_count > 0


def update_work(email, profile):
    res = db['user'].update_one(
        { "email": email},
        {
            "$set": {
                "profile.course": profile['course'],
                "profile.institution": profile['institution'],
                "profile.occupation": profile['occupation'],
                "profile.organization": profile['organization']
            }
        }
    )
    return res.matched_count > 0


def update_password(email, password):
    res = db['user'].update_one(
        { "email": email},
        {
            "$set": {
                "password": password
            }
        }
    )
    return res.matched_count > 0


def update_language(email, lan):
    res = db['user'].update_one(
        { "email": email},
        {
            "$set": {
                "profile.language": lan
            }
        }
    )
    return res.matched_count > 0


def update_interest(email, interest):
    res = db['user'].update_one(
        { "email": email},
        {
            "$set": {
                "profile.interest": interest
            }
        }
    )
    return res.matched_count > 0


def store_posts(post_info):
    obj = {}
    obj['posts'] = post_info
    
    find_query = {'email': session['username']}
    action =  {"$addToSet": { "posts": { "$each": [post_info] }}}
    db['user'].update(find_query, action)


def store_patent(post_info):
    db['patent'].insert_one(post_info)

def prof_img_upd(email, filename, rem):
    attr = 'profile.' + rem
    res = db['user'].update_one(
        {"email": email},
        {
            "$set": {
                attr: filename
            }
        }
    )
    return res.matched_count > 0


def email_bid_status_to_other_sponsers(app, email, headline, session_user_email):
    with app.app_context():
        query = {"email": email, "posts.post_headline": headline}
        result = db['user'].find_one(query)
        bidding_status = ""
        bidding_person_emails = []

        for post in result["posts"]:
            if post['post_headline'] == headline:
                bidding_status = post['bidding_status']
                bidding_person_emails = post['bidding_person']

        # remove the email of the current person which placed the bid earlier
        try:
            while True:
                bidding_person_emails.remove(session['username'])
        except ValueError:
            pass
        try:
            if bidding_status == 'open':
                msg = Message('[Bid Update] Hike in the Bid Price!', sender=app.config['MAIL_DEFAULT_SENDER'], recipients=bidding_person_emails)
                msg.html = EMAIL_BID_UPDATE_TEMPLATE.format(email_address=session_user_email)
                mail.send(msg)
        except:
            return



def mail_sponsers_when_a_post_is_added(app, email):
    with app.app_context():
        query = {"isSponsor": 1}
        sponsers = list(db['user'].find(query))
        email_ids = []

        try:
            if sponsers:
                for sponser in sponsers:
                    email_ids.append(sponser['email'])

                msg = Message('[Post] Seeking for a Patron!', sender=app.config['MAIL_DEFAULT_SENDER'], recipients=email_ids)
                msg.html = GENERAL_EMAIL_POST_NOTIFICATION_TEMPLATE.format(email_address=email)
                mail.send(msg)
            return
        except:
            return


# WARNING: DO NOT DELETE THE BELOW EMAIL TEMPLATES!
GENERAL_EMAIL_POST_NOTIFICATION_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>Page Title</title>
</head>
<body>
<h1 style="color:red;font-size:40px;">Hello Patron!</h1>
<p style="font-family:Helvetica, Arial, sans-serif; font-size:20px; color:#4d4d4e;"> {email_address} is on a hunt for a Patron for his new million dollar idea. Do check it out and bid for the same if that idea mesmerizes you!</p>
<table border="0" cellpadding="0" cellspacing="0" width="500">
  <tbody>

    <tr>
      <td height="64" style="font-family:Helvetica, Arial, sans-serif; font-size:18px; font-style:bold;">
        <strong>The Patrons Pool</strong>
        <br>
        <em style="font-size:17px; font-weight:400;">Where Seekers meets Patrons</em>
      </td>
    </tr>
    <tr>
      <td height="58" style="font-family:Helvetica, Arial, sans-serif; font-size:16px; color:#4d4d4e;">
        Dr. Vishnuvardhana Road Post, Channasandra, RR Nagar 
        <br> Bengaluru, Karnataka 560098
      </td>
    </tr>  
    <tr>
      <td height="70">
        <small style="font-family:Helvetica, Arial, sans-serif; font-size:10px; color:#4d4d4e;">This is an auto-generated mail sent by the Patrons Pool Portal whenever a new seeker posts an idea.</small>
      </td>
    </tr>
  </tbody>
</table>
</body>
</html>
"""



EMAIL_BID_UPDATE_TEMPLATE = """
<html>
<head>
<title>Page Title</title>
</head>
<body>
<h1 style="color:red;font-size:40px;">Hello Patron!</h1>
<p style="font-family:Helvetica, Arial, sans-serif; font-size:20px; color:#4d4d4e;">Patron {email_address} placed a higher amount for idea that you bid earlier. Kindly, quickly update the bid price to win this bid before the bidding time gets over!<br/></p>
<table border="0" cellpadding="0" cellspacing="0" width="500">
  <tbody>
    
    <tr>
      <td height="64" style="font-family:Helvetica, Arial, sans-serif; font-size:18px; font-style:bold;">
        <strong>The Patrons Pool</strong>
        <br>
        <em style="font-size:17px; font-weight:400;">Where Seekers meets Patrons</em>
      </td>
    </tr>
    <tr>
      <td height="58" style="font-family:Helvetica, Arial, sans-serif; font-size:16px; color:#4d4d4e;">
        Dr. Vishnuvardhana Road Post, Channasandra, RR Nagar 
        <br> Bengaluru, Karnataka 560098
      </td>
    </tr>  
    <tr>
      <td height="70">
        <small style="font-family:Helvetica, Arial, sans-serif; font-size:10px; color:#4d4d4e;">This is an auto-generated mail sent by the Patrons Pool Portal whenever a new seeker posts an idea.</small>
      </td>
    </tr>
  </tbody>
</table>
</body>
</html>
"""