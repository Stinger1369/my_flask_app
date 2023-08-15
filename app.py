from flask import Flask, request, render_template
from modules.clean_data import remove_duplicates_blueprint
from modules.explore_data import replace_missing_blueprint
import pandas as pd
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.register_blueprint(remove_duplicates_blueprint)
app.register_blueprint(replace_missing_blueprint)

# Définition du chemin absolu pour le dossier d'upload
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def determine_separator(file):
    separators = [',', ';', '\t']
    max_cols = 0
    best_sep = ','

    # Position de départ du fichier pour revenir après le test
    start_position = file.tell()

    for sep in separators:
        try:
            file.seek(start_position)  # Retourner à la position de départ pour chaque test
            data = pd.read_csv(file, sep=sep, nrows=1)  # lire seulement la première ligne pour déterminer le séparateur
            if len(data.columns) > max_cols:
                max_cols = len(data.columns)
                best_sep = sep
        except pd.errors.EmptyDataError:
            return None
        except pd.errors.ParserError:
            continue
    return best_sep

@app.route("/", methods=["GET", "POST"])
def index():
    data = None
    cleaned_data = None  # Initialize cleaned_data
    error_message = None

    if request.method == "POST":
        csv_file = request.files["file"]

        if not csv_file or csv_file.filename == '':
            error_message = "Aucun fichier sélectionné."
            return render_template("index.html", data=data, cleaned_data=cleaned_data, error_message=error_message)

        if not allowed_file(csv_file.filename):
            error_message = "Type de fichier non autorisé. Veuillez uploader un fichier CSV."
            return render_template("index.html", data=data, cleaned_data=cleaned_data, error_message=error_message)

        sep = determine_separator(csv_file.stream)
        if sep is None:
            error_message = "Le fichier est vide ou ne peut être lu comme un CSV."
            return render_template("index.html", data=data, cleaned_data=cleaned_data, error_message=error_message)

        csv_file.stream.seek(0)  # reset file pointer to start
        try:
            data = pd.read_csv(csv_file, sep=sep)

            # Sauvegarde du fichier dans le dossier "uploads"
            filename = secure_filename(csv_file.filename)
            csv_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        except Exception as e:
            error_message = str(e)
            return render_template("index.html", data=data, cleaned_data=cleaned_data, error_message=error_message)

    return render_template("index.html", data=data, cleaned_data=cleaned_data)
if __name__ == "__main__":
    app.run(debug=True)

@app.route("/clean_data", methods=["POST"])
def clean_data():
    # Assurez-vous d'avoir le chemin du fichier uploadé
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(request.form['filename']))
    data = pd.read_csv(filepath)

    data = remove_nan(data)
    data = remove_zeros(data)

    cleaned_filepath = os.path.join(app.config['UPLOAD_FOLDER'], "cleaned_" + secure_filename(request.form['filename']))
    data.to_csv(cleaned_filepath, index=False)

    return render_template("cleaned_data.html", data=data, path=cleaned_filepath)



@remove_duplicates_blueprint.route("/remove_duplicates", methods=["POST"])
def remove_duplicates():
    # Obtenir le chemin du fichier CSV uploadé
    filepath = request.form['filepath']
    data = pd.read_csv(filepath)

    # Supprimer les doublons
    cleaned_data = data.drop_duplicates()

    # Sauvegarder les données nettoyées
    cleaned_filepath = filepath.replace(".csv", "_no_duplicates.csv")
    cleaned_data.to_csv(cleaned_filepath, index=False)

    return render_template("index.html", data=data, cleaned_data=cleaned_data)
