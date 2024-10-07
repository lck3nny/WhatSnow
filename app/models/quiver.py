
import logging, re

# A P P L I C A T I O N                          I M P O R T S
# ------------------------------------------------------------
from app.core import setupdb



# ------------------------------------------------------------
# / / / / / / / / / / / / / / /  \ \ \ \ \ \ \ \ \ \ \ \ \ \ \
# ============================================================
# Q U I V E R                                        C L A S S
# ============================================================
# \ \ \ \ \ \ \ \ \ \ \ \ \ \ \  / / / / / / / / / / / / / / /
# ------------------------------------------------------------
class Quiver():
        
    def __init__(self, user_id, skiboard_id, size):
        self.user_id = user_id
        self.skiboard_id = skiboard_id
        self.size = size

    # G E T   Q U I V E R   I T E M            F U N C T I O N
    # --------------------------------------------------------
    @classmethod
    def get(cls, skiboard_id = None, user_id = None, size = None):

        db = setupdb()
        cursor = db.cursor()

        if not skiboard_id and not user_id and not size:
            sql = "SELECT * FROM QuiverItems ORDER BY user_id ASC"
            cursor.execute(sql)
            results = cursor.fetchall()
            

        
    