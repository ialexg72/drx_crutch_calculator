from docx.table import Table, _Row, _Cell
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import docx
import re
from docx import Document
from docx.text.paragraph import Paragraph
import xml.etree.ElementTree as ET
import logging
import logging.config
from src import settings
# Импортируем настройки логирования
logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

def delete_row_from_table(table: Table, row: _Row) -> None:
    """
    Удаляет указанную строку из таблицы.

    :param table: Таблица из документа.
    :param row: Строка, которую нужно удалить.
    """
    try:
        tbl = table._tbl
        tr = row._tr
        tbl.remove(tr)
        logging.info(f"Удалена строка из таблицы: {row}")
    except Exception as e:
        logging.error(f"Ошибка при удалении строки: {e}")

def remove_specific_rows(doc, target_text: str, num_rows_to_delete: int = 5) -> None:
    """
    Удаляет строки из всех таблиц в документе, содержащие целевой текст и последующие num_rows_to_delete строк.

    :param doc_path: Путь к документу.
    :param target_text: Текст для поиска в строках.
    :param num_rows_to_delete: Количество последующих строк для удаления.
    """
    try:
        # Открываем документ)
        # Нормализуем целевой текст для регистронезависимого поиска
        normalized_target_text = target_text.lower().strip()
        logging.debug(f"Нормализованный целевой текст: '{normalized_target_text}'")

        # Проходим по всем таблицам в документе
        for table_index, table in enumerate(doc.tables, start=1):
            logging.info(f"Обработка таблицы {table_index}")
            i = 0
            while i < len(table.rows):
                row = table.rows[i]
                # Извлекаем полный текст из строки с учетом всех ячеек
                row_text = ' '.join(cell.text for cell in row.cells).lower().strip()
                logging.debug(f"Текст строки {i + 1} в таблице {table_index}: '{row_text}'")
                
                # Используем регулярное выражение для более гибкого поиска
                if re.search(re.escape(normalized_target_text), row_text):
                    logging.info(f"Найден целевой текст в таблице {table_index}, строка {i + 1}")
                    # Удаляем найденную строку и следующие num_rows_to_delete строк
                    for _ in range(num_rows_to_delete + 1):  # +1 для самой найденной строки
                        if i < len(table.rows):
                            delete_row_from_table(table, table.rows[i])
                            logging.info(f"Строка {i + 1} удалена из таблицы {table_index}")
                        else:
                            break
                    # После удаления сдвигаем индекс назад, чтобы продолжить проверку
                    i -= 1
                i += 1
    except Exception as e:
        logging.error(f"Ошибка при обработке документа: {e}")

#Функция поиска и удаления текста
def delete_paragraphs_by_text(doc, text_to_delete):
    paragraphs = doc.paragraphs
    for paragraph in paragraphs:
        if text_to_delete in paragraph.text:
            p = paragraph._element
            p.getparent().remove(p)
            p._p = p._element = None

#Функция для замены текста в шаблоне
def replace_placeholder(doc, placeholder, value):
    # Обработка параграфов
    for paragraph in doc.paragraphs:
        if placeholder in paragraph.text:
            # Объединение всех runs в одном тексте
            inline = paragraph.runs
            full_text = ''.join([run.text for run in inline])
            if placeholder in full_text:
                new_text = full_text.replace(placeholder, value)
                # Очистка существующих runs
                for run in inline:
                    run.text = ''
                # Добавление нового текста в первый run
                inline[0].text = new_text

    # Обработка таблиц
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                replace_placeholder(cell, placeholder, value)

def iter_block_items(parent):
    """
    Генератор для последовательного перебора всех блоков (абзацев и таблиц) в документе.
    
    Args:
        parent: Объект документа или ячейки таблицы.
    Yields:
        Объекты Paragraph или Table.
    """
    # Проверяем тип объекта через его класс
    if parent.__class__.__name__ == 'Document':
        parent_elm = parent.element.body
    else:
        parent_elm = parent._element
        
    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)

def get_heading_level(paragraph):
    """
    Определяет уровень заголовка абзаца.
    
    Args:
        paragraph: Объект Paragraph.
    Returns:
        int: Уровень заголовка или None, если это не заголовок.
    """
    style = paragraph.style.name
    if style.startswith('Heading'):
        try:
            return int(style.split(' ')[1])
        except (IndexError, ValueError):
            return None
    return None

def remove_heading_and_content(doc, heading_text):
    """
    Удаляет заголовок с указанным текстом и всё его содержимое до следующего заголовка того же или более высокого уровня.
    
    Args:
        doc: Объект Document из python-docx.
        heading_text: Текст заголовка, который нужно удалить.
    """
    elements_to_remove = []
    remove_mode = False
    target_level = None

    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            current_text = block.text.strip()
            current_level = get_heading_level(block)

            if remove_mode:
                if current_level is not None and current_level <= target_level:
                    remove_mode = False
                    continue
                elements_to_remove.append(block._element)
            elif current_text == heading_text:
                target_level = get_heading_level(block)
                if target_level is not None:
                    remove_mode = True
                    elements_to_remove.append(block._element)
        
        elif isinstance(block, Table) and remove_mode:
            elements_to_remove.append(block._element)

    # Удаляем все собранные элементы
    for element in elements_to_remove:
        parent = element.getparent()
        if parent is not None:
            parent.remove(element)            
