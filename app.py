from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Float
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# init Database
db = SQLAlchemy(app)
ma = Marshmallow(app)


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
@app.route('/planets')
def planets():
    planet_list = Planet.query.all()
    results = planets_schema.dump(planet_list)
    return jsonify(results)


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
