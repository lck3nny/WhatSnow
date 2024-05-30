
import logging

# A P P L I C A T I O N                          I M P O R T S
# ------------------------------------------------------------
from app.core import setupdb



# ------------------------------------------------------------
# / / / / / / / / / / / / / / /  \ \ \ \ \ \ \ \ \ \ \ \ \ \ \
# ============================================================
# S I Z E                                            C L A S S
# ============================================================
# \ \ \ \ \ \ \ \ \ \ \ \ \ \ \  / / / / / / / / / / / / / / /
# ------------------------------------------------------------
class Size():

    def __init__(self, skibaord_id, size, nose_width, waist_width, tail_width, sidecut, setback, effective_edge):
        self.skibaord_id = skibaord_id
        self.size = size
        self.nose_width = nose_width
        self.waist_width = waist_width
        self.tail_width = tail_width
        self.sidecut = sidecut
        self.setback = setback
        self.effective_edge = effective_edge


    # G E T   A L L   S I Z E S                F U N C T I O N
    # --------------------------------------------------------
    @classmethod
    def get(cls, skiboard_id):

        db = setupdb()
        cursor = db.cursor()

        try:
            sql = f"SELECT * FROM Sizes WHERE skiboard_id = {skiboard_id}"
            cursor.execute(sql)
            results = cursor.fetchall()
        except Exception as e:
            logging.error(f"Could not retreive sizes for skiboard: {skiboard_id}")

        sizes = []
        for r in results:
            size = Size(
                skibaord_id=skiboard_id,
                size=r[1],
                nose_width=r[2],
                waist_width=r[3],
                tail_width=r[4],
                sidecut=r[5],
                setback=r[6],
                effective_edge=r[9]
            )
            sizes.append(size)

        return sizes



    # U P D A T E                        F U N C T I O N
    # --------------------------------------------------
    def update(self):
        return True
