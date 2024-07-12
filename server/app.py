from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Models definitions using SQLAlchemy
class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)
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
    name = db.Column(db.String)
    ingredients = db.Column(db.String)
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
    price = db.Column(db.Integer)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))

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

# Routes and API endpoints
@app.route("/")
def index():
    return "<h1>Welcome to the Pizza Restaurant API</h1>"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants])

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant is None:
        return jsonify({"error": "Restaurant not found"}), 404
    return jsonify(restaurant.to_dict(rules=('-restaurant_pizzas.restaurant',)))

@app.route('/restaurants', methods=['POST'])
def create_restaurant():
    data = request.get_json()
    try:
        new_restaurant = Restaurant(
            name=data['name'],
            address=data['address']
        )
        db.session.add(new_restaurant)
        db.session.commit()
        return jsonify(new_restaurant.to_dict()), 201
    except KeyError as e:
        return jsonify({"error": f"Missing required parameter: {e}"}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Restaurant name must be unique"}), 400

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant is None:
        return jsonify({"error": "Restaurant not found"}), 404
    db.session.delete(restaurant)
    db.session.commit()
    return '', 204

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas])

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        rp = RestaurantPizza(
            price=data['price'],
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )
        db.session.add(rp)
        db.session.commit()
        return jsonify(rp.to_dict(rules=('-pizza.restaurant_pizzas', '-restaurant.restaurant_pizzas'))), 201
    except KeyError as e:
        return jsonify({"error": f"Missing required parameter: {e}"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(port=5555, debug=True)
