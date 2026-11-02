import unittest
import monitor

class HistoryTests(unittest.TestCase):
    def test_retains_previous_check_and_appends_new_sample(self):
        old = {'서비스': {'is_up': True, 'status': 200, 'latency_ms': 10, 'last_check': '이전'}}
        result = {'name': '서비스', 'url': 'https://example.com', 'category': '테스트', 'is_up': True, 'status': 200, 'latency_ms': 20}
        updated = monitor.handle_alerts([result], old)['서비스']
        self.assertEqual([sample['latency_ms'] for sample in updated['samples']], [10, 20])
        self.assertEqual(updated['url'], result['url'])

if __name__ == '__main__':
    unittest.main()
