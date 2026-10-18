import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from calculator import calculate
from server import Handler


def plan(weapon='satchel', **row):
    return dict(weapon=weapon, rows=[dict(target='metal-door', quantity=1, **row)])


class CalculationTests(unittest.TestCase):
    def test_sheet_door_resources(self):
        result = calculate(plan())
        self.assertEqual([result[k] for k in ('amount', 'sulfur', 'powder', 'charcoal')], [4, 1920, 960, 2880])

    def test_explosive_ammo_recipe_per_round(self):
        result = calculate(plan('explosive-ammo'))
        self.assertEqual(result['amount'], 63)
        self.assertEqual(result['sulfur'], 1575)
        self.assertEqual(result['powder'], 630)

    def test_beans(self):
        self.assertEqual(calculate(plan('bean'))['amount'], 18)

    def test_individual_rounding_and_soft_side(self):
        result = calculate(dict(weapon='pickaxe', rows=[dict(target='stone-wall', quantity=3, side='soft', damage=17)]))
        self.assertEqual(result['amount'], 90)
        self.assertIsNone(result['sulfur'])

    def test_partial_health(self):
        self.assertIsNone(calculate(plan(hp=125))['amount'])
        self.assertEqual(calculate(plan(hp=125, damage=60))['amount'], 3)

    def test_unknown_and_zero_damage(self):
        self.assertIsNone(calculate(plan('gas'))['amount'])
        self.assertIsNone(calculate(plan('rocket', damage=0))['amount'])

    def test_custom_recipe(self):
        payload = plan('custom', damage=100)
        payload['resources'] = dict(sulfur=20, powder=5)
        result = calculate(payload)
        self.assertEqual((result['amount'], result['sulfur'], result['charcoal']), (3, 60, 45))

    def test_invalid_inputs(self):
        for payload in [None, {}, dict(weapon='missing', rows=[]), dict(weapon='rocket', rows=[]), plan(damage='NaN'), plan(damage=-1), plan(hp=99999), plan(side='unknown')]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                calculate(payload)
        for quantity in [True, 0, 1.2, 1001]:
            payload = plan()
            payload['rows'][0]['quantity'] = quantity
            with self.assertRaises(ValueError):
                calculate(payload)


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_static_and_catalog(self):
        for path in ['/', '/style.css', '/app.js', '/api/catalog']:
            with urlopen(self.base + path) as response:
                self.assertEqual(response.status, 200)
                self.assertTrue(response.read())
        with urlopen(self.base + '/api/catalog') as response:
            self.assertGreater(len(json.load(response)['weapons']), 40)

    def test_post_calculation(self):
        request = Request(self.base + '/api/calculate', json.dumps(plan()).encode(), {'Content-Type': 'application/json'})
        with urlopen(request) as response:
            self.assertEqual(json.load(response)['amount'], 4)

    def test_invalid_json_and_private_files(self):
        for path in ['/server.py', '/.git/config', '/../calculator.py']:
            with self.assertRaises(HTTPError) as caught:
                urlopen(self.base + path)
            self.assertEqual(caught.exception.code, 404)
        with self.assertRaises(HTTPError) as caught:
            urlopen(Request(self.base + '/api/calculate', b'invalid'))
        self.assertEqual(caught.exception.code, 400)


if __name__ == '__main__':
    unittest.main()
