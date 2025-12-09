import sqlite3
from flask import Flask, jsonify, request, abort
import models
from datetime import datetime, UTC
from schemas import UserSchema
from pydantic import ValidationError

app = Flask(__name__)


@app.route("/api/users", methods=['GET'])
def read_users():
    users_db = models.init_users_db()
    cur = users_db.cursor()
    cur.execute("SELECT * FROM Users")

    users = [{'id': user[0], 'name': user[1], 'email': user[2], 'created_at': user[3]}
             for user in cur.fetchall()]

    return jsonify(users), 200


@app.route("/api/users/<user_id>", methods=['GET'])
def read_user(user_id):
    if not user_id.isdigit():
        abort(400, description="User ID should be int")

    users_db = models.init_users_db()
    cur = users_db.cursor()

    sql = "SELECT * FROM Users WHERE id = ?"
    cur.execute(sql, (user_id, ))

    user = cur.fetchone()
    if not user:
        abort(404, description="This user does not exists")
    return jsonify({
        'id': user[0],
        'name': user[1],
        'email': user[2],
        'created_at': user[3]
    }), 200


@app.route("/api/users", methods=['POST'])
def create_user():
    new_user = request.json

    if not new_user or 'name' not in new_user:
        abort(400, description="You should write a name")

    if 'email' not in new_user:
        new_user['email'] = f"{new_user['name']}@email.com"

    try:
        validate_user = UserSchema(name=new_user['name'], email=new_user['email'])
        print(f"Success validation! Name: {validate_user.name}, email: {validate_user.email}")
    except ValidationError:
        abort(400, description="Validation error!")

    created_at = datetime.now(UTC).isoformat()
    new_user['created_at'] = created_at

    users_db = models.init_users_db()
    cur = users_db.cursor()

    try:
        sql = "INSERT INTO Users (name, email, created_at) VALUES (?, ?, ?)"
        cur.execute(sql, (new_user['name'], new_user['email'], new_user['created_at']))
        users_db.commit()

        return jsonify({
            'name': new_user['name'],
            'email': new_user['email'],
            'created_at': new_user['created_at']
        }), 201
    except sqlite3.IntegrityError:
        abort(409, description="Email should be unique")


@app.route("/api/users/<user_id>", methods=['DELETE'])
def delete_user(user_id):
    if not user_id.isdigit():
        abort(400, description="User ID should be int")

    users_db = models.init_users_db()
    cur = users_db.cursor()

    sql = "SELECT * FROM Users WHERE id = ?"
    cur.execute(sql, (user_id, ))

    user = cur.fetchone()
    if not user:
        abort(404, description="This user does not exists")

    sql = "DELETE FROM Users WHERE id = ?"
    cur.execute(sql, (user_id, ))
    users_db.commit()

    return jsonify({'message': 'User deleted successfully'}), 200


@app.route("/api/users/<user_id>", methods=['PATCH'])
def update_user(user_id):
    if not user_id.isdigit():
        abort(400, description="User ID should be int")

    updated_data = request.json
    if not updated_data:
        abort(400, description="No data to update")

    users_db = models.init_users_db()
    cur = users_db.cursor()

    sql = "SELECT * FROM Users WHERE id = ?"
    cur.execute(sql, (user_id, ))
    user = cur.fetchone()

    if not user:
        abort(404, description="This user does not exists")

    new_name = updated_data.get('name', user[1])
    new_email = updated_data.get('email', user[2])

    try:
        validate_user = UserSchema(name=new_name, email=new_email)
        print(f"Success validation! Name: {validate_user.name}, name: {validate_user.email}")
    except ValidationError:
        abort(400, description="Validation error!")

    try:
        sql = "UPDATE Users SET name = ?, email = ? WHERE id = ?"
        cur.execute(sql, (new_name, new_email, user_id))
        users_db.commit()

        sql = "SELECT * FROM Users WHERE id = ?"
        cur.execute(sql, (user_id, ))
        user = cur.fetchone()

        return jsonify({
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'created_at': user[3]
        }), 200
    except sqlite3.IntegrityError:
        abort(409, description="Email should be unique")
