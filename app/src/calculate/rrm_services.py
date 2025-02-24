import math
def calculate_rrm(redundancy, concurrent_users):
    """
    Calculate the number of RRM nodes, CPU, RAM, and HDD.
    Parameters:
    redundancy (str): Whether redundancy is enabled.
    concurrent_users (int): The number of concurrent users.
    Returns:
    int: The number of RRM nodes.
    int: The number of CPU cores.
    int: The amount of RAM in GB.
    int: The amount of HDD in GB.
    """
    if redundancy.lower() == "true":
        rrm_node_count = 0 if concurrent_users < 501 else 1
        rrm_node_count += 2 if redundancy.lower() == "true" else 0
        rrm_cpu = 0
        if rrm_node_count > 0:
            if concurrent_users < 5001:
                rrm_cpu = 2
            elif concurrent_users > 10000:
                rrm_cpu = 6
            else:
                rrm_cpu = 4
        rrm_ram = 0
        if rrm_node_count > 0:
            if concurrent_users < 5001:
                rrm_ram = 2
            elif concurrent_users > 10000:
                rrm_ram = 6
            else:
                rrm_ram = 4

        rrm_hdd = 0 if rrm_node_count == 0 else 50
    else:
        rrm_node_count = 0
        rrm_cpu = 0
        rrm_ram = 0
        rrm_hdd = 0
    return rrm_node_count, rrm_cpu, rrm_ram, rrm_hdd

