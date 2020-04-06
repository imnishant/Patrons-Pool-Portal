from app import db


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

def store_posts(post_info):
    db['posts'].insert_one(post_info)
