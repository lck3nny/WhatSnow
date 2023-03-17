import pytz
from datetime import datetime
from firebase_admin import firestore 

__author__ = 'liamkenny'

def get_user(id=None, email=None):
    if not id and not email:
        return False

    db = firestore.client()
    if id:
        # Get user by ID
        col_ref = db.collection('Users')
        doc_ref = col_ref.document(id)
        user = doc_ref.get()
    else:
        # Get user by email
        col_ref = db.collection('Users')
        user = col_ref.where('email', '==', email).get()[0]

    if not user.exists:
        return False

    return user


def update_user(id, obj={}):
    if not id:
        return False, None

    # Remove non-editable params
    update_params = ['fname', 'lname']
    for key in obj:
        if key not in update_params:
            obj.pop(key)

    obj['updated'] = datetime.now(pytz.timezone('Canada/Pacific'))

    msg = "update_user() - Object:\n{}\n".format(obj)
    f = open("logs.txt", "a")
    f.write("{}\nLOGGING... {}\n\n".format(datetime.now(pytz.timezone('Canada/Pacific')), msg))
    f.close()

    try:
        # Update user object
        db = firestore.client()
        col_ref = db.collection('Users')
        user = col_ref.document(id)
        user.update(obj)
    except:
        return False, None

    return True, user.get()
    
        
    

    
