# from flask import Flask, render_template, request, jsonify, send_file
# from langchain_huggingface import HuggingFaceEmbeddings
# from helper import *
# import os
# import pdfkit
# import io

# app = Flask(__name__)
# # Global configurations
# MODEL_NAME = "deepseek-r1-distill-llama-70b"
# API_KEY = os.getenv("GROQ_API_KEY")
# UPLOAD_FOLDER = "uploads"

# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/upload_bos', methods=['POST'])
# def upload_bos():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file uploaded'}), 400
    
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No file selected'}), 400
    
#     if file and file.filename.endswith('.pdf'):
#         file_path = os.path.join(UPLOAD_FOLDER, file.filename)
#         print(file_path)
#         file.save(file_path)
#         try:
#             embeddings = save_bos_to_db(file_path)
#             return jsonify({'message': 'File processed successfully'})
#         except Exception as e:
#             return jsonify({'error': str(e)}), 500
    
#     return jsonify({'error': 'Invalid file type'}), 400

# @app.route('/get_units', methods=['POST'])
# def get_units():
#     subject = request.json.get('subject')
#     if not subject:
#         return jsonify({'error': 'Subject is required'}), 400
    
#     try:
#         llm = model_setup(MODEL_NAME, API_KEY)
#         embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#         retriever = load_db_n_get_retriever("faiss_index", embeddings)
#         units = GetUnits(llm, retriever, subject)
#         return jsonify({'units': units})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/get_topics', methods=['POST'])
# def get_topics():
#     subject = request.json.get('subject')
#     unit = request.json.get('unit')
#     if not subject or not unit:
#         return jsonify({'error': 'Subject and unit are required'}), 400
    
#     try:
#         llm = model_setup(MODEL_NAME, API_KEY)
#         embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#         retriever = load_db_n_get_retriever("faiss_index", embeddings)
#         topics = GetTopics(llm, retriever, subject, unit)
#         return jsonify({'topics': topics})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/get_content', methods=['POST'])
# def get_content():
#     subject = request.json.get('subject')
#     topic = request.json.get('topic')
#     student_level = request.json.get('student_level')
    
#     if not subject or not topic:
#         return jsonify({'error': 'Subject and topic are required'}), 400
    
#     if student_level not in ['beginner', 'intermediate', 'advanced']:
#         return jsonify({'error': 'Invalid student level'}), 400
    
#     try:
#         llm = model_setup(MODEL_NAME, API_KEY)
#         content = getContent(MODEL_NAME, API_KEY, subject, topic, student_level)
#         revision_notes = GetRevisionNotes(llm, content, topic)
        
#         return jsonify({
#             'content': content,
#             'revision_notes': revision_notes
#         })
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/download_pdf', methods=['POST'])
# def download_pdf():
#     content = request.json.get('content')
#     try:
#         pdf = pdfkit.from_string(content, False)
#         return send_file(
#             io.BytesIO(pdf),
#             mimetype='application/pdf',
#             as_attachment=True,
#             download_name='generated_content.pdf'
#         )
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True)
# from flask import Flask, render_template, request, jsonify, send_file
# from langchain_huggingface import HuggingFaceEmbeddings
# from functools import lru_cache
# from helper import *
# import os
# import pdfkit
# import io
# from typing import Optional
# from dataclasses import dataclass
# from werkzeug.utils import secure_filename
# from contextlib import contextmanager

# @dataclass
# class Config:
#     MODEL_NAME: str = "deepseek-r1-distill-llama-70b"
#     API_KEY: str = os.getenv("GROQ_API_KEY")
#     UPLOAD_FOLDER: str = "uploads"
#     ALLOWED_EXTENSIONS: set = frozenset({'pdf'})
#     STUDENT_LEVELS: set = frozenset({'beginner', 'intermediate', 'advanced'})
#     MAX_FILE_SIZE: int = 16 * 1024 * 1024  # 16MB

# class APIException(Exception):
#     def __init__(self, message: str, status_code: int = 400):
#         self.message = message
#         self.status_code = status_code
#         super().__init__(self.message)

# class EmbeddingsManager:
#     _instance = None
#     _embeddings = None
#     _retriever = None

#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super(EmbeddingsManager, cls).__new__(cls)
#         return cls._instance

#     def initialize(self):
#         if self._embeddings is None:
#             print("Initializing embeddings model...")
#             self._embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#             self._retriever = load_db_n_get_retriever("faiss_index", self._embeddings)
#             print("Embeddings model initialized successfully")

