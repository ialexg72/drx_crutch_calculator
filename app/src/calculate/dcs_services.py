import math
def calculate_dcs(redundancy: str, dcsdochours: int):
    """
    Calculate the number of DCS nodes, CPU, RAM, and HDD.

    Parameters:
    redundancy (str): Whether redundancy is enabled.
    dcsdochours (int): The number of hours.

    Returns:
    int: The number of DCS nodes.
    int: The number of CPU cores.
    int: The amount of RAM in GB.
    int: The amount of HDD in GB.
    """
    if redundancy.lower() == "true":
        count = 1
        cpu = math.ceil(dcsdochours / 150) + 2
        ram = math.ceil(dcsdochours / 150) * 2 + 2
        if cpu % 2 == 1:
            cpu += 1
        if ram % 2 == 1:
            ram += 1
        hdd = 50
    else:
        count = 0
        cpu = 0
        ram = 0
        hdd = 0
    return count, cpu, ram, hdd