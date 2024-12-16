import logging
import logging.handlers
import os

# Настройки FLASK
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    PARENT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))
    TMP_DIR = os.path.join(PARENT_DIR, 'tmp')
    UPLOAD_FOLDER = os.path.join(TMP_DIR, 'uploads')
    REPORT_FOLDER = os.path.join(TMP_DIR, 'ready_reports')
    SCHEME_FOLDER = os.path.join(TMP_DIR, 'ready_schemes')
    TEMPLATE_FOLDER = os.path.join('word_templates')
    TEMPLATE_SCHEMES = os.path.join('schemes_template')
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB

    @classmethod
    def create_folders(cls):
        """Create all required folders if they don't exist."""
        folders = [
            cls.TMP_DIR,
            cls.UPLOAD_FOLDER,
            cls.REPORT_FOLDER,
            cls.SCHEME_FOLDER,
            cls.TEMPLATE_FOLDER,
            cls.TEMPLATE_SCHEMES
        ]
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)

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
            'level': 'INFO',
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