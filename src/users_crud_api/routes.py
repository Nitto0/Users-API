import sqlite3
from flask import Flask, jsonify, request, abort
import models
from datetime import datetime, UTC

app = Flask(__name__)


@app.route("/api/users", methods=['GET'])
def read_users():
    users_db = models.init_users_db()
    cur = users_db.cursor()
    cur.execute("SELECT * FROM Users")

    users = [{'id': user[0], 'name': user[1], 'email': user[2], 'created_at': user[3]}
             for user in cur.fetchall()]

    return jsonify(users), 200


@app.route("/api/users/<int:user_id>", methods=['GET'])
def read_user(user_id):
    # Валидация здесь

    users_db = models.init_users_db()
    cur = users_db.cursor()
    cur.execute("SELECT * FROM Users WHERE id = ?", (user_id, ))

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

    # Валидация здесь

    created_at = datetime.now(UTC).isoformat()
    new_user['created_at'] = created_at

    users_db = models.init_users_db()
    cur = users_db.cursor()

    try:
        cur.execute('INSERT INTO Users (name, email, created_at) VALUES (?, ?, ?)',
                    (new_user['name'], new_user['email'], new_user['created_at']))
        users_db.commit()

        return jsonify({
            'name': new_user['name'],
            'email': new_user['email'],
            'created_at': new_user['created_at']
        }), 201
    except sqlite3.IntegrityError:
        abort(409, description="Email should be unique")


@app.route("/api/users/<int:user_id>", methods=['DELETE'])
def delete_user(user_id):
    # Валидация здесь

    users_db = models.init_users_db()
    cur = users_db.cursor()
    cur.execute("SELECT * FROM Users WHERE id = ?", (user_id, ))

    user = cur.fetchone()
    if not user:
        abort(404, description="This user does not exists")

    cur.execute("DELETE FROM Users WHERE id = ?", (user_id, ))
    users_db.commit()

    return jsonify({'message': 'User deleted successfully'}), 200


@app.route("/api/users/<int:user_id>", methods=['PATCH'])
def update_user(user_id):
    # Валидация здесь (user_id)

    updated_data = request.json
    if not updated_data:
        abort(400, description="No data to update")

    users_db = models.init_users_db()
    cur = users_db.cursor()

    cur.execute("SELECT * FROM Users WHERE id = ?", (user_id, ))
    user = cur.fetchone()

    if not user:
        abort(404, description="This user does not exists")

    new_name = updated_data.get('name', user[1])
    new_email = updated_data.get('email', user[2])

    # Валидация name и email

    try:
        cur.execute("UPDATE Users SET name = ?, email = ? WHERE id = ?",
                    (new_name, new_email, user_id))
        users_db.commit()

        cur.execute("SELECT * FROM Users WHERE id = ?", (user_id, ))
        user = cur.fetchone()

        return jsonify({
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'created_at': user[3]
        }), 200
    except sqlite3.IntegrityError:
        abort(409, description="Email should be unique")
