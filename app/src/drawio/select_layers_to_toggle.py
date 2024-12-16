def main(
    nomad_count,
    elasticsearch_count,
    ario_count,
    onlineeditor_count,
    monitoring_count,
    dcs_count
):
    layers_to_toggle = []
    if nomad_count > 0:
        layers_to_toggle.append("NOMAD")
    if elasticsearch_count > 0:
        layers_to_toggle.append("ELASTIC")
    if ario_count > 0:
        layers_to_toggle.append("ARIO")
    if onlineeditor_count > 0:
        layers_to_toggle.append("ONLINEEDITOR")
    if monitoring_count > 0:
        layers_to_toggle.append("MONITORING")
    if dcs_count > 0:
        layers_to_toggle.append("DCS")
    return layers_to_toggle