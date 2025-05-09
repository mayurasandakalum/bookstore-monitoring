from flask import Flask, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics
from pymongo import MongoClient
from bson.objectid import ObjectId
import json

app = Flask(__name__)
# Initialize with default metrics and export HTTP request metrics
metrics = PrometheusMetrics(app)

# Track all endpoints with default metric name 'flask_http_requests_total'
metrics.info("app_info", "Bookstore API", version="1.0.0")

# MongoDB Cloud connection string
mongo_uri = "mongodb+srv://vaued2025a2g09:oaTsa6H61PZlE3cb@cluster0.l50ynzo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)
db = client.bookstore
books_collection = db.books


# Custom JSON encoder to handle MongoDB ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


@app.route("/books", methods=["GET"])
def get_books():
    books = list(books_collection.find())
    return JSONEncoder().encode(books), 200, {"Content-Type": "application/json"}


@app.route("/books/<book_id>", methods=["GET"])
def get_book(book_id):
    try:
        book = books_collection.find_one({"_id": ObjectId(book_id)})
        if book:
            return JSONEncoder().encode(book), 200, {"Content-Type": "application/json"}
        return jsonify({"error": "Book not found"}), 404
    except Exception:
        return jsonify({"error": "Invalid book ID format"}), 400


@app.route("/books", methods=["POST"])
def add_book():
    data = request.get_json()
    result = books_collection.insert_one(data)
    data["_id"] = str(result.inserted_id)
    return jsonify({"message": "Book added", "book": data}), 201


@app.route("/books/<book_id>", methods=["PUT"])
def update_book(book_id):
    try:
        data = request.get_json()
        result = books_collection.update_one({"_id": ObjectId(book_id)}, {"$set": data})
        if result.modified_count > 0:
            updated_book = books_collection.find_one({"_id": ObjectId(book_id)})
            return (
                JSONEncoder().encode({"message": "Book updated", "book": updated_book}),
                200,
                {"Content-Type": "application/json"},
            )
        return jsonify({"error": "Book not found"}), 404
    except Exception:
        return jsonify({"error": "Invalid book ID format"}), 400


@app.route("/books/<book_id>", methods=["DELETE"])
def delete_book(book_id):
    try:
        result = books_collection.delete_one({"_id": ObjectId(book_id)})
        if result.deleted_count > 0:
            return jsonify({"message": "Book deleted"}), 200
        return jsonify({"error": "Book not found"}), 404
    except Exception:
        return jsonify({"error": "Invalid book ID format"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
