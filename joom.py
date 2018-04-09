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
@app.route('/')
@app.route('/reviews')
def reviews():

    reviews = session.query(Reviews).all()
    images = session.query(ReviewsImages).all()
    categories = session.query(Categories).all()

    return render_template('reviews.html', reviews=reviews, images=images, categories=categories)


@app.route('/categories')
def categories():

    categories = session.query(Categories).all()
    #return render_template('reviews.html', reviews=reviews)
    for cat in categories:
        print(cat.category_name)
    return


# admin page
@app.route('/comand')
def comand():


    return

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)