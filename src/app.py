"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, FavoritePlanet
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/search', methods=['GET'])
def get_form():
       return '''
        <form action="/search">
            <label for="planet_id">Planet ID:</label>
            <input type="number" id="planet_id" name="planet_id">
            <input type="submit" value="Search">
        </form>
        '''

@app.route('/planet', methods = ['POST'])
def post_planet():
    body = request.get_json()

    planet_name = body['planet_name']
    population = body['population']
    planet = Planet(planet_name=planet_name, population=population)
    db.session.add(planet)
    db.session.commit()

    return jsonify({'msg': 'Planet inserted with id ' + str(planet.id)}), 200




@app.route('/word-size/<string:word>', methods=['GET'])
def get_word_size(word):
   return str(len(word)), 200


@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


# [POST] /favorite/user/<int:user_id>/planet/<int:planet_id> Añade un nuevo planet favorito al usuario actual con el planet id = planet_id.
@app.route('/favorite/user/<int:user_id>/planet/<int:planet_id>', methods=['POST'])
def post_favorite_planet(user_id, planet_id):
    
    print(str(user_id))
    print(str(planet_id))


    favorite_planet = FavoritePlanet(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite_planet)
    db.session.commit()

    return jsonify({'msg': 'Favorited planet  success ' + str(favorite_planet.insertion_date)}), 200


#[GET] /favorite/user/<int: user_id> Listar todos los favoritos que pertenecen al usuario actual.
@app.route('/favorite/user/<int:user_id>/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite(user_id, planet_id):
    favorite = FavoritePlanet.query.filter_by(user_id=user_id, planet_id= planet_id).first()
    
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'msg': 'Favorito eliminado correctamente'}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
