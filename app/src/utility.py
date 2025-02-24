import os
import re
from datetime import datetime
from . import settings
from flask import Flask

app = Flask(__name__)
app.config.from_object(settings.Config) 

def round_up_to_even(value):
    return value if value % 2 == 0 else value + 1

#Функция получения даты
def get_current_date_formatted():
    today = datetime.today()
    return today.strftime("%d.%m.%Y")

#функция проверки существования файла
def file_exists(file_path):
    return os.path.exists(file_path)

#функция проверки существования файла
def sanitize_filename(name):
    """
    Очищает строку от недопустимых символов в имени файла Windows.
    """
    # Заменяем недопустимые символы на подчеркивание
    invalid_chars = r'[<>:"/\\|?*]'
    return re.sub(invalid_chars, '_', name)

def generate_filename(organization, filetype):
    """
    Генерирует имя файла с автоинкрементом версии.
    Пример: organization_v1.xml, organization_v2.xml, и т.д.
    """
    # Очищаем имя организации от недопустимых символов
    organization = sanitize_filename(organization.replace(" ", "_"))
    version = 1
    
    while True:
        if filetype == "docx":
            filename = f"Рекомендации_по_характеристикам_серверов_{organization}_v{version}.docx" 
            file_path = os.path.join(app.config['REPORT_FOLDER'], filename)
        elif filetype == "drawio":
            filename = f"{organization}_v{version}.drawio"
            file_path = os.path.join(app.config['SCHEME_FOLDER'], filename)
        elif filetype == "png":
            filename = f"{organization}_v{version}.png"
            file_path = os.path.join(app.config['SCHEME_FOLDER'], filename)
        elif filetype == "xml":
            filename = f"{organization}_v{version}.xml"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        else:
            raise ValueError(f"Unsupported file type: {filetype}")
            
        if not os.path.exists(file_path):
            return file_path, filename
        version += 1

def generate_heading(redundancy, lk_users, concurrent_users, organization):
    if lk_users == 0:
        if redundancy == "true":
            heading = f"Рекомендации по характеристикам серверов для {organization} для одновременной работы {concurrent_users} пользователей «Directum RX» c обеспечением отказоустойчивости"
        else:
            heading = f"Рекомендации по характеристикам серверов для {organization} для одновременной работы {concurrent_users} пользователей «Directum RX» без обеспечения отказоустойчивости"
    else:
        if redundancy == "true":
            heading = f"Рекомендации по характеристикам серверов для {organization} для одновременной работы {concurrent_users} пользователей «Directum RX» и {lk_users} пользователей  «Личный кабинет» c обеспечением отказоустойчивости"
        else:
            heading = f"Рекомендации по характеристикам серверов для {organization} для одновременной работы {concurrent_users} пользователей «Directum RX» и {lk_users} пользователей  «Личный кабинет» без обеспечения отказоустойчивости"
    return heading
