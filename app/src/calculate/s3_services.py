def calculate_s3_storage(s3_storage):
    if s3_storage.lower() == "false":
        cpu, ram, count = 0, 0, 0
    else:
        cpu, ram, count = 4, 4, 1
    return cpu, ram, count
