import logging
import logging.handlers
import os

# Настройки FLASK
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join('uploads')
    REPORT_FOLDER = os.path.join( 'ready_reports')
    TEMPLATE_FOLDER = os.path.join('word_templates')
    TEMPLATE_SCHEMES = os.path.join('schemes_template')
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False


# Настройки логирования
# Добавляем словарь конфигурации для dictConfig
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'logs/app.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'encoding': 'utf-8',
            'formatter': 'standard',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {  # корневой логгер
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True
        },
        'werkzeug': {  # логгер для werkzeug
            'level': 'WARNING',
        },
    }
}

# Оставляем существующую настройку логгера
if not os.path.exists('logs'):
    os.makedirs('logs')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)