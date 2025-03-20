import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from gridfs import GridFS
from bson import ObjectId
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

fs = GridFS(mongo.db, collection='extensions')
cors = CORS(app, resources={r"/*": {"origins": os.getenv("ALLOWED_ORIGINS"), "methods": ["GET", "POST", "PUT", "DELETE"]}})


@app.route('/extensions', methods=['POST'])
def create_extension():
    file = request.files['file']
    metadata = {
        'model': request.form['model'],
        'manufacturer': request.form['manufacturer'],
        'author': request.form['author'],
        'version': request.form['version'],
        'license': request.form['license'],
        'repository': request.form['repository'],
        'settings': request.form.get('settings', '{}')
    }
    if not metadata['settings'].startswith('{'):
        return jsonify({'error': 'Settings must be a JSON object'}), 400
    filename = f"{metadata['model'].lower()}-{metadata['manufacturer'].lower()}-{metadata['version']}.html"
    file_id = fs.put(file, content_type='text/html', filename=filename, metadata=metadata)
    return jsonify({'_id': str(file_id)}), 201

@app.route('/extensions/<id>', methods=['GET'])
def get_extension(id):
    file = fs.get(ObjectId(id))
    if file:
        return jsonify({
            '_id': str(file._id),
            'filename': file.filename,
            'content_type': file.content_type,
            'metadata': file.metadata,
            'file': file.read().decode('utf-8')
        })
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/extensions', methods=['GET'])
def get_all_extensions():
    files = fs.find()
    output = []
    for file in files:
        output.append({
            '_id': str(file._id),
            'filename': file.filename,
            'content_type': file.content_type,
            'metadata': file.metadata,
            'file': file.read().decode('utf-8')
        })
    return jsonify({'extensions': output})

@app.route('/extensions/<id>', methods=['PUT'])
def update_extension(id):
    fs.delete(ObjectId(id))
    file = request.files['file']
    metadata = {
        'model': request.form['model'],
        'manufacturer': request.form['manufacturer'],
        'author': request.form['author'],
        'version': request.form['version'],
        'license': request.form['license'],
        'repository': request.form['repository'],
        'settings': request.form.get('settings', '{}')
    }
    if not metadata['settings'].startswith('{'):
        return jsonify({'error': 'Settings must be a JSON object'}), 400
    filename = f"{metadata['model'].lower()}-{metadata['manufacturer'].lower()}-{metadata['version']}.js"
    filename = filename.replace(" ", "-")
    file_id = fs.put(file, content_type='text/html', filename=filename, metadata=metadata)
    return jsonify({'_id': str(file_id)}), 200

@app.route('/extensions/<id>', methods=['DELETE'])
def delete_extension(id):
    fs.delete(ObjectId(id))
    return jsonify({'message': 'Extension deleted successfully'}), 200

if __name__ == '__main__':
    debug = (os.getenv("DEBUG_MODE", "False").lower() == "true")
    app.run(debug=debug, host='0.0.0.0')