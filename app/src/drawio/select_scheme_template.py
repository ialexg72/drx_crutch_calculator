import os
from flask import current_app

app = current_app

def select_scheme_template(redundancy: str, operating_system: str, kubernetes: str, lk_users: int, concurrent_users: int, ario: str) -> str:
    """
    Selects the appropriate scheme template based on the specified parameters.

    Args:
        redundancy (str): Whether redundancy is enabled.
        operating_system (str): The operating system being used.
        kubernetes (str): Whether Kubernetes is being used.
        lk_users (int): The number of users in the LK HR Pro.
        concurrent_users (int): The number of concurrent users.

    Returns: 
        str: The path to the selected scheme template.
    """
    base_path = current_app.config['TEMPLATE_SCHEMES']

    if kubernetes.lower() == "true" and ario.lower() == "true":
        return os.path.join(base_path, 'kubernetes-ario.drawio')
    if kubernetes.lower() == "true":
        return os.path.join(base_path, 'kubernetes.drawio')

    if operating_system.lower() == 'linux':
        if redundancy.lower() == "true":
            if lk_users > 0 and concurrent_users > 499:
                return os.path.join(base_path, 'ha-hrpro.drawio')
            elif lk_users > 0 and concurrent_users <= 499:
                return os.path.join(base_path, 'pg-ha-lk-noms.drawio')
            else:
                return os.path.join(base_path, 'ha.drawio' if concurrent_users > 499 else 'ha-noms.drawio')
        else:
            if lk_users > 0:
                return os.path.join(base_path, 'standalone-lk.drawio')
            else:
                return os.path.join(base_path, 'standalone.drawio')
    elif operating_system.lower() == 'windows':
        return os.path.join(base_path, 'ha-ms.drawio' if redundancy.lower() == "true" else 'standalone.drawio')