# Krishaka Kavacham🌱 - Plant Disease Detection

Display-Website Link: https://krishaka-kavacham.netlify.app/

Krishaka Kavacham is an advanced web application that uses artificial intelligence to detect and diagnose plant diseases from leaf images. The system provides treatment recommendations and tracks disease history.



## Features

- **AI-Powered Disease Detection**: Upload a photo of your plant leaf and get instant diagnosis
- **Detailed Analysis**: View disease percentage, confidence score, and diagnosis details
- **Treatment Recommendations**: Get specific treatment advice for identified diseases
- **PDF Reports**: Generate and download detailed diagnosis reports
- **Historical Comparison**: Compare current diagnosis with previous cases
- **Responsive Design**: Works on desktop and mobile devices

## Gallery
![Screenshot 2025-01-19 231818](https://github.com/user-attachments/assets/34f9db94-0dbb-484e-852d-79c8d910cd1f)
---
![Screenshot 2025-01-19 231844](https://github.com/user-attachments/assets/29f87cc4-2af0-431f-b766-183f192f7507)
---
![Screenshot 2025-01-19 231615](https://github.com/user-attachments/assets/73367889-e778-44f1-a73b-e51a80b5e466)
---
![Screenshot 2025-01-19 231706](https://github.com/user-attachments/assets/58ecdf89-2c34-4633-a119-9b305451d02a)
---
![Screenshot 2025-01-19 231734](https://github.com/user-attachments/assets/61beb3ec-61a4-4c99-b500-a1107031599e)
---
![Screenshot 2025-01-21 121307](https://github.com/user-attachments/assets/db925072-211b-4b23-bfb5-b455c891c4a8)
---
![Screenshot 2025-01-21 121429](https://github.com/user-attachments/assets/cd4a7acb-8b39-4805-b657-c4200b0bc752)
---
![Screenshot 2025-01-19 232252](https://github.com/user-attachments/assets/3bedfebb-e718-4bb0-9452-9c58373aa11f)
---
![Screenshot 2025-01-19 232005](https://github.com/user-attachments/assets/b22dea0f-0c31-40a9-a65d-5b312ffc59c5)
---
![Screenshot 2025-01-19 231928](https://github.com/user-attachments/assets/1efca746-0132-42ca-90dd-d509983a6a6a)


## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS (Tailwind CSS), JavaScript
- **Machine Learning**: TensorFlow/Keras
- **Database**: MongoDB
- **Image Processing**: OpenCV, PIL
- **PDF Generation**: ReportLab

## Project Structure

```
plant_disease_detection/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── Plantdisease-1.h5       # Pre-trained ML model
├── class_indices.json      # Class indices for the model
├── traits.json             # Disease information database
├── static/                 # Static assets (CSS, JS, images)
├── templates/              # HTML templates
│   └── index.html          # Main application page
├── uploads/                # Folder for uploaded images
└── diagnosis_reports/      # Folder for generated reports
```

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- MongoDB (local or Atlas)
- Virtual environment (recommended)

### Installation Steps

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/plant-disease-detection.git
   cd plant-disease-detection
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables (optional):
   Create a `.env` file in the project root with the following variables:
   ```
   MONGO_URI=your_mongodb_connection_string
   MODEL_PATH=path_to_model_file
   CLASS_INDICES_PATH=path_to_class_indices_file
   DISEASE_INFO_PATH=path_to_traits_json_file
   PORT=8080
   ```

5. Run the application:
   ```
   python app.py
   ```

6. Open your browser and navigate to `http://localhost:8080`

## Deployment

### Deploying to Heroku

1. Create a Heroku account and install the Heroku CLI
2. Login to Heroku:
   ```
   heroku login
   ```

3. Create a new Heroku app:
   ```
   heroku create plant-doctor-app
   ```

4. Add a Procfile with the following content:
   ```
   web: gunicorn app:app
   ```

5. Push to Heroku:
   ```
   git push heroku main
   ```

6. Set environment variables:
   ```
   heroku config:set MONGO_URI=your_mongodb_connection_string
   ```

### Deploying with Docker

1. Create a Dockerfile with the following content:
   ```
   FROM python:3.8-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   EXPOSE 8080

   CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
   ```

2. Build and run the Docker image:
   ```
   docker build -t plant-doctor .
   docker run -p 8080:8080 plant-doctor
   ```

## Usage

1. Load the model and class indices using the buttons in the header
2. Upload a plant leaf image using the upload form
3. Click "Diagnose Now" to process the image
4. View the diagnosis results, including disease details and treatment recommendations
5. Download a PDF report or view historical comparisons

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Plant disease dataset from [PlantVillage](https://plantvillage.psu.edu/)
- TensorFlow and Keras for the machine learning framework
- Flask for the web framework
