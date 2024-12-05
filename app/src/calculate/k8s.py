import math
def calculate_kubernetes(kubernetes):
    """
    Расчет узлов k8s.

    Parameters:
    kubernetes (str): Входные данные.

    Returns: k8s_count, k8s_cpu, k8s_ram, k8s_hdd 
    """
    if kubernetes.lower() == "true":
        k8s_count = 1
        k8s_cpu = 4
        k8s_ram = 4
        k8s_hdd = 50
    else:
        k8s_count = 0
        k8s_cpu = 0
        k8s_ram = 0
        k8s_hdd = 0
    return k8s_count, k8s_cpu, k8s_ram, k8s_hdd