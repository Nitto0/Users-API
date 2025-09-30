from flask import Flask, jsonify, request
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

    return jsonify(users)


@app.route("/api/users", methods=['POST'])
def create_user():
    new_user = request.json
    created_at = datetime.now(UTC).isoformat()
    new_user['created_at'] = created_at

    users_db = models.init_users_db()
    cur = users_db.cursor()

    cur.execute("INSERT INTO Users (name, email, created_at) VALUES (?, ?, ?)",
                (new_user['name'], new_user['email'], new_user['created_at']))
    users_db.commit()

    return jsonify({
        'name': new_user['name'],
        'email': new_user['email'],
        'created_at': new_user['created_at']
    })
