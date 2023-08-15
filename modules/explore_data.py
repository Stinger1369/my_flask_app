from flask import Blueprint, request
import pandas as pd

replace_missing_blueprint = Blueprint('replace_missing_blueprint', __name__)

@replace_missing_blueprint.route("/replace_missing", methods=["POST"])
def replace_missing():
    # Get the path of the uploaded CSV
    filepath = request.form['filepath']
    data = pd.read_csv(filepath)

    # Replace missing values
    for col in data.columns:
        if data[col].dtype == "object":  # if column is of type string/object
            data[col].fillna(data[col].mode()[0], inplace=True)
        else:
            data[col].fillna(data[col].mean(), inplace=True)

    # Save data after replacing missing values
    cleaned_filepath = filepath.replace(".csv", "_replaced_missing.csv")
    data.to_csv(cleaned_filepath, index=False)

    return cleaned_filepath
