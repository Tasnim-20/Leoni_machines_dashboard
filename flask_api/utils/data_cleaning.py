from flask import jsonify
import numpy as np
import pandas as pd
import json
from datetime import datetime, timedelta
import pandas as pd


# Basic data cleaning
def clean_data(df):
    # Remove completely empty rows
    df.dropna(how='all', inplace=True)

    columns_to_drop = [
    'No of Sleeves',
    'No of Seal Applicators', 
    'No of Seals',
    'No of Tools',
    'No of Terminals', 
    'No of Stripping Lengths',
    'No of Cross Sections',
    'No of Wire Types',
    'No of Wires',
    'Order No.',
    'Remark'
    ]
    # Drop the specified columns
    df = df.drop(columns=columns_to_drop)

    
    # Convert timestamp columns to datetime
    timestamp_columns = ['Time Stamp', 'Insert Time', 'Update Time']
    for col in timestamp_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Convert duration to timedelta
    if 'Duration' in df.columns:
        df['Duration'] = pd.to_timedelta(df['Duration'])
    
    # Convert numeric columns
    numeric_columns = [
        'Produced Parts', 'Waste', 'No of Wires', 'No of Wire Types', 
        'No of Cross Sections', 'No of Stripping Lengths', 
        'No of Terminals', 'No of Tools', 'No of Seals', 
        'No of Seal Applicators', 'No of Sleeves'
    ]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df







def read_custom_csv(file_path):
    """
    Read CSV file with specific handling for problematic files
    
    Parameters:
    -----------
    file_path : str
        Path to the CSV file
    
    Returns:
    --------
    pandas.DataFrame
        Cleaned and processed DataFrame
    """
    try:
        # Try reading with different encodings and error handling
        encodings_to_try = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings_to_try:
            try:
                # Read the CSV file with multiple options to handle parsing issues
                df = pd.read_csv(
                    file_path, 
                    encoding=encoding,
                    on_bad_lines='skip',  # Updated for newer pandas versions
                    delimiter=',',  # Explicit comma delimiter
                    skipinitialspace=True,  # Skip spaces after delimiter
                    low_memory=False  # Prevent mixed type inference warning
                )
                
                # If successful, break the loop
                break
            except Exception as e:
                print(f"Failed to read with {encoding} encoding: {e}")
        else:
            raise ValueError("Could not read the file with any attempted encoding")
        

        
        # Apply cleaning
        df = clean_data(df)
        
        return df
    
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return None




def serialize_dataframe(df):
    """
    Convert DataFrame to a JSON-serializable format
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Input DataFrame to be serialized
    
    Returns:
    --------
    list
        List of dictionaries representing DataFrame rows
    """
    def convert_value(val):
        # Handle NaN and NaT values
        if pd.isna(val) or val is pd.NaT:
            return None
        
        # Convert Timestamp to string
        if isinstance(val, pd.Timestamp):
            try:
                # Use isoformat or convert to string
                return val.isoformat() if not pd.isnull(val) else None
            except Exception:
                return str(val) if val is not pd.NaT else None
        
        # Convert timedelta to total seconds
        elif isinstance(val, timedelta):
            try:
                return val.total_seconds()
            except Exception:
                return None
        
        # Handle numpy types
        elif isinstance(val, (np.integer, np.floating)):
            # Convert numpy types to native Python types
            return val.item() if not pd.isnull(val) else None
        
        return val

    # Create a copy to avoid modifying original data
    serialized_data = df.copy()
    
    # Apply conversion to each column
    for col in serialized_data.columns:
        try:
            serialized_data[col] = serialized_data[col].apply(convert_value)
        except Exception as e:
            print(f"Error converting column {col}: {e}")
            # Fallback to string conversion if apply fails
            serialized_data[col] = serialized_data[col].astype(str)
    
    # Convert to list of dictionaries
    return serialized_data.to_dict(orient='records')









class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle special data types
    """
    def default(self, obj):
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            return obj.total_seconds()
        elif isinstance(obj, float) and pd.isna(obj):
            return None
        return super().default(obj)

# Example usage in Flask route
def get_data():
    """
    Flask route to get data with proper JSON serialization
    """
    try:
        # Your existing data reading code
        file_path = r"C:\Users\tasni\OneDrive\Desktop\Leoni_project\leonivenev\Filecao.csv"
        df = read_custom_csv(file_path)
        
        if df is not None:
            # Serialize the DataFrame
            serialized_data = serialize_dataframe(df)
            
            return jsonify(serialized_data)
        else:
            return jsonify({"error": "Could not read the CSV file"}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
