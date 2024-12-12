from flask import Flask
from flask_api.routes.data_routes import data_blueprint
from flask_api.utils.data_cleaning import CustomJSONEncoder  

app = Flask(__name__)

# Register the blueprint
app.register_blueprint(data_blueprint)

if __name__ == "__main__":
    app.run(debug=True)
    app.json_encoder = CustomJSONEncoder