from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os
import logging
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

db_path = 'sqlite:///' + os.path.join(basedir, 'todo.db')
print(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# db.Model.metadata.reflect(db.engine)

class Movies(db.Model):
    __tablename__ = 'movie_shows'
    index = db.Column(db.Integer, primary_key=True)
    Theatre = db.Column(db.String(30))
    Time = db.Column(db.String(30))
    type = db.Column(db.String(10))
    TotalSeats = db.Column(db.Integer)
    SeatsAvailable = db.Column(db.Integer)
    Cost = db.Column(db.String(30))
    Longitude = db.Column(db.Float)
    Latitude = db.Column(db.Float)
    Movie = db.Column(db.String(30))
    City = db.Column(db.String(30))

    def __repr__(self):
        return f'<Task {self.Movie}>'

@app.route("/")
def home():
    movie_list = Movies.query.all()
    logging.info(movie_list)
    return render_template("base.html", data=movie_list) 

@app.route("/movies",  methods=["GET", "POST"])
def theatre_level():
    movie = request.args.get("movie")
    movie_list = Movies.query.filter_by(Movie=movie).all()
    logging.info(movie_list[0])
    return render_template("movie.html", data=movie_list) 

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
