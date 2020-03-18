from app import db


def user_exists(email):
    query = {"email": email}
    result = db['user'].find_one(query)
    
    if bool(result):
        return result
    return False


def save_user(user_info):
    db['user'].insert_one(user_info)
