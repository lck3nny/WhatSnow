from datetime import datetime
from flask import render_template, redirect, session, flash, request
from flask.views import MethodView

__author__ = 'liamkenny'

def is_duplicate(type, brand, model, year):
    return False

def get_item_by_id(id):
    item = {
            'type': 'Snowboard',
            'brand': 'Burton',
            'model': 'Custom',
            'year': '2022'
        }
    return item

class NewImportHandler(MethodView):
    def get(r):
        #return redirect('/')
        return render_template('imports.html', page_name='imports')

    def post(r):
        import_type = request.form.get('type')
        brand = request.form.get('brand')
        model = request.form.get('model')
        year = request.form.get('year')
        if is_duplicate(import_type, brand, model, year):
            flash('Looks like we already have a listing for this item. Check it out <a href="/" class="alert-link">here</a>')
            return redirect('/import')

        # Save ski / board to database
        id = 123
        return redirect('/import/{}/'.format(id))

class ImportDetailsHandler(MethodView):
    def get(r, id):
        new_item = get_item_by_id(id)
        if not new_item:
            flash('There was a problem with your connection. Please restart the import process.')
            return redirect('/import')
        
        item = {
            'type': 'Snowboard',
            'brand': 'Burton',
            'model': 'Custom',
            'year': '2022'
        }
        return render_template('import_details.html', page_name='import_details', import_item=item)

    def post(r, id):
        from ... import app
        raw_data = request.form['data_table']
        item = get_item_by_id(id)

        # Logging imported data
        # ------------------------------------------------------------
        msg = "\nSize Chart Submitted: \n{}".format(raw_data)

        app.logger.info("Submitted Data:")
        app.logger.info(msg)

        f = open("logs.txt", "a")
        f.write("{}\nLOGGING... {}\n\n".format(datetime.now(), msg))
        f.close()
        # ------------------------------------------------------------

        # Extract Data from raw table
        # ------------------------------------------------------------
        params = []
        f = open("logs.txt", "a")
        f.write("{}\nEXTRACTING...".format(datetime.now()))
        for line in raw_data.split('\n'):
            f.write("\n{}".format(line))
            split_line = line.split(" ")
            
            line_name = " ".join(split_line[:-1])
            f.write("\nName: {}".format(line_name))

            units = str(line)[line.find('(') +1:line.find(')')]
            f.write("\nUnits: {}".format(units))
            
            values = split_line[-1].split('\t')[1:]
            for x, v in enumerate(values):
                values[x] = v.replace("\r", "")
            f.write("\nValues: {}".format(values))

            params.append({'model_name': line_name, 'unit': units, 'values': values})


        f.close()
        # ------------------------------------------------------------

        data = {
            'id': id,
            'type': item['type'],
            'brand_name': item['brand'],
            'model_name': item['model'],
            'year': item['year'],
            'params': params
        }
        

        return render_template('import_complete.html', page_name='import_complete', item_type=data['type'], item_id=id)

