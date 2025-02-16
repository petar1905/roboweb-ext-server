import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from gridfs import GridFS

load_dotenv()
app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

fs = GridFS(mongo.db, collection='extensions')

@app.route('/extensions', methods=['POST'])
def create_extension():
    file = request.files['file']
    metadata = {
        'model': request.form['model'],
        'manufacturer': request.form['manufacturer'],
        'author': request.form['author'],
        'version': request.form['version'],
        'license': request.form['license'],
        'repository': request.form['repository']
    }
    file_id = fs.put(file, content_type='application/javascript', metadata=metadata)
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

@app.route('/extensions/<id>', methods=['PUT'])
def update_extension(id):
    file = request.files['file']
    metadata = {
        'model': request.form['model'],
        'manufacturer': request.form['manufacturer'],
        'author': request.form['author'],
        'version': request.form['version'],
        'license': request.form['license'],
        'repository': request.form['repository']
    }

    fs.update(ObjectId(id), file, metadata=metadata)

    return jsonify({'message': 'Extension updated successfully'}), 200

@app.route('/extensions/<id>', methods=['DELETE'])
def delete_extension(id):
    fs.delete(ObjectId(id))
    return jsonify({'message': 'Extension deleted successfully'}), 200

if __name__ == '__main__':
    debug = (os.getenv("DEBUG_MODE", "False").lower() == "true")
    app.run(debug=debug)