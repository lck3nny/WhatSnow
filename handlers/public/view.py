from flask import render_template
from flask.views import MethodView

__author__ = 'liamkenny'

# Duplicate method
# Needs to be consolodated
def get_item_by_id(id):
    item = {
            'id': id,
            'type': 'Snowboard',
            'brand': 'Burton',
            'model': 'Custom',
            'year': '2022',
            'params': [
                {'key': 'Size', 'unit': 'cm', 'values': ['150', '154', '154W', '156', '158', '158W', '162', '162W', '166W', '170W']}, 
                {'key': 'Effective Edge', 'unit': 'mm', 'values': ['1135', '1175', '1175', '1195', '1215', '12151255', '1255', '1255', '1295', '1335']}]
        }

    return item

class ViewItemHandler(MethodView):
    def get(r, id):
        item  = get_item_by_id(id)

        return render_template('view.html', page_name='view', data=item)


class CompareItemsHandler(MethodView):
    def get(r, ids):
        return render_template('index.html', page_name='index')