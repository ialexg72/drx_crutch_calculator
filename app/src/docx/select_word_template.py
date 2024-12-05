import os
import sys
from .. import settings
import logging
import logging.config

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

def select_word_template(operationsystem, kubernetes, version, app):
    if operationsystem.lower() == "linux":
        template_path = os.path.join(app.config['TEMPLATE_FOLDER'], f'RecomendBaseTpl{version}_linux.docx')
        if kubernetes.lower() == "true":
            template_path = os.path.join(app.config['TEMPLATE_FOLDER'], f'RecomendBaseTpl{version}_kubernetes.docx')
    else:
        template_path = os.path.join(app.config['TEMPLATE_FOLDER'], f'RecomendBaseTpl{version}_windows.docx')
    if not os.path.exists(template_path):
        logger.info("Шаблон Word не найден.")
    return template_path