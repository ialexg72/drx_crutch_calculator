import math
def calculate_lk(redundancy, lk_users, concurrent_users):
    if lk_users == 0:
        return (0, 0, 0, 0, 0, 0, 0, 0)
    hdd = 50
    if redundancy.lower() == "true" or concurrent_users > 5000:
        node_count = 3
    elif concurrent_users > 75000:
        node_count = 5
    else:
        node_count = 1
    if node_count == 1:
        cpu = 6
        ram = 12 if lk_users < 1000 else 18
    else:
        cpu = 4 if lk_users < 50000 else 6
        ram = 8 if lk_users < 50000 else 12
    if lk_users > 4999:
        additional_nodes = math.ceil(lk_users / 20000)
        additional_cpu = math.ceil(lk_users / additional_nodes / 3500) * 2
        additional_ram = math.ceil(lk_users / additional_nodes / 3500) * 4
        additional_hdd = 100
    else:
        additional_nodes = 0
        additional_cpu = 0
        additional_ram = 0
        additional_hdd = 0
    return (
        node_count, cpu, ram, hdd,
        additional_nodes, additional_cpu, additional_ram, additional_hdd
    )