from flask import Blueprint, request, render_template, current_app
import pandas as pd
import os
from werkzeug.utils import secure_filename

remove_duplicates_blueprint = Blueprint('remove_duplicates_blueprint', __name__)

# Définissez BASE_DIR et UPLOAD_DIR après vos importations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')

@remove_duplicates_blueprint.route("/remove_duplicates", methods=["POST"])
def remove_duplicates():
    # Get the path of the uploaded CSV
    filename = secure_filename(request.form['filepath'])
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    print(f"Trying to open file at path: {filepath}")

    data = pd.read_csv(filepath)

    # Remove duplicates
    cleaned_data = data.drop_duplicates()

    # Save cleaned data
    cleaned_filepath = filepath.replace(".csv", "_no_duplicates.csv")
    cleaned_data.to_csv(cleaned_filepath, index=False)

    return render_template("operations.html", cleaned_data=cleaned_data)


