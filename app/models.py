from app import db


def user_exists(email):
    query = {"email": email}
    result = db['users'].find_one(query)
    
    if bool(result):
        return result
    return False


def save_user(user_info):
    db['users'].insert_one(user_info)


def store_posts(post_info):
    db['posts'].insert_one(post_info)
