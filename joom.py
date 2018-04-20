from flask import Flask, render_template, url_for, request, redirect, jsonify, flash

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Reviews, ReviewsImages, Categories


app = Flask(__name__)

engine = create_engine('sqlite:///joom.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Making an API Endpoint (GET request)
@app.route('/', methods=['GET'])
@app.route('/reviews', methods=['GET'])
def reviews():
    REVIEWS_PER_PAGE = 100
    page = 0
    if request.args.get('page'):
        try:
            page = int(request.args.get('page'))
        except ValueError:
            page = 0

    reviews_count = session.query(Reviews).count()
    pages_count = int(reviews_count/REVIEWS_PER_PAGE)
    print(pages_count)
    offset = page * REVIEWS_PER_PAGE

    reviews = session.query(Reviews).limit(REVIEWS_PER_PAGE).offset(offset)
    images = session.query(ReviewsImages).all()
    categories = session.query(Categories).all()

    pagination = {'current_page': page,
                  'next_page': page+1,
                  'prev_page': page-1,
                  'pages_count': pages_count
                  }
    return render_template('reviews.html',
                           reviews=reviews,
                           images=images,
                           categories=categories,
                           pagination=pagination
                           )


@app.route('/categories')
def categories():

    categories = session.query(Categories).filter_by(parent_id=None).all()

    return render_template('categories.html', categories=categories)


# admin page
@app.route('/command')
def command():

    return

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)