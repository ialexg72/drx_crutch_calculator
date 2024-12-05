import math
def calculate_reverseproxy(redundancy, concurrent_users):
    """
    Calculate the number of reverse proxy nodes, CPU, RAM, and HDD.

    Parameters:
    redundancy (str): Whether redundancy is enabled.
    concurrent_users (int): The number of concurrent users.

    Returns:
    int: The number of reverse proxy nodes.
    int: The number of CPU cores.
    int: The amount of RAM in GB.
    int: The amount of HDD in GB.
    """
    if concurrent_users > 500 or redundancy.lower() == "true":
        if concurrent_users == 0:
            count = 0
        else:
            if redundancy.lower() == "true":
                count = 2
            else:
                count = 1
        cpu = concurrent_users / 5000
        cpu = math.ceil(cpu) * 2
        ram = concurrent_users / 5000
        ram = math.ceil(ram) * 2
        if ram % 2 != 0:
            ram += 1
        hdd = 50
        return count, cpu, ram, hdd
    else:
        return 0, 0, 0, 0