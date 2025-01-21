from flask import Flask, render_template, request
import pandas as pd
from datetime import datetime

app = Flask(__name__)

def load_data():
    data = pd.read_csv(r'C:\RVCE(2023-27)\venv\uploads\notess_export_20250121_003228.csv')
    data.columns = [col.strip() for col in data.columns]
    return data

def format_comparison(rows):
    results = []
    for _, row in rows.iterrows():
        result = {
            'Plant Name': row['plant_name'],
            'Disease Percentage': f"{row['disease_percentage']}%",
            'Status': row['status'],
            'Confidence Score': f"{row['confidence_score']:.2f}",
            'Timestamp': row['timestamp'],
            'Disease Name': row['disease_details.name'],
            'Lacking Trait': row['disease_details.lacking_trait'],
            'Symptoms': row['disease_details.symptoms'],
            'Treatment': row['disease_details.treatment']
        }
        results.append(result)
    return results

@app.route('/')
def home():
    return render_template('compare.html')

@app.route('/compare', methods=['POST'])
def compare():
    comparison_type = request.form['comparison_type']
    search_term = request.form.get('search_term', '')
    plant_name = request.form.get('plant_name', '')
    
    data = load_data()
    results = []
    
    if comparison_type == 'plant_name':
        matching_rows = data[data['plant_name'].str.contains(search_term, case=False, na=False)]
        results = format_comparison(matching_rows)
        
    elif comparison_type == 'disease_name':
        matching_rows = data[data['disease_details.name'].str.contains(search_term, case=False, na=False)]
        results = format_comparison(matching_rows)
        
    elif comparison_type == 'lacking_trait':
        matching_rows = data[data['disease_details.lacking_trait'].str.contains(search_term, case=False, na=False)]
        results = format_comparison(matching_rows)
        
    elif comparison_type == 'date':
        matching_rows = data[data['plant_name'].str.contains(plant_name, case=False, na=False)]
        matching_rows = matching_rows.sort_values('timestamp')
        results = format_comparison(matching_rows)

    return render_template('results.html', results=results, comparison_type=comparison_type)

if __name__ == '__main__':
    app.run(debug=True)