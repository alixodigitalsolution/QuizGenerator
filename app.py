from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from quiz_engine import generate_quiz_from_text
from utils import extract_text_from_pdf, allowed_file

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def handle_generation():
    try:
        # Handle File Upload
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                if filename.endswith('.pdf'):
                    content = extract_text_from_pdf(filepath)
                else:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                
                # Cleanup
                os.remove(filepath)
                
                num_q = request.form.get('num_questions', 5)
                difficulty = request.form.get('difficulty', 'Intermediate')
                quiz_type = request.form.get('quiz_type', 'Multiple Choice')
            else:
                return jsonify({"error": "Invalid file type"}), 400
        else:
            # Handle Text/Topic
            data = request.json
            content = data.get('text')
            num_q = data.get('num_questions', 5)
            difficulty = data.get('difficulty', 'Intermediate')
            quiz_type = data.get('quiz_type', 'Multiple Choice')

        if not content or len(content.strip()) < 5:
            return jsonify({"error": "Content is too short to generate a quiz."}), 400
            
        quiz = generate_quiz_from_text(content, num_q, difficulty, quiz_type)
        
        if isinstance(quiz, dict) and "error" in quiz:
            return jsonify(quiz), 500
            
        return jsonify(quiz)
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
