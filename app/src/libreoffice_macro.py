import sys
sys.path.append("/usr/lib/python3/dist-packages")
sys.path.append("/usr/lib/libreoffice/program")

# Инициализируем окружение UNO
import uno

# Импортируем необходимые компоненты
from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK
from com.sun.star.text import XTextContent
from com.sun.star.beans import PropertyValue

def update_table_of_contents(doc_path):
    # Получаем локальный контекст
    local_context = uno.getComponentContext()
    
    # Создаем UNO менеджер соединений
    resolver = local_context.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_context)
    
    try:
        # Подключаемся к запущенному процессу LibreOffice
        context = resolver.resolve(
            "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
        desktop = context.ServiceManager.createInstanceWithContext(
            "com.sun.star.frame.Desktop", context)
        
        # Открываем документ
        doc = desktop.loadComponentFromURL(
            uno.systemPathToFileUrl(doc_path), "_blank", 0, ())
        
        # Получаем все индексы в документе
        indexes = doc.getDocumentIndexes()
        
        # Обновляем каждый индекс
        for i in range(indexes.getCount()):
            index = indexes.getByIndex(i)
            if index.supportsService("com.sun.star.text.ContentIndex"):
                index.update()
        
        # Сохраняем и закрываем документ
        doc.store()
        doc.close(True)
        
    except Exception as e:
        print(f"Ошибка при обновлении оглавления: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python libreoffice_macro.py <путь_к_документу>", file=sys.stderr)
        sys.exit(1)
    
    update_table_of_contents(sys.argv[1])
