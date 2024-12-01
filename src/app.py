'''
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
'''
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Characters, Planets, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv('DATABASE_URL')
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace('postgres://', 'postgresql://')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
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


# ENDPOINTS 'GET'

@app.route('/user', methods = ['GET'])
def handle_hello():

    response_body = {
        'msg': 'Hello, this is your GET /user response'
    }

    return jsonify(response_body), 200

@app.route('/users', methods = ['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify({'All The users': users}), 200

@app.route('/characters', methods = ['GET'])
def get_characters():
    characters = Characters.query.all()
    return jsonify(characters), 200

@app.route('/character/<int:character_id>', methods = ['GET'])
def get_character_by_id(character_id):
    character_filter = Characters.query.filter_by(id = character_id)
    
    character_to_found = [character.serialize() for character in character_filter]
    
    if character_to_found:
        return jsonify(character_to_found), 200
    else:
        return jsonify({'Error': 'character not found'}), 404

@app.route('/planets', methods = ['GET'])
def get_planets():
    planets = Planets.query.all()
    serialize_planets = [planet.serialize() for planet in planets]
    return jsonify(serialize_planets), 200

@app.route('/planet/<int:planet_id>', methods = ['GET'])
def get_planet_by_id(planet_id):
    planet_filter = Planets.query.filter_by(id = planet_id).first()
    
    if planet_filter:
        return jsonify({'Planet': planet_filter.serialize(), 'message': 'was successfully found'}), 200
    else:
        return jsonify({'Error': 'planet not fonud'}), 404

@app.route('/users/favorites/<int:user_id>', methods = ['GET'])
def get_favorites_of_user(user_id):
    favorites_of_user = Favorites.query.filter_by(user_id = user_id).all()
      
    if favorites_of_user:
        return jsonify({'Favorites:': [favorite.serialize() for favorite in favorites_of_user]}), 200
    else:
        return jsonify({'Error': 'favorite not found'}), 404
    
    
# ENDPOINTS 'POST'

@app.route('/create/user', methods = ['POST'])
def create_user():
    body = request.json
    email = body.get('email')
    password = body.get('password')
    is_active = body.get('is_active')
    
    new_user = User(email = email, password = password, is_active = is_active)
    
    db.session.add(new_user)
    try: 
        db.session.commit()
        return 'User Created'
    except Exception as error:
        db.session.rollback()
        return 'An Error Ocurred', 500

@app.route('/create/planet', methods = ['POST'])
def create_planet():
    body = request.json
    name = body.get('name')
    image_src = body.get('image_src')
    description = body.get('description')
    
    new_planet = Planets(name = name, image_src = image_src, description = description)
    
    db.session.add(new_planet)
    try:
        db.session.commit()
        return 'Planet Created'
    except Exception as error:
        db.session.rollback()
        return 'An Error Ocurrer', 500
    
@app.route('/create/character', methods = ['POST'])
def create_character():
    body = request.json
    name = body.get('name')
    image_src = body.get('image_src')
    description = body.get('description')
    
    new_character = Characters(name = name, image_src = image_src, description = description)
    
    db.session.add(new_character)
    try:
        db.session.commit()
        return 'Character Created'
    except Exception as error:
        db.session.rollback()
        return 'An Error Ocurred', 500

@app.route('/favorite/character/<int:character_id>', methods = ['POST'])
def add_new_favorite_character(character_id):
    body = request.json
    user_id = body.get('user_id')

    if user_id is None:
        return jsonify({'Error': 'user id and character id required'}), 404
    
    new_favorite_character = Favorites(user_id = user_id, characters_id = character_id)
    
    db.session.add(new_favorite_character)
    try:
        db.session.commit()
        return 'A character was added to Favorites'
    except Exception as error:
        db.session.rollback()
        print(error)
        return 'An Error Ocurred', 500      
    
    
@app.route('/favorite/planet/<int:planets_id>', methods = ['POST'])
def add_favorite_planet(planets_id):
    body = request.json
    user_id = body.get('user_id')
    
    if user_id is None:
        return jsonify({'Error': 'user id and planet id required'}), 404
    
    new_favorite_planet = Favorites(user_id = user_id, planets_id = planets_id)
    
    db.session.add(new_favorite_planet)
    try:
        db.session.commit()
        return 'A planet was added to Favorites'
    except Exception as error:
        db.session.rollback()
        return 'An Error Ocurred', 500
    
@app.route('/user/delete/favorite/<int:favorite_id>', methods = ['DELETE'])
def delete_favorite_character(favorite_id):
    favorite_filter = Favorites.query.filter_by(id = favorite_id).one_or_none()
    
    if favorite_filter is None:
        return jsonify({'Error': 'character not found'}), 404
    
    db.session.delete(favorite_filter)
    try:    
        db.session.commit()
        return jsonify({'Details': 'Favorite DELETED'}), 200
    except Exception as error:
        print(error)
        return jsonify({'Error': 'Internal server error'}), 500
        
# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)