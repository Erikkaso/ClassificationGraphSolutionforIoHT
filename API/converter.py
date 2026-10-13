import xmltodict


def parse_xml(xml_content):
    return xmltodict.parse(
        xml_content,
        disable_entities=True,
        force_list=('EdgeSensorFeature', 'EdgeFeatureModel', 'EdgeModelsFinalStatus'),
    )
