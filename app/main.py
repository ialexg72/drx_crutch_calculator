# app.py
from fileinput import filename
import uuid
import logging
import logging.config
import os
import base64
from src import settings, loading_and_processing_xml, utility
from flask import Flask, render_template, send_from_directory, request, jsonify, redirect, url_for
from functools import wraps
from flask import request, Response
from datetime import datetime

app = Flask(__name__)
app.config.from_object(settings.Config) 
settings.Config.create_folders()  # Create required folders on startup

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

USERNAME = 'admin'
PASSWORD = 'password'

def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return Response(
        'Необходима авторизация.', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

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
    
    # Сначала сохраняем с временным именем
    temp_filename = f"temp_{uuid.uuid4()}.xml"
    temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
    file.save(temp_filepath)
    logger.info(f"XML файл временно сохранен: {temp_filepath}")

    try:
        result = loading_and_processing_xml.upload_xml(temp_filepath)
        logging.debug(f"Рендеринг шаблона 'index.html' с отчетной ссылкой: {result}")
        return render_template('index.html', report_link=result)
    except Exception as e:
        logging.error(f"Ошибка при обработке файла: {e}")
        # Удаляем временный файл в случае ошибки
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        return "Ошибка при обработке файла", 500

@app.route('/process-xml', methods=['POST'])
def process_xml_data():
    logger.info("Начата обработка XML данных из формы")
    if not request.data:
        logger.error("XML данные не получены")
        return jsonify({"error": "XML данные не получены"}), 400
    logger.info(f"Получены XML данные размером {len(request.data)} байт")
    # Сохраняем XML данные в файл
    encoded_name = request.headers.get('X-Organization-Name', 'VW5rbm93bg==')  # 'Unknown' в Base64
    try:
        import base64
        organization_name = base64.b64decode(encoded_name).decode('utf-8')
    except Exception as e:
        logger.error(f"Ошибка при декодировании названия организации: {e}")
        organization_name = 'Unknown'
    filepath, _ = utility.generate_filename(organization_name, "xml")
    logger.info(f"Сохраняем XML в файл: {filepath}")
    try:
        with open(filepath, 'wb') as f:
            f.write(request.data)
        logger.info(f"XML данные успешно сохранены: {filepath}")
        # Обработка XML файла
        logger.info("Начинаем обработку XML файла через upload_xml")
        result = loading_and_processing_xml.upload_xml(filepath)
        logger.info(f"Получен результат от upload_xml: {result}")           
        return jsonify({
            'success': True,
            'report_link': result,
            'message': 'Отчет успешно создан'
        })
    except Exception as e:
        logger.error(f"Ошибка при обработке XML данных: {str(e)}")
        logger.exception("Полный стек ошибки:")
        return jsonify({"error": str(e)}), 500

@app.route('/reports/<filename>')
def download_report(filename):
    return send_from_directory(app.config['REPORT_FOLDER'], filename, as_attachment=True)

@app.route('/admin', methods=['GET'])
@requires_auth
def admin():
    reports = []
    try:
        for filename in os.listdir(app.config['REPORT_FOLDER']):
            filepath = os.path.join(app.config['REPORT_FOLDER'], filename)
            creation_date = os.path.getctime(filepath)
            reports.append({
                'name': filename,
                'creation_date': datetime.fromtimestamp(creation_date).strftime('%Y-%m-%d %H:%M:%S')
            })
    except Exception as e:
        logger.error(f"Ошибка при получении списка отчетов: {e}")
    return render_template('admin.html', reports=reports)
        
if __name__ == '__main__':
    app.run(debug=True)
