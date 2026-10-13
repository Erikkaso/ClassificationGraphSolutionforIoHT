import xmltodict
import json
from Utilitarios import Constants

def convert_xml_to_json(xml: str, fileName = Constants.graphName) -> str:
    """
    Converte uma string XML para JSON formatado.
    
    Args:
        xml_content (str): Conteúdo XML em texto.
    
    Returns:
        str: JSON formatado (indentado).
    """
    try:
        file = open(xml, "r")
        xml_data = file.read()
        # Converte XML em dicionário Python
        dict_data = xmltodict.parse(xml_data)

        #path json
        path = Constants.pathProjectDownloads
        feedFile = path+"\\"+fileName+".json"
        print(feedFile)
        
        # Converte dicionário em JSON
        json_data = json.dumps(dict_data, indent=2, ensure_ascii=False)

        with open(feedFile, 'w', encoding="utf-8") as f2: 
            f2.write(json_data)
        f2.close()
        
        return feedFile
    except Exception as e:
        raise ValueError(f"Erro ao converter XML para JSON: {e}")