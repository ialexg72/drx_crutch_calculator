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
@app.route('/processing')
def processing():
    return render_template('processing.html')

@app.route('/questionnaire', methods=['GET'])
def questionnaire():
    return render_template('questionnaire.html')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_xml():
    return loading_and_processing_xml.upload_xml()

@app.route('/reports/<filename>')
def download_report(filename):
    return send_from_directory(app.config['REPORT_FOLDER'], filename, as_attachment=True)
        
if __name__ == '__main__':
    app.run(debug=True)
