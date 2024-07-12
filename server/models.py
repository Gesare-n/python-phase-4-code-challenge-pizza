from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    restaurant_pizzas = db.relationship('RestaurantPizza', backref='restaurant', cascade='all, delete-orphan')

    def to_dict(self, only=(), rules=()):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "restaurant_pizzas": [rp.to_dict(rules=rules) for rp in self.restaurant_pizzas]
        }

class Pizza(db.Model):
    __tablename__ = 'pizzas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)
    restaurant_pizzas = db.relationship('RestaurantPizza', backref='pizza', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "ingredients": self.ingredients
        }

class RestaurantPizza(db.Model):
    __tablename__ = 'restaurant_pizzas'
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    
    pizza = db.relationship('Pizza', backref='restaurant_pizzas')
    restaurant = db.relationship('Restaurant', backref='restaurant_pizzas')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not (1 <= self.price <= 30):
            raise ValueError("Price must be between 1 and 30")

    def to_dict(self, rules=()):
        return {
            "id": self.id,
            "price": self.price,
            "pizza": self.pizza.to_dict(),
            "pizza_id": self.pizza_id,
            "restaurant_id": self.restaurant_id,
            "restaurant": self.restaurant.to_dict(only=('id', 'name', 'address'))
        }
