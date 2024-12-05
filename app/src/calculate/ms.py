import math
def calculate_ms(redundancy, concurrent_users):
    if concurrent_users > 499:
        def calculate_ms_count(concurrent_users, redundancy):
            if concurrent_users > 500:
                ms_count = math.ceil(concurrent_users / 2500)
                return ms_count + 1 if redundancy.lower() == "true" else ms_count
            return 0
        def round_up_to_even(value):
            return value if value % 2 == 0 else value + 1
        def calculate_ms_cpu(concurrent_users, ms_count, redundancy):
            if concurrent_users < 1001:
                result = 6
            elif redundancy.lower() == "true":
                result = math.ceil(concurrent_users / (ms_count - 1) / 500) * 2
            else:
                result = math.ceil(concurrent_users / ms_count / 500) * 2
            return result
        def calculate_ms_ram(concurrent_users, ms_count, redundancy):
            if concurrent_users == 0 or ms_count == 0:
                return 0
            if concurrent_users < 1501:
                return 12
            divider = ms_count - 1 if redundancy.lower() == "true" else ms_count
            if redundancy.lower() == "true" and ms_count <= 1:
                raise ValueError("webserver_count должно быть больше 1, если redundancy равно 'Да'.")
            temp = math.ceil(concurrent_users / divider / 1000)
            value = temp * 6
            return value if value % 2 == 0 else value + 1
        def calculate_ms_hdd(concurrent_users):
            return 100 if concurrent_users > 500 else 0
    else:
        ms_count = 0
        ms_cpu = 0
        ms_ram = 0
        ms_hdd = 0
    return ms_count, ms_cpu, ms_ram, ms_hdd