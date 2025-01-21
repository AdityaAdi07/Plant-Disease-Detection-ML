from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import json
import os
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
import io
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import logging
import traceback
import sys

# Enhanced logging configuration
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration with error checking
try:
    MONGO_URI = os.environ.get('MONGO_URI', "mongodb+srv://sushmaaditya717:rdqdcaYTLY7p50za@adityaadi.vztbe.mongodb.net/mern_1_db")
    MODEL_PATH = os.environ.get('MODEL_PATH', r'C:\RVCE(2023-27)\venv\Plantdisease-1.h5')
    CLASS_INDICES_PATH = os.environ.get('CLASS_INDICES_PATH', r'C:\RVCE(2023-27)\venv\class_indices (1).json')
    DISEASE_INFO_PATH = os.path.join(os.path.dirname(__file__), 'traits.json')
    
    # Verify file existence
    for path in [MODEL_PATH, CLASS_INDICES_PATH, DISEASE_INFO_PATH]:
        if not os.path.exists(path):
            logger.error(f"Required file not found: {path}")
            raise FileNotFoundError(f"Required file not found: {path}")
            
    logger.info("All required files found")
except Exception as e:
    logger.critical(f"Error during configuration: {str(e)}")
    raise

# Initialize MongoDB with connection testing
try:
    client = MongoClient(MONGO_URI)
    # Test connection
    client.server_info()
    db = client["plant_disease_db"]
    diagnoses_collection = db['diagnoses']
    logger.info("MongoDB connection successful")
except Exception as e:
    logger.critical(f"MongoDB connection failed: {str(e)}")
    raise

# Global variables
model = None
class_indices = None
disease_info = None

def load_disease_info():
    """Load disease information from JSON file with enhanced error handling"""
    try:
        logger.info(f"Attempting to load disease info from: {DISEASE_INFO_PATH}")
        with open(DISEASE_INFO_PATH, 'r') as f:
            info = json.load(f)
            logger.info(f"Successfully loaded disease info: {len(info)} plants found")
            logger.debug(f"Disease info content sample: {list(info.keys())[:3]}")
            return info
    except FileNotFoundError:
        logger.error(f"Disease info file not found at {DISEASE_INFO_PATH}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in disease info file: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading disease info: {str(e)}")
        raise

def get_disease_details(plant_name, disease_name):
    """Get disease details with enhanced logging and error handling"""
    try:
        logger.info(f"Looking up details - Plant: {plant_name}, Disease: {disease_name}")
        
        if disease_info is None:
            logger.error("Disease info not loaded")
            return None
            
        # Clean plant name (remove any special characters)
        plant_name = plant_name.strip()
        logger.debug(f"Cleaned plant name: {plant_name}")
        
        # First try exact match
        plant_data = disease_info.get(plant_name)
        
        # If no exact match, try case-insensitive match
        if not plant_data:
            logger.debug("No exact match found, trying case-insensitive match")
            plant_name_lower = plant_name.lower()
            for key in disease_info.keys():
                if key.lower() == plant_name_lower:
                    plant_data = disease_info[key]
                    break
        
        if not plant_data:
            logger.warning(f"No plant data found for: {plant_name}")
            return None
            
        # Construct full disease name
        full_disease_name = f"{plant_name}___{disease_name}"
        logger.debug(f"Looking for disease with full name: {full_disease_name}")
        
        # Search for disease
        for disease in plant_data.get("diseases", []):
            if disease["name"].lower() == full_disease_name.lower():
                logger.info(f"Found matching disease: {disease}")
                return disease
        
        logger.warning(f"No disease found with name: {full_disease_name}")
        return None
        
    except Exception as e:
        logger.error(f"Error in get_disease_details: {str(e)}")
        return None

def get_alpha(image):
    """Calculate alpha channel with error checking"""
    try:
        alpha = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
        mask = np.all(image > 200, axis=2)
        alpha[mask] = 255
        return alpha
    except Exception as e:
        logger.error(f"Error calculating alpha channel: {str(e)}")
        raise

def calculate_disease_percentage(disease, alpha, threshold=150):
    """Calculate disease percentage with validation"""
    try:
        if disease is None or alpha is None:
            raise ValueError("Invalid input to calculate_disease_percentage")
            
        mask = alpha == 0
        total_pixels = np.sum(mask)
        
        if total_pixels == 0:
            logger.warning("No valid pixels found for disease calculation")
            return 0
            
        diseased_pixels = np.sum((disease < threshold) & mask)
        percentage = round((diseased_pixels / total_pixels * 100), 2)
        logger.debug(f"Disease calculation - Total: {total_pixels}, Diseased: {diseased_pixels}, Percentage: {percentage}%")
        
        return percentage
        
    except Exception as e:
        logger.error(f"Error calculating disease percentage: {str(e)}")
        return 0

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/load_model', methods=['POST'])
def load_saved_model():
    """Load model with enhanced error handling"""
    global model
    try:
        logger.info(f"Loading model from {MODEL_PATH}")
        model = load_model(MODEL_PATH)
        logger.info("Model loaded successfully")
        return jsonify({"message": "Model loaded successfully"}), 200
    except Exception as e:
        error_msg = f"Error loading model: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/load_class_indices', methods=['POST'])
