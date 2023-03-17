from firebase_admin import firestore 

__author__ = 'liamkenny'

def get_user(id=None, email=None):
    if not id and not email:
        return False

    db = firestore.client()
    if id:
        # Get user by ID
        user = db.collection('Users').document(id).get()
    else:
        # Get user by email
        users = db.collection('Users').where('email', '==', email).get()
        user = users[0]

    if not user.exists:
        return False

    return user


def update_user(doc_ref, obj={}):
    if not doc_ref:
        return False

    # Remove non-editable params
    update_params = ['fname', 'lname']
    for key in obj:
        if key not in update_params:
            obj.pop(key)

    # Update user object
    doc_ref.update(obj)
    
        
    

    
