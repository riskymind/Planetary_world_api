from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Float
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Mail, Message
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')
app.config['JWT_SECRET_KEY'] = 'super-secret'  # change in real application to UUID
app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

# init Database
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
mail = Mail(app)


@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database Created!')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database Dropped!')


@app.cli.command('db_seed')
def db_seed():
    mercury = Planet(
        planet_name='Mercury',
        planet_type='Class D',
        home_star='Sol',
        mass=3.258e23,
        radius=1516,
        distance=35.98e6
    )

    venus = Planet(
        planet_name='Venus',
        planet_type='Class K',
        home_star='Sol',
        mass=4.867e24,
        radius=3760,
        distance=67.24e6
    )
    earth = Planet(
        planet_name='Earth',
        planet_type='Class M',
        home_star='Sol',
        mass=5.972e24,
        radius=3959,
        distance=92.96e6
    )

    db.session.add(mercury)
    db.session.add(venus)
    db.session.add(earth)

    test_user = User(
        first_name='Zuri',
        last_name='Opara',
        email='test@gmail.com',
        password='p@ssword'
    )

    db.session.add(test_user)
    db.session.commit()
    print('Database seeded!')


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/super_simple')
def super_super():
    return jsonify(message='Hello from planetary Api.')


@app.route('/not_found')
def not_found():
    return jsonify(message='no resources found'), 404


@app.route('/parameters')
def parameters():
    name = request.args.get('name')
    age = int(request.args.get('age'))
    if age < 18:
        return jsonify(message='not qualified'), 401
    else:
        return jsonify(message='welcome to planetary')


@app.route('/url_variables/<string:name>/<int:age>')
def path_call(name: str, age: int):
    if age < 18:
        return jsonify(message='not qualified'), 401
    else:
        return jsonify(message='welcome to planetary' + name), 200


# get all planets
@app.route('/planets', methods=['GET'])
def planets():
    planet_list = Planet.query.all()
    results = planets_schema.dump(planet_list)
    return jsonify(results)


# Register Users
@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    mailExist = User.query.filter_by(email=email).first()
    if mailExist:
        return jsonify(message='This mail already exists.'), 409
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        user = User(first_name=first_name, last_name=last_name, password=password, email=email)
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User register successfully."), 201


# Login
@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']
    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message='Login Succeed!!', token=access_token), 200
    else:
        return jsonify(message='Wrong email or password'), 401


# Retrieve password
@app.route('/retrieve_password/<string:email>', methods=['GET'])
def retrieve_password(email: str):
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message("Your planetary password is " + user.password, sender='admin@planetary.com', recipients=[email])
        mail.send(msg)
        return jsonify(message='Password sent to ' + user.email)
    else:
        return jsonify(message='This mail ' + email + ' doesn\'t exists'), 401


# Get a single planet
@app.route('/planet_details/<int:id>', methods=['GET'])
def planet_details(id: int):
    planet = Planet.query.filter_by(planet_id=id).first()
    if planet:
        result = planet_schema.dump(planet)
        return jsonify(data=result)
    else:
        return jsonify(message='planet does not exists'), 404


# Add Planet to DB
@app.route('/add_planet', methods=['POST'])
@jwt_required()
def add_planet():
    planet_name = request.form['planet_name']
    test = Planet.query.filter_by(planet_name=planet_name).first()
    if test:
        return jsonify(message='Planet already exists!.'), 409
    else:
        planet_type = request.form['planet_type']
        home_star = request.form['home_star']
        mass = float(request.form['mass'])
        radius = float(request.form['radius'])
        distance = float(request.form['distance'])

        new_planet = Planet(
            planet_name=planet_name,
            planet_type=planet_type,
            home_star=home_star,
            mass=mass,
            radius=radius,
            distance=distance
        )

        db.session.add(new_planet)
        db.session.commit()
        return jsonify(message='Planet ' + planet_name + ' added successfully.')


# Update planet
@app.route('/update_planet', methods=['PUT'])
@jwt_required()
def update_planet():
    planet_id = request.form['planet_id']
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        planet.planet_name = request.form['planet_name']
        planet.planet_type = request.form['planet_type']
        planet.home_star = request.form['home_star']
        planet.mass = float(request.form['mass'])
        planet.radius = float(request.form['radius'])
        planet.distance = float(request.form['distance'])
        db.session.commit()
        return jsonify(message='planet updated successfully'), 202
    else:
        return jsonify(message='The planet does not exists'), 404


# Remove planet
@app.route('/remove_planet/<int:planet_id>', methods=['DELETE'])
@jwt_required()
def remove_planet(planet_id: int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        db.session.delete(planet)
        db.session.commit()
        return jsonify(message=planet.planet_name + ' deleted successfully.'), 202
    else:
        return jsonify(message='No such planet'), 404


# Database Model
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)


class Planet(db.Model):
    __tablename__ = 'planets'
    planet_id = Column(Integer, primary_key=True)
    planet_name = Column(String)
    planet_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password')


class PlanetSchema(ma.Schema):
    class Meta:
        fields = ('planet_id', 'planet_name', 'planet_type', 'home_star', 'mass', 'radius', 'distance')


user_schema = UserSchema()
users_schema = UserSchema(many=True)

planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)

if __name__ == '__main__':
    app.run()
