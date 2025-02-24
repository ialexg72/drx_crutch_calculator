def calculate_ario(operationsystem, ario_document_count, ario):
    ario = ario.lower()
    if ario != "true":
        return (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    os = operationsystem.lower()

    # Определение конфигурации ресурсов для ario и dtes на основе операционной системы
    resource_config = {
        "linux": {
            "ario": {
                25000: (4, 20),
                55000: (8, 24),
                90000: (12, 40),
                150000: (10, 14),
                250000: (16, 24)
            },
            "dtes": {
                150000: (10, 28),
                250000: (16, 48)
            }
        },
        "windows": {
            "ario": {
                25000: (4, 10),
                55000: (8, 12),
                90000: (12, 20),
                150000: (10, 14),
                250000: (16, 24)
            },
            "dtes": {
                150000: (10, 14),
                250000: (16, 24)
            }
        }
    }

    # Инициализируем дефолтные значения
    ario_count = 1 if ario == "true" else 0
    ario_hdd = 100 if ario == "true" else 0
    ario_cpu = 0
    ario_ram = 0
    dtes_count = 0
    dtes_hdd = 0
    dtes_cpu = 0
    dtes_ram = 0
    ansible_count = 0
    ansible_cpu = 0
    ansible_ram = 0
    ansible_hdd = 0

    if ario == "true":
        # Определяем русурсы для Арио
        ario_ranges = resource_config[os]["ario"]
        for threshold, (cpu, ram) in sorted(ario_ranges.items()):
            if ario_document_count <= threshold:
                ario_cpu = cpu
                ario_ram = ram
                break

        # Определяем русурсы для Дтес
        if ario_document_count > 90000:
            dtes_ranges = resource_config[os]["dtes"]
            dtes_count = 1
            dtes_hdd = 100
            for threshold, (cpu, ram) in sorted(dtes_ranges.items()):
                if ario_document_count <= threshold:
                    dtes_cpu = cpu
                    dtes_ram = ram
                    break

        # Добавляем ноду с ансиб если установка на линукс распределенная
        if dtes_count > 0 and os == "linux":
            ansible_count = 1
            ansible_cpu = 2
            ansible_ram = 2
            ansible_hdd = 50

    return (
        ario_count, ario_cpu, ario_ram, ario_hdd,
        dtes_count, dtes_cpu, dtes_ram, dtes_hdd,
        ansible_count, ansible_cpu, ansible_ram, ansible_hdd)