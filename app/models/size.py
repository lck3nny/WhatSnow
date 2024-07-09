
import logging, re

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
    
    # E X T R A C T   R A W   D A T A          F U N C T I O N
    # --------------------------------------------------------
    @classmethod
    def extract_raw_size_data(cls, raw_data):

        raw_data = raw_data.lower()
        logging.info(f"Raw Data: {raw_data}")

        params = {
            'size': {'aliases': ['board size', 'size', 'length'], 'found': False, 'keep': True, 'values': []},
            'binding size': {'aliases': ['binding sizes', 'binding size'], 'found': False, 'keep': False, 'values': []},
            'running length': {'aliases': ['running length'], 'found': False, 'keep': True, 'values': []},
            'nose width': {'aliases': ['nose width', 'tip width'], 'found': False, 'keep': True, 'values': []},
            'waist width': {'aliases': ['waist width'], 'found': False, 'keep': True, 'values': []},
            'tail width': {'aliases': ['tail width'], 'found': False, 'keep': True, 'values': []},
            'sidecut depth': {'aliases': ['sidecut depth'], 'found': False, 'keep': False, 'values': []},
            'sidecut': {'aliases': ['sidecut radius', 'turning radius', 'radius', 'sidecut'], 'found': False, 'keep': True, 'values': []},
            'setback': {'aliases': ['stance setback', 'stance location', 'setback'], 'found': False, 'keep': True, 'values': []},
            'effective edge': {'aliases': ['effective edge'], 'found': False, 'keep': True, 'values': []},
            'weight range': {'aliases': ['weight range'], 'found': False, 'keep': False, 'values': []},
            'reference stance': {'aliases': ['stance width', 'reference stance'], 'found': False, 'keep': True, 'values': []}
        }

        # Remove units from headings
        while re.search(r'\(([a-zA-Z]+)\)', raw_data) != None:
            match = re.search(r'\(([a-zA-Z]+)\)', raw_data)
            substr = raw_data[match.start():match.end()]
            raw_data = raw_data.replace(substr, '')

            
        breakpoints = []
        
        # Find location of headings in table
        for key, param in params.items():
            # Check each param alias
            print(param)
            for alias in param['aliases']:
                print(f"Looking for {alias}")
                if alias in raw_data:
                    breakpoints.append(raw_data.find(alias))
                    break
            
            
        # Extract table data into rows
        rows = []
        breakpoints.sort()
        for i, b in enumerate(breakpoints):
            if i > 0:
                rows.append(raw_data[breakpoints[i-1]:b])
                print(f"Row: {raw_data[breakpoints[i-1]:b]}")
            if i == len(breakpoints) -1:
                rows.append(raw_data[b:])
        
        
        # Remove lables and messy data from rows
        for row in rows:
            for key, param in params.items():
                for alias in param['aliases']:
                    if alias in row and not param['found']:
                        vals = row.replace(alias, '')
                        vals = vals.strip()
                        vals = vals.replace('\u0020\u002f\u0020', '/')
                        vals = vals.replace('\u0020\u200b\u002f\u0020', '/')
                        vals = vals.replace('\u0020\u200b\u200b\u002f\u0020', '/')
                        vals = vals.replace('cm', '')
                        vals = vals.replace('mm', '')
                        vals = vals.replace('m', '')
                        vals = vals.split() 
                        param['values'] = vals
                        param['found'] = True
                        break

        
        # Truncate long rows to the correct size
        num_sizes = len(params['size']['values'])
        for key, param in params.items():
            # Sidecuts can have more than one radius
            if param != "sidecut":
                param['values'] = param['values'][:num_sizes]

            # Remove rogue characters from row values
            if len(param['values']) > 0 and type(param['values'][0]) == str:
                for x, v in enumerate(param['values']):
                    param['values'][x] = param['values'][x].replace('\u200b', '')
            
            
            # Fill empty or missing data with null values
            for x in range(num_sizes - len(param['values'])):
                
                param['values'].append(0)
            
            
        return params
    

    @classmethod
    def save_batch_data(cls, skiboard, batch_data):

        if not skiboard.id:
            return False, 'No SkiBoard ID Found'
        
        logging.info(f"Updating SkiBoard {skiboard.id} with size data: {batch_data}")
        
        db = setupdb()
        cursor = db.cursor()
        for x in range(len(batch_data['size']['values'])):
            try:
                sql = f"""INSERT INTO sizes (
                    skiboard_id,
                    size,
                    nose_width,
                    waist_width,
                    tail_width,
                    sidecut,
                    setback,
                    effective_edge,
                    running_length
                ) VALUES (
                    '{str(skiboard.id)}',
                    '{str(batch_data['size']['values'][x])}',
                    '{float(batch_data['nose width']['values'][x])}',
                    '{float(batch_data['waist width']['values'][x])}',
                    '{float(batch_data['tail width']['values'][x])}',
                    '{str(batch_data['sidecut']['values'][x])}',
                    '{float(batch_data['setback']['values'][x])}',
                    '{float(batch_data['effective edge']['values'][x])}',
                    '{float(batch_data['running length']['values'][x])}'
                )"""

                cursor.execute(sql)
                db.commit()
            except Exception as e:
                print(f"ERROR: size ({batch_data['size']['values'][x]})\n{e}\n")
                return False, f"An error occured: {e}"
        
        return True, "Successfully added sizes to skiboard"
    
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
