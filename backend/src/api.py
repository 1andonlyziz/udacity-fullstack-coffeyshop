import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


db_drop_and_create_all()


# ------------ Endpoints

@app.route('/drinks', methods=['GET'])
def get_all_drinks():
    drinks = Drink.query.all()
    return jsonify({
        'success': True,
        'drinks': [d.short() for d in drinks]
    }), 200


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(payload):
    drinks = Drink.query.all()
    return jsonify({
        'success': True,
        'drinks': [d.long() for d in drinks]
    }), 200


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):

    # get raw data
    body = request.get_json()

    title = body['title']
    recipe = body['recipe']

    drink = Drink(title=title, recipe=recipe)
    drink.insert()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def something(payload, id):

    drink = Drink.query.filter_by(id=id).one_or_none()

    if drink is None:
        abort(404)

    body = request.get_json()

    try:
        body_title = body['title']
        body_recipe = body['recipe']

        if body_title:
            drink.title = body_title

        if body_recipe:

            drink.recipe = json.dumps(body_recipe)

        drink.update()

    except Exception:
        abort(400)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200


@app.route('/drinks/<int:id>')
@requires_auth('delete:drinks')
def delete_drinks(payload, id):

    drink = Drink.query.filter_by(id=id).one_or_none()

    if drink is None:
        abort(404)

    drink.delete()

    return jsonify({
        'success': True,
        'delete': id
    }), 200


'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'unauthorized'

    }), 401


@app.errorhandler(AuthError)
def process_auth_error(error):
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response
