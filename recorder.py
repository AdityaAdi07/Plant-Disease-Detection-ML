from pymongo import MongoClient
import pandas as pd
import os
from datetime import datetime

def mongo_collection_to_excel(connection_string, database_name, collection_name, output_path=None):
    
    try:
        # Connect to MongoDB
        client = MongoClient(connection_string)
        db = client[database_name]
        collection = db[collection_name]
        
        # Retrieve all documents from the collection
        documents = list(collection.find())
        if not documents:
            raise ValueError(f"The collection '{collection_name}' is empty.")
        
        # Convert documents to DataFrame
        df = pd.json_normalize(documents)
        
        # Generate timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Set output directory
        if output_path is None:
            output_path = os.getcwd()
        
        # Generate filenames
        csv_filename = f"{collection_name}_export_{timestamp}.csv"
        excel_filename = f"{collection_name}_export_{timestamp}.xlsx"
        
        csv_path = os.path.join(output_path, csv_filename)
        excel_path = os.path.join(output_path, excel_filename)
        
        # Export to CSV
        df.to_csv(csv_path, index=False)
        
        # Export to Excel
        df.to_excel(excel_path, index=False)
        
        print(f"Files generated successfully:")
        print(f"CSV: {csv_path}")
        print(f"Excel: {excel_path}")
        
        return csv_path, excel_path
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, None
    
    finally:
        client.close()

# Example usage
if __name__ == "__main__":
    # Replace with your MongoDB connection details
    CONNECTION_STRING = "mongodb+srv://sushmaaditya717:rdqdcaYTLY7p50za@adityaadi.vztbe.mongodb.net/mern_1_db"
    DATABASE_NAME = "mern_1_db"
    COLLECTION_NAME = "notess"
    
    # Optional: Specify output directory
    OUTPUT_PATH = r'C:\RVCE(2023-27)\venv\uploads'  # or None for current directory
    
    csv_file, excel_file = mongo_collection_to_excel(
        CONNECTION_STRING,
        DATABASE_NAME,
        COLLECTION_NAME,
        OUTPUT_PATH
    )
