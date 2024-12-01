from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(80), unique = False, nullable = False)
    is_active = db.Column(db.Boolean(), unique = False, nullable = False)
    favorites = db.relationship("Favorites")
    
    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
        }
        
class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    planets_id = db.Column(db.Integer, db.ForeignKey("planets.id"), nullable = True)
    characters_id = db.Column(db.Integer, db.ForeignKey("characters.id"), nullable = True)
    
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'planets_id': self.planets_id,
            'characters-id': self.characters_id
        }
    
class Characters(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    image_src = db.Column(db.String(500), nullable = False)
    description = db.Column(db.String(500), nullable = False)
    favorites = db.relationship("Favorites")
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'image_src': self.image_src,
            'description': self.description
        }

class Planets(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    image_src = db.Column(db.String(500), nullable = False)
    description = db.Column(db.String(500), nullable = False)
    favorites = db.relationship("Favorites")
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'image_src': self.image_src,
            'desciption': self.description
        }