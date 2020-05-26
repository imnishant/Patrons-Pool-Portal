from flask_mail import Message

from app import db, mail
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


def get_posts(email):
   query = {"email": email}
   result = db['user'].find_one(query)

   if bool(result):
       return result['posts']
   return False


def get_sponser_timeline():
    query = {"isSponsor" : 0}
    users = list(db['user'].find(query))
    posts = []

    for user in users:
        username = user['email']
        userposts = user['posts']
        for post in userposts:
            post['username'] = username
            post['name'] = user['profile']['fname'] + " " + user['profile']['lname']

            current_time = int(datetime.datetime.now().timestamp())
            window_in_seconds = 600

            first_bidding_time = post['first_bidding_time']
            if first_bidding_time == "N/A":
                post['bidding_status'] = "open"

            elif current_time - int(first_bidding_time) < window_in_seconds:
                post['bidding_status'] = "open"

            else:
                post['bidding_status'] = "closed"

            set_new_bid_update_status(post['username'], post['post_headline'], post['bidding_status'])

            posts.append(post)

    print(posts)
    #  return result
    return posts


def set_new_bid_update_status(email, headline, get_new_update):
    update_query = {"email": email, "posts.post_headline": headline}
    db['user'].update_one(update_query, {"$set": {"posts.$.bidding_status": get_new_update}})
    return


def email_bid_status_to_other_sponsers(email, headline):
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

    if bidding_status == 'open':
        msg = Message('Bid Update', sender='bid-update@patronspool.com', recipients=bidding_person_emails)
        msg.body = "The sponser " + session['username'] + " placed a higher bid for the idea for which you bid earlier. Place more amount to win the bid before the bidding time gets over! "
        mail.send(msg)

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


def mail_sponsers_when_a_post_is_added():
    query = {"isSponsor": 1}
    sponsers = list(db['user'].find(query))
    email_ids = []

    if sponsers:
        for sponser in sponsers:
            email_ids.append(sponser['email'])

        msg = Message('New Post Added', sender='post-update@patronspool.com', recipients=email_ids)
        msg.body = session['username'] + " posted a new idea. Log in to the portal to view more about it and check if you would like to sponser for it!"
        mail.send(msg)
        return
    return
