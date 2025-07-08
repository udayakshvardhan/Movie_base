import sqlite3
from flask_bootstrap import Bootstrap
from flask import Flask, request, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField
import requests
import gunicorn
from flask_sqlalchemy import SQLAlchemy
from wtforms.fields.simple import SubmitField, TextAreaField


db = sqlite3.connect("movies2.db")
app = Flask(__name__)
app.secret_key = "syam"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies2.db'
Bootstrap(app)
db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    date = db.Column(db.String(50))
    movie_id = db.Column(db.Integer)
    des = db.Column(db.String(5000))
    url = db.Column(db.String(250))
    review = db.Column(db.String(250))
    rating = db.Column(db.String(250))

app.app_context().push()
db.create_all()

api_key = "b42915038ddb6a2a7abe8112028d0b09"
url = "https://api.themoviedb.org/3/search/movie"
img_url = "https://image.tmdb.org/t/p/w500"

movie_names = []
class Form(FlaskForm):
    movie_name= StringField(label="MOVIE TITLE")
    submit = SubmitField(label="ADD MOVIE")

class Update(FlaskForm):
    rating = StringField(label="RATING")
    review = TextAreaField(label="REVIEW")
    submit = SubmitField(label="ADD MOVIE")

@app.route('/')
def home():
    data = db.session.query(Movie).all()
    return render_template("movies.html", data=data)

@app.route('/add_movie')
def add_movies():
    form = Form()
    return render_template("add_movie.html", form=form)

@app.route('/select_movie', methods=['POST', 'GET'] )
def gather_movies():
    form = Form()
    movie_names.clear()
    response = requests.get(url, params={"api_key": api_key, "query": form.movie_name.data})
    response.close()
    for movie in response.json()["results"]:
        movie_names.append({"title": movie['title'], "date": movie['release_date'], "id":movie["id"],
                            "des": movie['overview'], 'image_url': movie['poster_path']})
    return render_template("select_movie.html", movies=movie_names)

@app.route('/add_to_database/<movie_title>/<movie_date>/<movie_id>/<image_url>/<movie_des>')
def update_db(movie_title, movie_date, movie_id,image_url, movie_des):
    movie_details = Movie(title=movie_title, date=movie_date, movie_id=movie_id, des=movie_des,
                          url=f"{img_url}/{image_url}")
    db.session.add(movie_details)
    db.session.commit()
    return redirect(url_for("home"))

@app.route('/delete/<movie_name>')
def delete(movie_name):
    movie = Movie.query.filter_by(title=movie_name).first()
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))

@app.route('/update/<movie_name>')
def update_page(movie_name):
    form = Update()
    return render_template("update.html", form=form, title=movie_name)

@app.route('/update_movie/<title>', methods=['POST', 'GET'])
def update_movie(title):
    form = Update()
    movie_to_update = Movie.query.filter_by(title=title).first()
    movie_to_update.rating = form.rating.data
    db.session.commit()
    movie_to_update.review = form.review.data
    db.session.commit()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)