# app.py
import uuid
import logging
import logging.config
import os
from datetime import datetime
from src import settings, loading_and_processing_xml
from flask import Flask, render_template, send_from_directory, request, jsonify, redirect, url_for

app = Flask(__name__)
app.config.from_object(settings.Config) 

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

@app.route('/questionnaire', methods=['GET'])
def questionnaire():
    return render_template('questionnaire.html')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_xml():
    logger.info("Начата обработка загруженного XML файла")
    if 'xml_file' not in request.files:
        logger.error("Файл не был загружен в запросе")
        return "Файл не загружен", 400
    
    file = request.files['xml_file']
    if file.filename == '':
        logger.error("Загружен файл с пустым именем")
        return "Имя файла пустое", 400
    
    if not file.filename.lower().endswith('.xml'):
        logger.error(f"Попытка загрузки файла неверного формата: {file.filename}")
        return "Неподдерживаемый формат файла. Пожалуйста, загрузите XML файл.", 400
    
    # Сохраняем загруженный XML файл
    filename = f"{uuid.uuid4()}.xml"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    logger.info(f"XML файл успешно сохранен: {filepath}")
    return loading_and_processing_xml.upload_xml(filepath)

@app.route('/process-xml', methods=['POST'])
def process_xml_data():
    logger.info("Начата обработка XML данных из формы")
    if not request.data:
        logger.error("XML данные не получены")
        return jsonify({"error": "XML данные не получены"}), 400
    
    # Сохраняем XML данные в файл
    filename = f"{uuid.uuid4()}.xml"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        with open(filepath, 'wb') as f:
            f.write(request.data)
        logger.info(f"XML данные успешно сохранены: {filepath}")
        
        # Обработка XML файла
        result = loading_and_processing_xml.upload_xml(filepath)
        if isinstance(result, tuple):
            return result
        return result
    except Exception as e:
        logger.error(f"Ошибка при обработке XML данных: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/reports/<filename>')
def download_report(filename):
    return send_from_directory(app.config['REPORT_FOLDER'], filename, as_attachment=True)
        
if __name__ == '__main__':
    app.run(debug=True)