def load_class_indices():
    """Load indices and disease info with enhanced error handling"""
    global class_indices, disease_info
    try:
        logger.info("Loading class indices and disease info")
        
        # Load class indices
        with open(CLASS_INDICES_PATH, 'r') as f:
            class_indices = json.load(f)
            logger.info(f"Loaded {len(class_indices)} class indices")
            
        # Load disease info
        disease_info = load_disease_info()
        
        return jsonify({"message": "Class indices and disease info loaded successfully"}), 200
    except Exception as e:
        error_msg = f"Error loading indices: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/process_image', methods=['POST'])
def process_image():
    """Process image with comprehensive error handling and logging"""
    if model is None or class_indices is None:
        return jsonify({"error": "Model or class indices not loaded"}), 400

    try:
        # Validate input
        file = request.files.get('image')
        if not file:
            return jsonify({"error": "No image file uploaded"}), 400

        logger.info("Processing uploaded image")
        
        # Read and validate image
        img = Image.open(file.stream).convert('RGB')
        img_array = np.array(img)
        
        if img_array.shape[-1] != 3:
            return jsonify({"error": "Invalid image format - must be RGB"}), 400
            
        logger.debug(f"Image shape: {img_array.shape}")

        # Disease analysis
        r, g = img_array[:, :, 0], img_array[:, :, 1]
        disease = r - g
        alpha = get_alpha(img_array)

        # Prepare image for model
        img_resized = cv2.resize(img_array, (224, 224))
        img_preprocessed = img_resized.astype('float32') / 255.0
        img_preprocessed = np.expand_dims(img_preprocessed, axis=0)

        # Get prediction
        logger.info("Running model prediction")
        prediction = model.predict(img_preprocessed)
        predicted_class_index = np.argmax(prediction)
        predicted_class_name = class_indices.get(str(predicted_class_index), "Unknown")
        
        logger.info(f"Predicted class: {predicted_class_name}")

        # Extract plant and disease names
        name_parts = predicted_class_name.split('___')
        plant_name = name_parts[0]
        disease_name = name_parts[1] if len(name_parts) > 1 else 'healthy'
        
        logger.debug(f"Plant name: {plant_name}, Disease name: {disease_name}")

        # Get disease details
        disease_details = get_disease_details(plant_name, disease_name)
        logger.debug(f"Retrieved disease details: {disease_details}")

        # Calculate disease percentage
        percentage_disease = (
            np.random.randint(0, 5)
            if 'healthy' in predicted_class_name.lower()
            else calculate_disease_percentage(disease, alpha)
        )

        # Prepare diagnosis data
        diagnosis_data = {
            "plant_name": predicted_class_name,
            "disease_percentage": percentage_disease,
            "status": "Healthy" if 'healthy' in predicted_class_name.lower() else "Treatment Required",
            "confidence_score": float(prediction[0][predicted_class_index]),
            "timestamp": datetime.utcnow(),
            "disease_details": disease_details
        }

        # Save to database
        result = diagnoses_collection.insert_one(diagnosis_data)
        diagnosis_data['_id'] = str(result.inserted_id)
        
        logger.info(f"Diagnosis completed and saved with ID: {diagnosis_data['_id']}")

        return jsonify({
            "data": diagnosis_data,
            "message": "Diagnosis completed successfully"
        }), 200

    except Exception as e:
        error_msg = f"Error processing image: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/get_comparison/<plant_name>', methods=['GET'])
def get_comparison(plant_name):
    """Get comparison data with error handling"""
    try:
        similar_cases = list(diagnoses_collection.find({
            "plant_name": {"$regex": f".*{plant_name}.*", "$options": "i"}
        }).sort("timestamp", -1).limit(5))

        for case in similar_cases:
            case['_id'] = str(case['_id'])

        logger.info(f"Retrieved {len(similar_cases)} similar cases for {plant_name}")
        return jsonify({
            "similar_cases": similar_cases,
            "message": "Comparison data retrieved successfully"
        }), 200

    except Exception as e:
        error_msg = f"Error getting comparison: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/download_report/<diagnosis_id>', methods=['GET'])
def download_report(diagnosis_id):
    """Generate and download PDF report with error handling"""
    try:
        diagnosis = diagnoses_collection.find_one({"_id": ObjectId(diagnosis_id)})
        
        if not diagnosis:
            logger.warning(f"No diagnosis found with ID: {diagnosis_id}")
            return jsonify({"error": "Diagnosis not found"}), 404

        pdf_buffer = generate_pdf_report(diagnosis)
        logger.info(f"Generated PDF report for diagnosis ID: {diagnosis_id}")
        
        return send_file(
            pdf_buffer,
            download_name=f'plant-diagnosis-{diagnosis_id}.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        error_msg = f"Error generating report: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)