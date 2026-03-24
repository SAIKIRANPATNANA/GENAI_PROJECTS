from flask import Flask, request, jsonify, send_from_directory, render_template
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
import subprocess

def convert_ppt_to_pdf(ppt_path, output_dir):
    try:
        subprocess.run(
            ['/usr/bin/soffice', '--headless', '--convert-to', 'pdf', '--outdir', output_dir, ppt_path],
            check=True
        )
        print(f"Converted '{ppt_path}' to PDF successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
    except FileNotFoundError:
        print("Error: LibreOffice (soffice) not found. Ensure it is installed and in your PATH.")

# ppt_file = "7_wt_clientSideScripting-Inro.pptx"  # Replace with the actual path
# output_dir = "/home/user/Documents/HYBD"   # Replace with your desired output directory
# convert_ppt_to_pdf(ppt_file, output_dir)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('test.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith(('.ppt', '.pptx')):
        return jsonify({'error': 'Invalid file format. Please upload a PPT or PPTX file'}), 400
    
    try:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        ppt_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(ppt_path)
        
        # Convert to PDF
        convert_ppt_to_pdf(ppt_path, app.config['UPLOAD_FOLDER'])
        
        # Generate PDF filename
        pdf_filename = os.path.splitext(filename)[0] + '.pdf'
        pdf_url = f'/download/{pdf_filename}'
        
        return jsonify({'success': True, 'pdf_url': pdf_url})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)