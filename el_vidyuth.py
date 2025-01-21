from flask import Flask, request, jsonify, send_from_directory
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import json
from PIL import Image
import os
from random import randint
from datetime import datetime

app = Flask(__name__)

# Global variables
model = None
class_indices = None
Alpha = None

# Serve the HTML file
@app.route('/')
def serve_html():
    return send_from_directory('', 'el_vidyuth.html')

# Load the saved model
@app.route('/load_model', methods=['POST'])
def load_saved_model():
    global model
    try:
        model_path = r'C:\RVCE(2023-27)\venv\Plantdisease-1.h5'
        model = load_model(model_path)
        return jsonify({"message": "Model loaded successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Load class indices
@app.route('/load_class_indices', methods=['POST'])
def load_class_indices():
    global class_indices
    try:
        class_indices_path = r'C:\RVCE(2023-27)\venv\class_indices (1).json'
        with open(class_indices_path, 'r') as f:
            class_indices = json.load(f)
        return jsonify({"message": "Class indices loaded successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Define a function to calculate the Alpha channel
def get_alpha(image):
    alpha = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            if image[i, j, 0] > 200 and image[i, j, 1] > 200 and image[i, j, 2] > 200:
                alpha[i, j] = 255
            else:
                alpha[i, j] = 0
    return alpha

# Calculate disease percentage
def display_disease_percentage(disease, alpha, threshold):
    count = 0
    res = 0
    for i in range(disease.shape[0]):
        for j in range(disease.shape[1]):
            if alpha[i, j] == 0:
                res += 1
            if disease[i, j] < threshold:
                count += 1
    percent = (count / res) * 100 if res != 0 else 0
    return round(percent, 2)

@app.route('/process_image', methods=['POST'])
def process_image():
    global model, class_indices, Alpha
    if model is None:
        return jsonify({"error": "Model not loaded. Please load the model first."}), 400

    if class_indices is None:
        return jsonify({"error": "Class indices not loaded. Please load the class indices first."}), 400

    try:
        # Get the file from the request
        file = request.files['image']
        
        # Define the uploads directory
        uploads_dir = 'uploads'
        
        # Create the uploads directory if it does not exist
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        
        # Save the file to the uploads directory
        file_path = os.path.join(uploads_dir, file.filename)
        file.save(file_path)
        
        img = Image.open(file)
        img = img.convert('RGB')
        img = np.array(img)

        # Extract channels
        b = img[:, :, 0]
        g = img[:, :, 1]
        r = img[:, :, 2]
        Disease = r - g

        # Calculate Alpha channel
        Alpha = get_alpha(img)

        # Resize and preprocess image for model
        img_resized = cv2.resize(img, (224, 224))  # Resize as per model's input shape
        img_preprocessed = img_resized.astype('float32') / 255.0
        img_preprocessed = np.expand_dims(img_preprocessed, axis=0)

        # Make a prediction
        prediction = model.predict(img_preprocessed)
        predicted_class_index = np.argmax(prediction)
        predicted_class_name = class_indices[str(predicted_class_index)]

        # Determine disease percentage and status
        if 'healthy' in predicted_class_name.lower():
            percentage_disease = randint(0, 5)
            message = "The plant is healthy."
        else:
            message = "The plant needs to be treated."
            threshold = 150
            percentage_disease = display_disease_percentage(Disease, Alpha, threshold)

        # Save diagnosis data as JSON
        diagnosis_data = {
            "plant_name": predicted_class_name,
            "plant_disease_percentage": f"{percentage_disease}%",
            "diagnosis": message,
            "path_name": file_path
        }

        # Save JSON file with diagnosis data
        report_dir = 'diagnosis_reports'
        os.makedirs(report_dir, exist_ok=True)
        json_filename = f"diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        json_path = os.path.join(report_dir, json_filename)
        with open(json_path, 'w') as json_file:
            json.dump(diagnosis_data, json_file, indent=4)

        # Return response including the JSON file path
        return jsonify({
            "data": diagnosis_data,
            "json_file_path": json_path
        }), 200

    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
@app.route('/diagnosis_reports/<filename>')
def serve_json(filename):
    return send_from_directory('diagnosis_reports', filename)

if __name__ == '__main__':
    app.run(debug=True)
