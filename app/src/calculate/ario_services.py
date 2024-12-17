def calculate_ario(operationsystem, ario_document_count, ario):
    ario_count = 0
    ario_cpu = 0
    ario_ram = 0
    ario_hdd = 0
    dtes_count = 0
    dtes_cpu = 0
    dtes_ram = 0
    dtes_hdd = 0
    if ario.lower() == "true":
        if operationsystem.lower() == "linux":
            ario_count = 1
            ario_hdd = 100
            if ario_document_count <= 25000:
                ario_cpu = 4
                ario_ram = 20
            elif ario_document_count <= 55000:
                ario_cpu = 8
                ario_ram = 24
            elif ario_document_count <= 90000:
                ario_cpu = 12
                ario_ram = 40
            elif ario_document_count <= 150000:
                ario_cpu = 10
                ario_ram = 14
            elif ario_document_count <= 250000:
                ario_cpu = 16
                ario_ram = 24
            if ario_document_count > 90000:
                dtes_count = 1
                dtes_hdd = 100
                if ario_document_count <= 150000:
                    dtes_cpu = 10
                    dtes_ram = 28
                elif ario_document_count <= 250000:
                    dtes_cpu = 16
                    dtes_ram = 48
        if operationsystem.lower() == "windows":
            ario_count = 1
            ario_hdd = 100
            if ario_document_count <= 25000:
                ario_cpu = 4
                ario_ram = 10
            elif ario_document_count <= 55000:
                ario_cpu = 8
                ario_ram = 12
            elif ario_document_count <= 90000:
                ario_cpu = 12
                ario_ram = 20
            elif ario_document_count <= 150000:
                ario_cpu = 10
                ario_ram = 14
            elif ario_document_count <= 250000:
                ario_cpu = 16
                ario_ram = 24
            if ario_document_count > 90000:
                dtes_count = 1
                dtes_hdd = 100
                if ario_document_count <= 150000:
                    dtes_cpu = 10
                    dtes_ram = 14
                elif ario_document_count <= 250000:
                    dtes_cpu = 16
                    dtes_ram = 24
    return (
        ario_count, ario_cpu, ario_ram, ario_hdd, 
        dtes_count, dtes_cpu, dtes_ram, dtes_hdd
    )