#     @property
#     def embeddings(self):
#         if self._embeddings is None:
#             self.initialize()
#         return self._embeddings

#     @property
#     def retriever(self):
#         if self._retriever is None:
#             self.initialize()
#         return self._retriever

# def create_app(config: Optional[Config] = None) -> Flask:
#     app = Flask(__name__)
    
#     if config is None:
#         config = Config()
    
#     app.config.from_object(config)
    
#     # Ensure upload directory exists
#     os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
#     # Initialize embeddings at app startup
#     embeddings_manager = EmbeddingsManager()
#     embeddings_manager.initialize()
    
#     @app.errorhandler(APIException)
#     def handle_api_exception(error):
#         return jsonify({'error': error.message}), error.status_code
    
#     @contextmanager
#     def get_llm():
#         llm = model_setup(app.config['MODEL_NAME'], app.config['API_KEY'])
#         yield llm
    
#     def allowed_file(filename: str) -> bool:
#         return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
    
#     @app.route('/')
#     def index():
#         return render_template('index.html')
    
#     @app.route('/upload_bos', methods=['POST'])
#     def upload_bos():
#         if 'file' not in request.files:
#             raise APIException('No file uploaded')
        
#         file = request.files['file']
#         if not file or not file.filename:
#             raise APIException('No file selected')
        
#         if not allowed_file(file.filename):
#             raise APIException('Invalid file type')
        
#         if request.content_length > app.config['MAX_FILE_SIZE']:
#             raise APIException('File size exceeds maximum limit')
        
#         filename = secure_filename(file.filename)
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
#         try:
#             file.save(file_path)
#             save_bos_to_db(file_path)
#             return jsonify({'message': 'File processed successfully'})
#         except Exception as e:
#             raise APIException(f'Error processing file: {str(e)}', 500)
#         finally:
#             # Clean up uploaded file
#             if os.path.exists(file_path):
#                 os.remove(file_path)
    
#     @app.route('/get_units', methods=['POST'])
#     def get_units():
#         subject = request.json.get('subject')
#         if not subject:
#             raise APIException('Subject is required')
        
#         try:
#             with get_llm() as llm:
#                 units = GetUnits(llm, embeddings_manager.retriever, subject)
#             return jsonify({'units': units})
#         except Exception as e:
#             raise APIException(f'Error retrieving units: {str(e)}', 500)
    
#     @app.route('/get_topics', methods=['POST'])
#     def get_topics():
#         subject = request.json.get('subject')
#         unit = request.json.get('unit')
        
#         if not subject or not unit:
#             raise APIException('Subject and unit are required')
        
#         try:
#             with get_llm() as llm:
#                 topics = GetTopics(llm, embeddings_manager.retriever, subject, unit)
#             return jsonify({'topics': topics})
#         except Exception as e:
#             raise APIException(f'Error retrieving topics: {str(e)}', 500)
    
#     @app.route('/get_content', methods=['POST'])
#     def get_content():
#         data = request.json
#         subject = data.get('subject')
#         topic = data.get('topic')
#         student_level = data.get('student_level')
        
#         if not subject or not topic:
#             raise APIException('Subject and topic are required')
        
#         if student_level not in app.config['STUDENT_LEVELS']:
#             raise APIException('Invalid student level')
        
#         try:
#             with get_llm() as llm:
#                 content = getContent(app.config['MODEL_NAME'], app.config['API_KEY'],
#                                    subject, topic, student_level)
#                 revision_notes = GetRevisionNotes(llm, content, topic)
            
#             return jsonify({
#                 'content': content,
#                 'revision_notes': revision_notes
#             })
#         except Exception as e:
#             raise APIException(f'Error generating content: {str(e)}', 500)
    
#     @app.route('/download_pdf', methods=['POST'])
#     def download_pdf():
#         content = request.json.get('content')
#         if not content:
#             raise APIException('Content is required')
        
#         try:
#             pdf = pdfkit.from_string(content, False)
#             buffer = io.BytesIO(pdf)
#             buffer.seek(0)
#             return send_file(
#                 buffer,
#                 mimetype='application/pdf',
#                 as_attachment=True,
#                 download_name='generated_content.pdf'
#             )
#         except Exception as e:
#             raise APIException(f'Error generating PDF: {str(e)}', 500)
    
#     return app

