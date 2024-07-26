from datetime import datetime
import os
import time
import unittest
from core import classes

test_folder_path = 'Mock-Path-Test'
custom_filename = 'test_file.txt'


class TestFileManagement(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        current_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_path)
        file_path = os.path.join(test_folder_path, custom_filename)
        cls.testing_path = file_path

    def test_create_file(self):
        os.makedirs(test_folder_path, exist_ok=True)
        file = open(self.testing_path, 'w')
        file.close()
        self.assertTrue(True)

    def test_delete_file(self):
        time.sleep(2)
        os.remove(self.testing_path)


testDomain = 'https://mock.theccdocs.com'


class TestBuidURL(unittest.TestCase):
    url_build = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.url_build = classes.URLBuilder(testDomain)

    def test_url_with_admin_pass(self):
        expected = self.url_build
        expected.add_admin_pass('Cron', '123145')
        self.assertTrue(expected)

    def test_build_url(self):
        params = f'query_date={datetime.today().date()}&end_date={datetime.today().date()}&query_time=00:00:00&end_time=23:59:59&group[]=Main&group[]=NoShow&user_group[]=ADMIN&user_group[]=Agents&users[]=--ALL--&shift=--&DB=0&show_percentages=&live_agents=&time_in_sec=&search_archived_data=&show_defunct_users=&breakdown_by_date=&report_display_type=TEXT&stage=&file_download=1'
        expected = self.url_build.build_url(
            'vicidial/AST_agent_performance_detail.php', '', params)
        print(expected)


class TestLogger(unittest.TestCase):
    def test_create_log_file(self):
        log_file = classes.Logger('mock_log_file.txt')
        log_file.append_line('This file will be logged script processes')
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
