
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

    def __init__(self, skiboard_id, size, nose_width, waist_width, tail_width, sidecut=0, setback=0, effective_edge=0):
        self.skiboard_id = skiboard_id
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
                skiboard_id=skiboard_id,
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
    
    # S A V E                                  F U N C T I O N
    # --------------------------------------------------------
    def save(self):
        db = setupdb()
        cursor = db.cursor()

        if not self.nose_width:
            self.nose_width = 0
            
        if not self.waist_width:
            self.waist_width = 0

        if not self.tail_width:
            self.tail_width = 0

        if not self.sidecut:
            self.sidecut = 0

        if not self.setback:
            self.setback = 0

        if not self.effective_edge:
            self.effective_edge = 0

        if self.skiboard_id:
            logging.info("Updating existing size")
            sql = f"""REPLACE INTO Sizes (skiboard_id, size, nose_width, waist_width, tail_width, sidecut, setback, effective_edge) 
            values(
            '{str(self.skiboard_id)}',
            '{str(self.size)}', 
            {float(self.nose_width)}, 
            {float(self.waist_width)}, 
            {float(self.tail_width)}, 
            {float(self.sidecut)}, 
            {float(self.setback)}, 
            {float(self.effective_edge)}
            )"""
            
        else:
            logging.info("Inserting new size")
            sql = f"""INSERT INTO Sizes (skiboard_id, size, nose_width, waist_width, tail_width, sidecut, setback, effective_edge) 
            values(
            '{str(self.skiboard_id)}',
            '{str(self.size)}', 
            {float(self.nose_width)}, 
            {float(self.waist_width)}, 
            {float(self.tail_width)}, 
            {float(self.sidecut)}, 
            {float(self.setback)}, 
            {float(self.effective_edge)}
            )"""

        
        try:
            logging.info(f"About to execute SQL: {sql}")
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            logging.error(f"Could not save Size:\n{e}")
            return False

        logging.info(f"Saved SkiBoard Size:\nSkiBoard: {self.skiboard_id}")

        # ToDo...
        # Update ElasticSearch
        '''
        successes = 0
        logging.info("Uploading SkiBoard to ElasticSearch")
        es.update(
            id=self.id,
            index='SkiBoards',
            document=self.__dict__
        )   
        '''
        

        return True



    # U P D A T E                        F U N C T I O N
    # --------------------------------------------------
    def update(self):
        return True
