import logging
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
        app.logger.info("Printing request variables:")
        data = request.form['data_table']

        msg = "\nSize Chart Submitted: \n{}".format(data)
        f = open("logs.txt", "a")
        f.write("{}\nLOGGING... {}\n\n".format(datetime.now(), msg))
        f.close()

        app.logger.info(msg)
        

        return render_template('import_complete.html', page_name='import_complete')

