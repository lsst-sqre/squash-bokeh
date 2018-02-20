import unittest
from app.api_helper import APIHelper

class TestAPIHelper(unittest.TestCase):
    """Test the API helper functions used in squash bokeh, the tests
    below make sure the functions run and the API returns
    consistent results.

    Note:
    -----
        It assumes the SQuaSH API is running at SQUASH_API_URL.
    """
    def setUp(self):

        self.APIHelper = APIHelper()
        self.default_msg = "It looks like you don't have enough data in " \
                   "the SQuaSH API."

    def test_get_datasets(self):

        # test invalid default as input
        datasets = self.APIHelper.get_datasets(default='foo')

        # must return a valid default
        default_dataset = datasets['default']

        self.assertIsNot(default_dataset, None, msg=self.default_msg)
        self.assertIn(default_dataset, datasets['datasets'])


    def test_get_packages(self):

        # test invalid default as input
        packages = self.APIHelper.get_packages(default='foo')

        # must return a valid default
        default_package = packages['default']

        self.assertIsNot(default_package, None, msg=self.default_msg)
        self.assertIn(default_package, packages['packages'])

    def test_get_metrics(self):

        packages = self.APIHelper.get_packages()
        default_package = packages['default']

        metrics = self.APIHelper.get_metrics(package=default_package)
