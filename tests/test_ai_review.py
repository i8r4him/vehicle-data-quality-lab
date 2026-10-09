import copy
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from vehicle_data_quality.ai_review import RULES, cases, prompt, run, validate_response
from vehicle_data_quality.database import ROOT


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.items = cases()
        self.response = json.loads((ROOT / 'examples/ai-response.json').read_text())

    def test_cases_come_from_real_validation(self):
        self.assertEqual([item['case_id'] for item in self.items], list(RULES))
        self.assertEqual([len(item['findings']) for item in self.items], [1, 2, 1, 1, 1])
        self.assertEqual(self.items[0]['findings'][0]['row_number'], 4)
        self.assertIn('Erfinde keine Preise', prompt(self.items))

    def test_complete_response_is_accepted_but_remains_pending(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run(directory, ROOT / 'examples/ai-response.json')
            review = json.loads((Path(directory) / 'review.json').read_text())
            self.assertEqual(result['structural_checks'], 'passed')
            self.assertEqual(review['human_review'], 'pending')
            self.assertEqual(len(review['suggestions']), 5)

    def test_missing_duplicate_unknown_or_untyped_cases_are_rejected(self):
        variants = [self.response['suggestions'][:-1], self.response['suggestions'] * 2]
        for identifier in ['UNKNOWN', [], None]:
            value = copy.deepcopy(self.response['suggestions'])
            value[0]['case_id'] = identifier
            variants.append(value)
        for entries in variants:
            with self.assertRaises(ValueError):
                validate_response({'suggestions': entries}, self.items)

    def test_unreviewed_actions_and_extra_fields_are_rejected(self):
        for key, value in [('needs_human_review', False), ('needs_human_review', 1),
                           ('sql', 'UPDATE offers SET price_cents=1'), ('explanation', '')]:
            response = copy.deepcopy(self.response)
            response['suggestions'][0][key] = value
            with self.assertRaises(ValueError):
                validate_response(response, self.items)

    def test_invalid_response_writes_no_review(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'bad.json'
            source.write_text('{"suggestions": []}')
            with self.assertRaises(ValueError):
                run(Path(directory) / 'result', source)
            self.assertFalse((Path(directory) / 'result/review.json').exists())

    def test_prepare_does_not_claim_an_ai_run(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run(directory)
            self.assertEqual(result['structural_checks'], 'not run')
            self.assertTrue((Path(directory) / 'prompt.txt').is_file())
            self.assertFalse((Path(directory) / 'review.json').exists())

    def test_bpmn_nodes_flows_and_diagram_references_are_complete(self):
        namespaces = {'b': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
                      'di': 'http://www.omg.org/spec/BPMN/20100524/DI'}
        root = ET.parse(ROOT / 'docs/vehicle-data-review.bpmn').getroot()
        process = root.find('b:process', namespaces)
        elements = {element.get('id'): element for element in process}
        flows = process.findall('b:sequenceFlow', namespaces)
        for flow in flows:
            source, target = flow.get('sourceRef'), flow.get('targetRef')
            self.assertIn(source, elements)
            self.assertIn(target, elements)
            self.assertIn(flow.get('id'), [item.text for item in elements[source].findall('b:outgoing', namespaces)])
            self.assertIn(flow.get('id'), [item.text for item in elements[target].findall('b:incoming', namespaces)])
        for gate in process.findall('b:exclusiveGateway', namespaces):
            branches = [flow for flow in flows if flow.get('sourceRef') == gate.get('id')]
            self.assertEqual({flow.get('name') for flow in branches}, {'Ja', 'Nein'})
            self.assertIn(gate.get('default'), {flow.get('id') for flow in branches})
        graphics = root.find('di:BPMNDiagram/di:BPMNPlane', namespaces)
        self.assertEqual({item.get('bpmnElement') for item in graphics}, set(elements))


if __name__ == '__main__':
    unittest.main()
