import math
import src.utility as utility
def calculate_webserver(concurrent_users, redundancy):
    if concurrent_users > 0:
        count = math.ceil(concurrent_users / 2500)
    webserver_count = count + 1 if redundancy.lower() == "true" else count

    if concurrent_users == 0 or webserver_count == 0:
        ws_cpu = 0
    elif concurrent_users < 501:
        ws_cpu = 6
    else:
        divider = webserver_count - 1 if redundancy.lower() == "true" else webserver_count
        if redundancy.lower() == "true" and webserver_count <= 1:
            raise ValueError("При redundancy='true' значение webserver_count должно быть больше 1.")
        temp = math.ceil(concurrent_users / divider / 500)
        ws_cpu = temp * 2 + 2       
    webserver_cpu = utility.round_up_to_even(ws_cpu)
    
    if concurrent_users == 0:
        ws_ram = 0
    elif concurrent_users < 501:
        ws_ram = 14
    elif concurrent_users < 2501:
        ws_ram = 12
    else:
        divider = webserver_count - 1 if redundancy.lower() == "true" else webserver_count
        if redundancy.lower() == "true" and webserver_count <= 1:
            raise ValueError("webserver_count должно быть больше 1, если redundancy равно 'Да'.")
        ceil_value = math.ceil(concurrent_users / divider / 500)
        ws_ram = ceil_value * 2 + 2
    webserver_ram = ws_ram if ws_ram % 2 == 0 else ws_ram + 1
    
    if webserver_count != 0:
        webserver_hdd = 100
    else:
        webserver_hdd = 0
    return webserver_count, webserver_cpu, webserver_ram, webserver_hdd