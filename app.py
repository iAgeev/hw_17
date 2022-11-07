# app.py
import json

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False

app.url_map.strict_slashes = False

db = SQLAlchemy(app)

api = Api(app)
ns_movie = api.namespace('movies')
ns_director = api.namespace('directors')
ns_genre = api.namespace('genres')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()



class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@ns_movie.route('/')
class MoviesView(Resource):

    def get(self):
        all_movies = db.session.query(Movie)

        director_id = request.args.get("director_id")
        if director_id is not None:
            all_movies = all_movies.filter(Movie.director_id == director_id)

        genre_id = request.args.get("genre_id")
        if genre_id is not None:
            all_movies = all_movies.filter(Movie.genre_id == genre_id)

        return movies_schema.dump(all_movies), 200

    def post(self):
        movie_data = request.json
        new_movie = Movie(**movie_data)

        with db.session.begin():
            db.session.add(new_movie)

        return "The movie has been added", 201


@ns_movie.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid):
        movie = Movie.query.get(uid)
        return movie_schema.dump(movie), 200

    def put(self, uid):

        update_movie = db.session.query(Movie).filter(Movie.id == uid).update(request.json)

        if update_movie != 1:
            return "", 404

        # movie.title = new_movie.title
        # movie.description = new_movie["description"]
        # movie.trailer = new_movie["trailer"]
        # movie.year = new_movie["year"]
        # movie.rating = new_movie["rating"]
        # movie.genre_id = new_movie["genre_id"]
        # movie.director_id = new_movie["director_id"]
        #
        # db.session.add(movie)
        # db.session.commit()
        return "The data has been updated", 201

@ns_director.route('/')
class DirectorsView(Resource):

    def get(self):
        all_directors = db.session.query(Director)
        return directors_schema.dump(all_directors), 200


@ns_director.route('/<int:uid>')
class DirectorView(Resource):
    def get(self, uid):
        director = Director.query.get(uid)
        return director_schema.dump(director), 200


@ns_genre.route('/')
class GenresView(Resource):

    def get(self):
        all_genres = db.session.query(Genre)
        return genres_schema.dump(all_genres), 200


@ns_genre.route('/<int:uid>')
class GenreView(Resource):
    def get(self, uid):
        genre = Genre.query.get(uid)
        return genre_schema.dump(genre), 200



if __name__ == '__main__':
    app.run(debug=True)