# if __name__ == '__main__':
#     app = create_app()
#     app.run(debug=True)
# from flask import Flask, render_template, request, jsonify, send_file
# from langchain_huggingface import HuggingFaceEmbeddings
# from functools import lru_cache
# from helper import *
# import os
# import pdfkit
# import io
# from typing import Optional
# from dataclasses import dataclass
# from werkzeug.utils import secure_filename
# from contextlib import contextmanager
# import logging

# # Setup logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# @dataclass
# class Config:
#     MODEL_NAME: str = "deepseek-r1-distill-llama-70b"
#     API_KEY: str = os.getenv("GROQ_API_KEY")
#     UPLOAD_FOLDER: str = "uploads"
#     ALLOWED_EXTENSIONS: set = frozenset({'pdf'})
#     STUDENT_LEVELS: set = frozenset({'beginner', 'intermediate', 'advanced'})
#     MAX_FILE_SIZE: int = 16 * 1024 * 1024  # 16MB
#     HF_TOKEN: str = os.getenv('HUGGINGFACE_TOKEN')  # Get from environment variable
#     EMBEDDINGS_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

# class APIException(Exception):
#     def __init__(self, message: str, status_code: int = 400):
#         self.message = message
#         self.status_code = status_code
#         super().__init__(self.message)

# class EmbeddingsManager:
#     _instance = None
#     _embeddings = None
#     _retriever = None

#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super(EmbeddingsManager, cls).__new__(cls)
#         return cls._instance

#     def initialize(self, hf_token: str, model_name: str):
#         if self._embeddings is None:
#             try:
#                 logger.info("Initializing embeddings model...")
#                 if not hf_token:
#                     raise ValueError(
#                         "HuggingFace token is required. Please set the HUGGINGFACE_TOKEN environment variable."
#                     )
                
#                 os.environ['HUGGINGFACE_TOKEN'] = hf_token
#                 self._embeddings = HuggingFaceEmbeddings(
#                     model_name=model_name,
#                     model_kwargs={'token': hf_token}
#                 )
#                 self._retriever = load_db_n_get_retriever("faiss_index", self._embeddings)
#                 logger.info("Embeddings model initialized successfully")
#             except Exception as e:
#                 logger.error(f"Failed to initialize embeddings model: {str(e)}")
#                 raise APIException(
#                     "Failed to initialize embeddings model. Please check your HuggingFace token and try again.",
#                     status_code=500
#                 )

#     @property
#     def embeddings(self):
#         if self._embeddings is None:
#             raise APIException("Embeddings model not initialized", status_code=500)
#         return self._embeddings

#     @property
#     def retriever(self):
#         if self._retriever is None:
#             raise APIException("Retriever not initialized", status_code=500)
#         return self._retriever

# def create_app(config: Optional[Config] = None) -> Flask:
#     app = Flask(__name__)
    
#     if config is None:
#         config = Config()
    
#     app.config.from_object(config)
    
#     # Ensure upload directory exists
#     os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
#     # Initialize embeddings at app startup
#     embeddings_manager = EmbeddingsManager()
#     try:
#         embeddings_manager.initialize(
#             hf_token=app.config['HF_TOKEN'],
#             model_name=app.config['EMBEDDINGS_MODEL']
#         )
#     except APIException as e:
#         logger.error(f"Failed to initialize embeddings: {e.message}")
#         # Continue app initialization, but endpoints requiring embeddings will fail
    
#     @app.errorhandler(APIException)
#     def handle_api_exception(error):
#         return jsonify({'error': error.message}), error.status_code
    
#     @contextmanager
#     def get_llm():
#         llm = model_setup(app.config['MODEL_NAME'], app.config['API_KEY'])
#         yield llm
    
#     def allowed_file(filename: str) -> bool:
#         return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

#     # ... [rest of the routes remain the same] ...

#     @app.route('/health', methods=['GET'])
#     def health_check():
#         status = {
#             'status': 'healthy',
#             'embeddings_initialized': embeddings_manager._embeddings is not None
#         }
#         return jsonify(status)
    
#     return app

# def main():
#     # Check for required environment variables
#     if not os.getenv('HUGGINGFACE_TOKEN'):
#         logger.error("""
#             HUGGINGFACE_TOKEN environment variable is not set.
#             Please set it using:
#             export HUGGINGFACE_TOKEN='your_token_here'
            
#             You can get your token from: https://huggingface.co/settings/tokens
#         """)
#         exit(1)
    
#     app = create_app()
#     app.run(debug=True)

# if __name__ == '__main__':
#     main()