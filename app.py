import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource
from marshmallow import Schema, fields

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['RESTY_JSON'] = {"ensure_ascii": False}
db = SQLAlchemy(app)
api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genres_ns = api.namespace('genres')


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


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        director_id = request.args.get('director_id', type=int)
        genre_id = request.args.get('genre_id', type=int)
        if director_id and genre_id:
            movies = db.session.query(Movie).filter(Movie.director_id == director_id, Movie.genre_id == genre_id).all()
            return movies_schema.dump(movies), 200
        if director_id:
            movies = db.session.query(Movie).filter(Movie.director_id == director_id).all()
            return movies_schema.dump(movies), 200
        if genre_id:
            movies = db.session.query(Movie).filter(Movie.genre_id == genre_id).all()
            return movies_schema.dump(movies)
        all_movies = db.session.query(Movie).all()
        return movies_schema.dump(all_movies), 200


    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return "", 201


@movie_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid):
        try:
            movie = db.session.query(Movie).get(mid)
            return movie_schema.dump(movie), 200
        except Exception as e:
            return str(e), 404


    def put(self, mid):
        try:
            movie = db.session.query(Movie).get(mid)
        except Exception as e:
            return str(e), 404

        req_json = request.json

        movie.title = req_json.get("title")
        movie.description = req_json.get("description")
        movie.trailer = req_json.get("trailer")
        movie.year = req_json.get("year")
        movie.rating = req_json.get("rating")
        movie.genre_id = req_json.get("genre_id")
        movie.director_id = req_json.get("director_id")

        db.session.add(movie)
        db.session.commit()
        return "", 204


    def patch(self, mid):
        try:
            movie = db.session.query(Movie).get(mid)
        except Exception as e:
            return str(e), 404

        req_json = request.json
        if "title" in req_json:
            movie.title = req_json.get("title")
        if "description" in req_json:
            movie.description = req_json.get("description")
        if "trailer" in req_json:
            movie.trailer = req_json.get("trailer")
        if "year" in req_json:
            movie.year = req_json.get("year")
        if "rating" in req_json:
            movie.rating = req_json.get("rating")
        if "genre_id" in req_json:
            movie.genre_id = req_json.get("genre_id")
        if "director_id" in req_json:
            movie.director_id = req_json.get("director_id")

        db.session.add(movie)
        db.session.commit()
        return "", 204


    def delete(self, mid):
        movie = db.session.query(Movie).get(mid)
        db.session.delete(movie)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
