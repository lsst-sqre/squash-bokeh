import os
import sys
from datetime import datetime
import pandas as pd

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.append(os.path.join(BASE_DIR))
from api_helper import APIHelper # noqa


class BaseApp(APIHelper):
    def __init__(self):
        super().__init__()
        self.doc = curdoc()
        self.args = self.parse_args()

        self.measurements = pd.DataFrame()
        self.code_changes = pd.DataFrame()

        self.cds = ColumnDataSource(data={'time': [],
                                          'date_created': [],
                                          'value': [],
                                          'ci_id': [],
                                          'ci_url': [],
                                          'count': [],
                                          'package_names': [],
                                          'git_urls': []})

    def parse_args(self):

        args = self.doc.session_context.request.arguments

        parsed_args = {}
        for key in args:
            parsed_args[key] = args[key][0].decode("utf-8")

        return parsed_args

    def load_data(self, selected_dataset, selected_metric,
                  selected_period):

        self.load_measurements(selected_dataset,
                               selected_metric,
                               selected_period)

        self.load_code_changes(selected_dataset,
                               selected_period)

        self.update_datasource()

    def load_code_changes(self, ci_dataset, period):

        self.code_changes = self.get_api_data_as_pandas_df(
            endpoint='code_changes',
            params={'ci_dataset': ci_dataset,
                    'period': period})

    def load_measurements(self, ci_dataset, metric, period):

        self.measurements = self.get_api_data_as_pandas_df(
            endpoint='monitor',
            params={'ci_dataset': ci_dataset,
                    'metric': metric,
                    'period': period})

        # Add datetime objects from the string representation
        time = [datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ")
                for x in self.measurements['date_created']]

        self.measurements['time'] = time

    @staticmethod
    def format_package_data(packages):

        package_names = []
        git_urls = []

        for i, sublist in enumerate(packages):
            package_names.append([])
            git_urls.append([])
            # can be a list or a nan
            if type(sublist) == list:
                for package in sublist:
                    package_names[i].append(package[0])
                    git_urls[i].append("{}/commit/{}".format(
                        package[2].replace('.git', ''),
                        package[1]))

        return package_names, git_urls

    def update_datasource(self):
        """ Create a bokeh column data source for the
        selected dataset and period
        """

        # Use this empty dataframe to reset the column datasource,
        # column names must match
        df = pd.DataFrame({'time': [], 'date_created': [],
                           'value': [], 'ci_id': [], 'ci_url': [],
                           'packages': [], 'count': [], 'package_names': [],
                           'git_urls': []})

        if self.measurements.size > 0:

            # Add packages and count columns
            df = self.measurements.merge(self.code_changes,
                                         on='ci_id', how='left')

            # Replace NaN with zeros in count
            df['count'] = df['count'].fillna(0)

            # Add list of package names and git urls
            package_names, git_urls = self.format_package_data(df['packages'])

            df['package_names'] = package_names
            df['git_urls'] = git_urls

        self.cds.data = df.to_dict(orient='list')

    def set_title(self, title):
        self.doc.title = title

    def add_layout(self, layout):
        self.doc.add_root(layout)
