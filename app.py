from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import json
from PIL import Image
import os
from datetime import datetime, timezone
from pymongo import MongoClient
from bson import ObjectId
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import logging
import traceback
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('app.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
MONGO_URI = "mongodb+srv://sushmaaditya717:rdqdcaYTLY7p50za@adityaadi.vztbe.mongodb.net/mern_1_db"
MODEL_PATH = r'C:\RVCE(2023-27)\venv\Plantdisease-1.h5'
CLASS_INDICES_PATH = r'C:\RVCE(2023-27)\venv\class_indices (1).json'
DISEASE_INFO_PATH = os.path.join(os.path.dirname(__file__), 'traits.json')

# Initialize MongoDB
client = MongoClient(MONGO_URI)
db = client["mern_1_db"]
diagnoses_collection = db['notess']

# Global variables
model = None
class_indices = None
disease_info = None

# Load disease information
def load_disease_info():
    try:
        with open(DISEASE_INFO_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading disease info: {str(e)}")
        return {}

def get_disease_details(plant_name, disease_name):
    """
    Get disease details from the JSON file based on plant name and disease
    """
    try:
        if disease_info is None:
            return None
            
        # Extract plant name and normalize
        plant_name = plant_name.lower().split('_')[0]  # Get first part before underscore
        
        # Search for plant in case-insensitive manner
        plant_data = None
        for plant_key in disease_info:
            if plant_key.lower() == plant_name:
                plant_data = disease_info[plant_key]
                break
        
        if not plant_data:
            return None
            
        # Search for disease in case-insensitive manner
        disease_name = disease_name.lower().replace(" ", "_")
        for disease in plant_data["diseases"]:
            if disease["name"].lower() == disease_name:
                return disease
                
        return None
    except Exception as e:
        logger.error(f"Error getting disease details: {str(e)}")
        return None

# Your existing helper functions
def get_alpha(image):
    alpha = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
    mask = np.all(image > 200, axis=2)
    alpha[mask] = 255
    return alpha

def calculate_disease_percentage(disease, alpha, threshold=150):
    mask = alpha == 0
    total_pixels = np.sum(mask)
    diseased_pixels = np.sum((disease < threshold) & mask)
    return round((diseased_pixels / total_pixels * 100) if total_pixels > 0 else 0, 2)

# Routes
@app.route('/')
def serve_html():
    return render_template('index.html')

@app.route('/load_model', methods=['POST'])
def load_saved_model():
    global model
    try:
        model = load_model(MODEL_PATH)
        return jsonify({"message": "Model loaded successfully"}), 200
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/load_class_indices', methods=['POST'])
def load_class_indices():
    global class_indices, disease_info
    try:
        # Load class indices
        with open(CLASS_INDICES_PATH, 'r') as f:
            class_indices = json.load(f)
        
        # Load disease information
        disease_info = load_disease_info()
        
        return jsonify({"message": "Class indices and disease info loaded successfully"}), 200
    except Exception as e:
        logger.error(f"Error loading indices: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/process_image', methods=['POST'])
def process_image():
    if model is None or class_indices is None:
        return jsonify({"error": "Model or class indices not loaded"}), 400

    try:
        file = request.files.get('image')
        if not file:
            return jsonify({"error": "No image file uploaded"}), 400

        # Open and preprocess the image
        img = Image.open(file.stream).convert('RGB')
        img_array = np.array(img)
        logger.info(f"Original image shape: {img_array.shape}")

        if img_array.shape[-1] != 3:
            return jsonify({"error": "Invalid image format"}), 400

        # Disease analysis
        r, g = img_array[:, :, 0], img_array[:, :, 1]
        disease = r - g
        alpha = get_alpha(img_array)

        # Resize and preprocess for model input
        img_resized = cv2.resize(img_array, (224, 224))
        img_preprocessed = img_resized.astype('float32') / 255.0
        img_preprocessed = np.expand_dims(img_preprocessed, axis=0)

        # Model prediction
        prediction = model.predict(img_preprocessed)
        logger.info(f"Prediction: {prediction}")

        # Get predicted class
        predicted_class_index = np.argmax(prediction)
        predicted_class_name = class_indices.get(str(predicted_class_index), "Unknown")
        logger.info(f"Predicted class index: {predicted_class_index}, Name: {predicted_class_name}")
        print(f"Predicted class name: {predicted_class_name}")

        # Extract plant name and disease name
        name_parts = predicted_class_name.split('_')
        plant_name = name_parts[0]
        disease_name = '_'.join(name_parts[1:]) if len(name_parts) > 1 else 'healthy'
        print(f"Plant name: {plant_name}, Disease name: {disease_name}")


        # Get disease details
        disease_details = get_disease_details(plant_name, disease_name)
        print(f"Retrieved disease details: {disease_details}")

        # Calculate disease percentage
        if 'healthy' in predicted_class_name.lower():
            percentage_disease = np.random.randint(0, 5)
        else:
            percentage_disease = calculate_disease_percentage(disease, alpha)

        # Construct response data
        diagnosis_data = {
            "plant_name": predicted_class_name,
            "disease_percentage": percentage_disease,
            "status": "Healthy" if 'healthy' in predicted_class_name.lower() else "Treatment Required",
            "confidence_score": float(prediction[0][predicted_class_index]),
            "timestamp": datetime.utcnow(),
            "disease_details": disease_details
        }
        logger.info(f"Diagnosis data: {diagnosis_data}")
        print(f"Final diagnosis data: {diagnosis_data}") 

        # Insert into MongoDB
        result = diagnoses_collection.insert_one(diagnosis_data)
        diagnosis_data['_id'] = str(result.inserted_id)

        return jsonify({
            "data": diagnosis_data,
            "message": "Diagnosis completed successfully"
        }), 200

    except Exception as e:
        logger.error(f"Error processing image: {traceback.format_exc()}")
        return jsonify({"error": f"Error processing the image: {str(e)}"}), 500

# Your existing comparison and report endpoints remain the same
@app.route('/get_comparison/<plant_name>', methods=['GET'])
def get_comparison(plant_name):
    try:
        similar_cases = list(diagnoses_collection.find({
            "plant_name": {"$regex": f".*{plant_name}.*", "$options": "i"}
        }).sort("timestamp", -1).limit(5))

        for case in similar_cases:
            case['_id'] = str(case['_id'])

        return jsonify({
            "similar_cases": similar_cases,
            "message": "Comparison data retrieved successfully"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/run_python', methods=['POST'])
def run_python():
    try:
        # Use the virtual environment's Python executable
        venv_python = r'C:\RVCE(2023-27)\venv\Scripts\python.exe'
        script_path = r'C:\RVCE(2023-27)\venv\recorder.py'
        
        # Run the script
        result = subprocess.run([venv_python, script_path], capture_output=True, text=True)
        
        if result.returncode == 0:
            return jsonify({"success": True, "message": result.stdout.strip()})
        else:
            error_message = result.stderr.strip() or "Unknown error occurred"
            return jsonify({"success": False, "error": error_message})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    




@app.route('/download_report/<diagnosis_id>', methods=['GET'])
def download_report(diagnosis_id):
    try:
        diagnosis = diagnoses_collection.find_one({"_id": ObjectId(diagnosis_id)})
        
        if not diagnosis:
            return jsonify({"error": "Diagnosis not found"}), 404

        pdf_buffer = generate_pdf_report(diagnosis)
        return send_file(
            pdf_buffer,
            download_name=f'plant-diagnosis-{diagnosis_id}.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':   
    app.run(debug=True, port=8080)