import logging
from flask import render_template, redirect, flash
from flask.views import MethodView

# Model Imports
# --------------------------------------------------
import application.models.skiboard as SkiBoard

__author__ = 'liamkenny'

item_names = ['asym']

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# V I E W   I T E M                    H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ViewHandler(MethodView):
    # ---------------------------------------- G E T
    def get(self, slug):
        skiboard, collections = SkiBoard.get_item_by_slug(slug)
        if not skiboard:
            logging.error("Could not collect SkiBoard: {}".format(id))
            flash('We could not find a ski or board with that ID. Please try again.')

            return redirect('/')
        
        if collections:
            skiboard['collections'] = collections

        logging.info("Collecting SkiBoard Data:\n{}".format(skiboard))
        return render_template('views/view.html', page_name='view', skiboard=skiboard)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# C O M P A R E   I T E M              H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class CompareHandler(MethodView):
    # ---------------------------------------- G E T
    def get(self, slugs):

        if not slugs:
            return redirect('/')

        msg = "Collecting SkiBoard Data:"
        # Collect each item to be compared
        skiboards = []
        slugs = slugs.split('+')
        logging.info("Comparing SkiBoards:\n{}".format(slugs))
        for slug in slugs:
            sizes = slug[slug.index('[') +1 : slug.index(']')]
            slug = slug.replace('[{}]'.format(sizes), '')
            sizes = sizes.split(',')
            logging.info("Slug: {}".format(slug))
            logging.info("Sizes: {}".format(sizes))
            skiboard, collections = SkiBoard.get_item_by_slug(slug)

            if not skiboard:
                flash('We had trouble finding one or more of your comparisons.')
                return redirect('/')
            else:
                if collections:
                    skiboard['collections'] = []
                    for collection in collections:
                        if 'size' in collection.keys() and collection['size'] in sizes:
                            skiboard['collections'].append(collection)

                skiboards.append(skiboard)

                msg += '\n{}'.format(skiboard)
    
        logging.info(msg)
        if not skiboards:
            return redirect('/')
        
        return render_template('core/index.html', page_name='index', skiboards=skiboards)