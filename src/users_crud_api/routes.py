from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def hello():
    return jsonify("Hello")


@app.route("/api/users", methods=['GET'])
def read_users():
    return jsonify("users")


@app.route("/api/users", methods=['POST'])
def create_user():
    return jsonify("create a user")
