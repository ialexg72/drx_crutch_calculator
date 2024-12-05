import math
def calculate_monitoring(monitoring, concurrent_users):
    """
    Calculate the resources required for monitoring.

    Parameters:
    monitoring (str): Whether monitoring is enabled.
    concurrent_users (int): The number of concurrent users.

    Returns:
    int: The number of monitoring nodes.
    int: The amount of HDD in GB required for monitoring.
    int: The number of CPU cores required for monitoring.
    int: The amount of RAM in GB required for monitoring.
    int: The number of logstash nodes.
    int: The amount of HDD in GB required for logstash.
    int: The number of CPU cores required for logstash.
    int: The amount of RAM in GB required for logstash.
    int: The size of the monitoring index in GB.
    """
    monitoring_count = 0
    monitoring_hdd = 0
    monitoring_cpu = 0
    monitoring_ram = 0
    logstash_count = 0
    logstash_hdd = 0
    logstash_cpu = 0
    logstash_ram = 0
    monitoring_index_size = 0
    if monitoring:
        monitoring_count = 1
        monitoring_hdd = 50
        monitoring_cpu = 16 if concurrent_users > 3000 else 8
        monitoring_ram = 32 if concurrent_users > 3000 else 16 
        monitoring_index_size = math.ceil(concurrent_users/100*30)
        if concurrent_users > 2000:
            logstash_count = 1
            logstash_hdd = 50
            logstash_cpu = 4
            logstash_ram = 6
        else: 
            logstash_hdd = 0
            logstash_cpu = 0
            logstash_ram = 0
    return (
        monitoring_count, monitoring_hdd, monitoring_cpu, monitoring_ram, 
        logstash_count, logstash_hdd, logstash_cpu, logstash_ram, 
        monitoring_index_size
    )