import pytz
import json
import logging
from datetime import datetime
from firebase_admin import firestore 
from operator import itemgetter

__author__ = 'liamkenny'

class User():

    # --------------------------------------------------
    # Create New User                    F U N C T I O N
    # --------------------------------------------------
    def create(fname, lanme, email, ski=None, snowboard=[None, None], permissions=[]):
        # Creating a document using 'add'
        db = firestore.client()
        try:
            create_time, user = db.collection('Users').add({
                'email': email,
                'fname': fname,
                'lname': lname,
                'ski': ski,
                'snowboard': snowboard,
                'created': datetime.now(pytz.timezone('Canada/Pacific')),
                'updated': datetime.now(pytz.timezone('Canada/Pacific')),
                'permissions': permissions
            }) 
            logging.info("New Firestore User Created: \n{}\n".format(json.dumps(user)))  
        except Exception as e:
            logging.error("Could not create new skiboard:\n{}".format(e))   
            return e, None

        return True, user

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
            collections = []
            
            for doc in collection_docs:
                quiver_id = doc.id
                skiboard = doc.to_dict()
                skiboard['id'] = quiver_id
                collections.append(skiboard)
            
            # Sort collections by size parameter
            collections = sorted(collections, key=itemgetter('skiboard'))
            return user, collections

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
            doc_ref = col_ref.document(id)
            user_doc = doc_ref.get()
            user = user_doc.to_dict()
            
        except Exception as e:
            logging.error(e)
            return False
        
        user['id'] = doc_ref.id

        logging.info("User: {}".format(user))
        # Check for admin permissions
        if not 'permissions' in user:
            logging.warning("Permissions not found for user")
            user['permissions'] = []
            user['updated'] = datetime.now(pytz.timezone('Canada/Pacific'))
            user_doc.update(user)
        
        logging.info("User: {}".format(user))

        if not 'admin' in user['permissions']:
            return False
        
        return True
        

    # --------------------------------------------------
    # Add To Quiver                      F U N C T I O N
    # --------------------------------------------------
    def add_to_quiver(id, skiboard, size):
        if not id or not skiboard or not size:
            return False
        
        db = firestore.client()
        col_ref = db.collection('Users')
        doc_ref = col_ref.document(id)

        logging.info("Adding skiboard to quiver: {}".format(skiboard))

        try:
            doc_ref.collection('Quiver').add({
                'skiboard': skiboard['slug'],
                'size': size,
                'added': datetime.now(pytz.timezone('Canada/Pacific'))
            })
        except Exception as e:
            logging.error("Could not add skiboard to quiver: {}".format(e))
            return e
        
        logging.info("Added skiboard to {}'s quiver: {} - {}".format(id, skiboard, size))
        return True    


    # --------------------------------------------------
    # Remove From Quiver                 F U N C T I O N
    # --------------------------------------------------
    def remove_from_quiver(user_id, quiver_id):
        if not user_id or not quiver_id:
            return False
        db = firestore.client()
        col_ref = db.collection('Users')
        doc_ref = col_ref.document(user_id)

        logging.info("Removing skiboard from quiver: {} / {}".format(user_id, quiver_id))

        try:
            doc_ref.collection('Quiver').document(quiver_id).delete()
        except Exception as e:
            logging.error(e)
            return e
        
        return True


