# app.py
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

# Глобальная переменная для хранения статуса расчета
calculation_status = {
    'status': 'not_started',  # 'not_started', 'processing', 'completed', 'failed'
    'progress': 0,
    'message': '',
    'report_link': None
}

@app.route('/processing')
def processing():
    return render_template('processing.html')

@app.route('/questionnaire', methods=['GET'])
def questionnaire():
    return render_template('questionnaire.html')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/calculation-status')
def get_calculation_status():
    return jsonify(calculation_status)

@app.route('/upload', methods=['POST'])
def upload_xml():
    return loading_and_processing_xml.upload_xml()

@app.route('/reports/<filename>')
def download_report(filename):
    return send_from_directory(app.config['REPORT_FOLDER'], filename, as_attachment=True)

@app.route('/save-xml', methods=['POST'])
def save_xml():
    try:
        # Сбрасываем статус расчета
        calculation_status.update({
            'status': 'processing',
            'progress': 0,
            'message': 'Начинаем расчет...',
            'report_link': None
        })

        # Запускаем расчет
        result = loading_and_processing_xml.upload_xml2()
        
        # Обновляем статус по завершении
        calculation_status.update({
            'status': 'completed',
            'progress': 100,
            'message': 'Расчет завершен',
            'report_link': result.get('report_link')
        })

        # Возвращаем успешный статус вместо редиректа
        return jsonify({'success': True})

    except Exception as e:
        # В случае ошибки
        calculation_status.update({
            'status': 'failed',
            'progress': 100,
            'message': str(e),
            'report_link': None
        })
        return jsonify({'error': str(e)}), 500
        
if __name__ == '__main__':
    app.run(debug=True)
