import pytz
import logging
from datetime import datetime
from firebase_admin import firestore 

__author__ = 'liamkenny'

# --------------------------------------------------
# Get User                           F U N C T I O N
# --------------------------------------------------
def get_user(id=None, email=None, quiver=False):
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
    
    if quiver:
        collection_docs = db.collection('Users').document(id).collection('Quiver').get()

    return user

# --------------------------------------------------
# Update User                        F U N C T I O N
# --------------------------------------------------
def update_user(id, obj={}):
    if not id:
        return None, "No ID"

    # Remove non-editable params
    update_params = ['fname', 'lname']
    for key in obj:
        if key not in update_params:
            obj.pop(key)

    obj['updated'] = datetime.now(pytz.timezone('Canada/Pacific'))

    # Collect and update user object
    try:
        logging.info("update_user() - Object:\n{}\n".format(obj))
        db = firestore.client()
        col_ref = db.collection('Users')
        user = col_ref.document(id)
        user.update(obj)
    except Exception as e:
        return None, e

    return user.get(), None


# --------------------------------------------------
# Is Admin User                      F U N C T I O N
# --------------------------------------------------
def is_admin(id):
    if not id:
        return False
    
    # Collect user object
    try:
        db = firestore.client()
        col_ref = db.collection('Users')
        user = col_ref.document(id)
    except:
        return False

    # Check for admin permissions
    if not 'admin' in user.permissions:
        return False
    
    return True
    
        
    

    
