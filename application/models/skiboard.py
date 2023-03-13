from operator import itemgetter
from firebase_admin import firestore

__author__ = 'liamkenny'

# --------------------------------------------------
# Is Duplicate                       F U N C T I O N
# --------------------------------------------------
def is_duplicate(type, brand, model, year):

    # Check firestore for duplicate entries
    db = firestore.client()
    skiboards = db.collection('SkiBoards').where('type', '==', type).where('brand', '==', brand).where('model', '==', model).where('year', '==', year).get()
    if skiboards.exists:
        # ToDo...
        # Return existing skiboard ID???
        return [True, skiboards]

    return False


# --------------------------------------------------
# Get By Item ID                     F U N C T I O N
# --------------------------------------------------
def get_item_by_id(id='obeW2NkdphpUYzOrTDDy'):

    # Get firestore doc by ID
    db = firestore.client()
    skiboard = db.collection('SkiBoards').document(id).get()
    collection_docs = db.collection('SkiBoards').document(id).collection('Sizes').get()
    collections = []
    if skiboard.exists:
        for doc in collection_docs:
            collections.append(doc.to_dict())
        
        # Sort collections by size parameter
        collections = sorted(collections, key=itemgetter('size'))
        return skiboard, collections

    return False

