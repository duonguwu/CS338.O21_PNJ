from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import numpy as np
import cv2
from ultralytics import YOLO
import cloudinary.uploader
from collections import Counter
from pymongo import MongoClient
import math
from datetime import datetime

app = Flask(__name__)
app.json.ensure_ascii = False
CORS(app)

cloudinary.config(
    cloud_name='dtldsdxbm',
    api_key="583827442458891",
    api_secret="EucQolFtyzct0gBQhe9lPy6RX_E"
)

uri = 'mongodb+srv://duonga1ne1:duong2003@cluster0.zjdjlqs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

client = MongoClient(uri)
db = client.jewelry_recognition
history_collection = db.history

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history():
    page = int(request.args.get('page', 1))
    per_page = 5
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = {}
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        query = {"timestamp": {"$gte": start_date, "$lt": end_date}}

    total_items = history_collection.count_documents(query)
    total_pages = math.ceil(total_items / per_page)

    history_items = history_collection.find(query).skip((page - 1) * per_page).limit(per_page)
    return render_template('history.html', history_items=history_items, page=page, total_pages=total_pages)


@app.route('/detect', methods=['POST'])
def detect_objects():
    try:
        model = YOLO("best.pt")
        file = request.files['image']
        file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        results = model.predict(img)
        object_counts = []
        for result in results:
            names = result.names
            counts = Counter(result.boxes.cls.tolist())
            for class_id, count in counts.items():
                object_counts.append({
                    "class": names[class_id],
                    "count": count
                })
        im_array = results[0].plot()
        temp_image_path = "temp_image.jpg"
        cv2.imwrite(temp_image_path, im_array)
        cloudinary_response = cloudinary.uploader.upload(temp_image_path)
        
        history_collection.insert_one({
            "image_url": cloudinary_response['secure_url'],
            "object_counts": object_counts,
            "timestamp": datetime()
        })
        
        return jsonify({
            "object_counts": object_counts,
            "image_url": cloudinary_response['secure_url']
        }), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred during processing.'}), 500

if __name__ == "__main__":
    app.run(debug=True)
