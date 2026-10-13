import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import API.app as api


XML = b'<KnowledgeRepresentation><edgeSensorFeature><EdgeSensorFeature><vSensor><typeSensor>ACC</typeSensor></vSensor></EdgeSensorFeature></edgeSensorFeature><edgeFeaturesModel/><edgeModelsFinalStatus/></KnowledgeRepresentation>'


class VisualizationApiTest(unittest.TestCase):
    def setUp(self):
        self.client = api.app.test_client()

    def test_convert_accepts_same_upload_contract_as_old_backend(self):
        response = self.client.post('/convert', data={'file': (io.BytesIO(XML), 'graph.xml')})
        self.assertEqual(response.status_code, 200)
        graph = json.loads(response.json['json_content'])['KnowledgeRepresentation']
        self.assertIsInstance(graph['edgeSensorFeature']['EdgeSensorFeature'], list)

    def test_convert_rejects_missing_file_wrong_extension_and_invalid_xml(self):
        for data in ({}, {'file': (io.BytesIO(XML), 'graph.txt')},
                     {'file': (io.BytesIO(b'<broken>'), 'graph.xml')}):
            with self.subTest(data=data):
                response = self.client.post('/convert', data=data)
                self.assertEqual(response.status_code, 400)
                self.assertIn('error', response.json)

    def test_json_graph_uses_xml_and_returns_useful_missing_file_error(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(api, 'DOWNLOAD_ROOT', Path(directory)):
            self.assertEqual(self.client.get('/GraphRequest?format=json').status_code, 404)
            Path(directory, 'KnowledgeBase.xml').write_bytes(XML)
            response = self.client.get('/GraphRequest?format=json')
            self.assertEqual(response.status_code, 200)
            self.assertIn('KnowledgeRepresentation', response.json)

    def test_model_catalog_lists_downloadable_relative_paths_only(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(api, 'MODEL_ROOT', Path(directory)):
            Path(directory, 'ANN').mkdir()
            Path(directory, 'ANN', 'model.tflite').touch()
            Path(directory, 'private.txt').touch()
            response = self.client.get('/saved_models')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['models'], ['ANN/model.tflite'])

    def test_complete_graph_uses_existing_json_export(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(api, 'DOWNLOAD_ROOT', Path(directory)):
            Path(directory, 'KnowledgeBase.xml').write_text('invalid XML')
            Path(directory, 'KnowledgeBase.json').write_text('{"KnowledgeRepresentation": {}}')
            response = self.client.get('/GraphRequest?format=json')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {'KnowledgeRepresentation': {}})

    def test_invalid_percentage_is_rejected_before_database_access(self):
        with patch.object(api, 'get_dao') as get_dao:
            for percentage in ('abc', '-1', '101'):
                response = self.client.get(f'/OptimizeGraphRequest/acc/{percentage}?format=json')
                self.assertEqual(response.status_code, 400)
            get_dao.assert_not_called()

    def test_optimized_json_uses_generated_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory, 'optimized.xml')
            artifact.write_bytes(XML)
            with patch.object(api, 'get_dao'), patch.object(api.gF, 'optimizeGraph', return_value=[[], [], []]) as optimize, patch.object(api, 'xml_create', return_value=str(artifact)):
                response = self.client.get('/OptimizeGraphRequest/acc_gyr/50?format=json')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(optimize.call_args.args[1:], (['acc', 'gyr'], 0.5))


if __name__ == '__main__':
    unittest.main()
