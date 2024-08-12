from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user


app = Flask(__name__)
app.config['SECRET_KEY'] = "super_secret_stuff_123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskecommerce.db'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/api/auth/login'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/api/auth/login', methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get("username")).first()
    if user and data.get("password") == user.password:
            login_user(user)
            return jsonify({"message": "Logged in successfully."}), 200
    return jsonify({"message": "Unauthorized. Invalid credentials."}), 401

@app.route('/api/auth/logout', methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successfully"}), 201


@app.route('/api/products', methods=["POST"])
@login_required
def add_product():
    data = request.json
    if 'name' in data and 'price' in data:
        product = Product(
            name=data.get('name'), 
            description=data.get('description', ""),
            price=data.get('price')
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({"message":"Product added successfully."}), 201
    return jsonify({"message":"Validation error."}), 400

@app.route('/api/products/<int:product_id>', methods=["PATCH"])
@login_required
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found."}), 404
    
    data = request.json
    if 'name' in data:
        product.name = data['name']
    
    if 'price' in data:
        product.price = data['price']

    if 'description' in data:
        product.description = data['description']

    db.session.commit()
    return jsonify({"message": "Product updated successfully."})

@app.route('/api/products/<int:product_id>', methods=["DELETE"])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully."})
    return jsonify({"message": "Product not found."}), 404

@app.route('/api/products', methods=["GET"])
@login_required
def get_products():
    products = Product.query.all()
    data = []
    for product in products:
        data.append({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description
        })
    return jsonify(data), 200

@app.route('/api/products/<int:product_id>', methods=["GET"])
@login_required
def get_product_details(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description
        })
    return jsonify({"message": "Product not found"}), 404


@app.route('/')
def hello_world():
    return "Hello world!"

if __name__ == "__main__":
    app.run(debug=True)
