import math
from src import utility
def calculate_sql(redundancy, concurrent_users, lk_users):
    """
    Calculate the number of SQL nodes, CPU, RAM, and HDD.

    Parameters:
    redundancy (str): Whether redundancy is enabled.
    concurrent_users (int): The number of concurrent users.
    lk_users (int): The number of users in the LK HR Pro.

    Returns:
    int: The number of SQL nodes.
    int: The number of CPU cores.
    int: The amount of RAM in GB.
    int: The amount of HDD in GB.
    """
    sql_count = 1 if redundancy.lower() != "true" else 2
    if concurrent_users < 501:
        sql_cpu = 6 + (lk_users / 10000) * 2
    elif concurrent_users < 1500:
        sql_cpu = 8 + (lk_users / 10000) * 2
    else:
        sql_cpu = math.ceil(concurrent_users / 400) * 2 + (lk_users / 10000) * 2
    sql_cpu = math.ceil(sql_cpu)
    sql_cpu = utility.round_up_to_even(sql_cpu)
    if concurrent_users > 0 or redundancy.lower() == "true":
        if concurrent_users < 500:
            sql_ram = math.ceil(concurrent_users / 125) + 6 + (lk_users / 10000) * 4
        elif concurrent_users < 2000:
            sql_ram = 16 + (lk_users / 10000) * 4
        else:
            sql_ram = math.ceil(concurrent_users / 400) * 4 + (lk_users / 10000) * 4
    sql_ram = math.ceil(sql_ram)
    sql_ram = utility.round_up_to_even(sql_ram)
    sql_hdd = 50
    return sql_count, sql_cpu, sql_ram, sql_hdd