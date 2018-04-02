from flask import Flask, render_template, url_for, request, redirect, jsonify, flash

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Reviews, ReviewsImages

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
    return render_template('reviews.html', reviews=reviews)