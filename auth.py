
from flask import session, request
from models import User

def check_login():
    # check if user id is in session
    user_id = None
    if 'id' in session:
        user_id = session['id']
    else:
        # get user id from cookies
        user_id = request.cookies.get('id')
    if user_id is not None:
        current_user = User.query.filter(User.id == user_id).first()
        return current_user
    return None


    