from flask import Blueprint, jsonify
import pandas as pd
from flask_api.utils.data_cleaning import clean_data, read_custom_csv, serialize_dataframe 
# Define the blueprint
data_blueprint = Blueprint('data', __name__)

# Load and clean data (make sure the path is correct)
file_path="C:\\Users\\tasni\\OneDrive\\Desktop\\Leoni_project\\leonivenev\\Filecao.csv"

df = read_custom_csv(file_path)
print(df.shape)


@data_blueprint.route('/api/data', methods=['GET'])
def get_data():
    try:
        # If the DataFrame is empty
        if df is None or df.empty:
            return jsonify({"message": "No data found in the file"}), 404

        # Use the new serialization function
        serialized_data = serialize_dataframe(df)
        
        return jsonify(serialized_data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

