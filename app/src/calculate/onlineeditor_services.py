import math
def calculate_online_editor(online_editor, concurrent_users):
    if online_editor.lower() != "none":
        editor_count = 1
        editor_hdd = 50
        def calculate_cpu(concurrent_users):
            value = 2 if math.ceil(concurrent_users * 0.2) < 200 else math.floor((concurrent_users * 0.2) / 200) * 2
            return value if value % 2 == 0 else value + 1
        def calculate_ram(concurrent_users):
            value = 4 if math.ceil(concurrent_users * 0.2) < 200 else math.floor((concurrent_users * 0.2) / 200) * 2 + 2
            return value if value % 2 == 0 else value + 1
        editor_cpu = calculate_cpu(concurrent_users)
        editor_ram = calculate_ram(concurrent_users)
    else:
        editor_count = 0
        editor_cpu = 0
        editor_ram = 0
        editor_hdd = 0
    return editor_count, editor_cpu, editor_ram, editor_hdd