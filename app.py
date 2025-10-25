import os
import subprocess
from flask import Flask, request, render_template, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import uuid # Per creare nomi di file unici

# Configuriamo Flask
app = Flask(__name__)

# Definiamo le cartelle per gli upload e gli output
UPLOAD_FOLDER = '/tmp/uploads'
OUTPUT_FOLDER = '/tmp/outputs'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Limite di 50 MB

# Creiamo le cartelle se non esistono
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """Mostra la pagina HTML principale."""
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_video():
    """Gestisce l'upload e la conversione."""
    
    if 'image' not in request.files or 'audio' not in request.files:
        return jsonify({"error": "File immagine o audio mancante"}), 400

    image_file = request.files['image']
    audio_file = request.files['audio']

    if image_file.filename == '' or audio_file.filename == '':
        return jsonify({"error": "Nessun file selezionato"}), 400

    # Salvataggio sicuro
    unique_id = str(uuid.uuid4())
    image_name = secure_filename(image_file.filename)
    audio_name = secure_filename(audio_file.filename)
    
    image_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_{image_name}")
    audio_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_{audio_name}")
    output_filename = f"output_{unique_id}.mp4"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    
    try:
        image_file.save(image_path)
        audio_file.save(audio_path)
    except Exception as e:
        return jsonify({"error": f"Errore nel salvataggio file: {e}"}), 500

    # Comando FFmpeg
    try:
        command = [
            'ffmpeg',
            '-loop', '1',          # Loopa l'immagine
            '-i', image_path,     # Input immagine
            '-i', audio_path,     # Input audio
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-shortest',          # Termina con l'audio
            '-y',                 
            output_path
        ]
        
        subprocess.run(command, check=True, capture_output=True, text=True)

    except subprocess.CalledProcessError as e:
        print("Errore FFmpeg:", e.stderr)
        return jsonify({"error": "Errore durante la conversione FFmpeg", "details": e.stderr}), 500
    except Exception as e:
        return jsonify({"error": f"Errore generico: {e}"}), 500

    # Restituisce il link per il download
    return jsonify({
        "success": True, 
        "downloadUrl": f"/download/{output_filename}"
    })

@app.route('/download/<filename>')
def download_file(filename):
    """Permette all'utente di scaricare il file generato."""
    try:
        return send_from_directory(
            OUTPUT_FOLDER, 
            filename, 
            as_attachment=True,
            download_name="video_generato.mp4"
        )
    except FileNotFoundError:
        return jsonify({"error": "File non trovato"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
