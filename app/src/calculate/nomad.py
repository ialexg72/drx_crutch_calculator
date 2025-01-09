import math
import src.utility as utility
def calculate_nomad(redundancy, mobileusers):
    if mobileusers > 50:
        #Расчет ЦПУ
        def calculate_nomad_count(mobileusers, redundancy):
            if redundancy.lower() == "true":
                result = math.ceil(mobileusers / 1000) + 1
            else:
                result = math.ceil(mobileusers / 1000)
            return result
        nomad_count = calculate_nomad_count(mobileusers, redundancy)
        def calculate_nomad_cpu(mobileusers, redundancy, nomad_count):
            if redundancy.lower() == "true":
                temp_result = math.ceil(mobileusers / (nomad_count - 1) / 150) * 2 + 2
            else:
                temp_result = math.ceil(mobileusers / nomad_count / 150) * 2 + 2  
            result = utility.round_up_to_even(temp_result)
            return result
        nomad_cpu = calculate_nomad_cpu(mobileusers, redundancy, nomad_count)
        def calculate_nomad_ram(mobileusers, redundancy, nomad_count):
            if redundancy.lower() == "true":
                result = math.ceil(mobileusers / (nomad_count - 1) / 50 * 1.5 + 2)
            else:
                result = math.ceil(mobileusers / nomad_count / 50 * 1.5 + 2)
            if utility.round_up_to_even(result):
                return result
            else:
                return result + 1
        nomad_ram = calculate_nomad_ram(mobileusers, redundancy, nomad_count)
        nomad_hdd = 100
    else:
        nomad_count = 0
        nomad_cpu = 0
        nomad_ram = 0
        nomad_hdd = 0
    return nomad_count, nomad_cpu, nomad_ram, nomad_hdd
