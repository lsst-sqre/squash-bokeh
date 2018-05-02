import os
import sys
from datetime import datetime

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

        self.message = str()

        self.empty = {'job_id': [], 'time': [], 'date_created': [],
                      'value': [], 'ci_id': [], 'ci_url': [], 'count': [],
                      'package_names': [], 'git_urls': []}

        self.cds = ColumnDataSource(data=self.empty)

        self.args = self.parse_args()

        self.validate_inputs()

        self.load_data(self.selected_dataset,
                       self.selected_metric,
                       self.selected_period)

    def parse_args(self):

        args = self.doc.session_context.request.arguments

        parsed_args = {}
        for key in args:
            parsed_args[key] = args[key][0].decode("utf-8")

        return parsed_args

    def validate_inputs(self):

        # Datasets
        self.datasets = self.get_datasets(default="validation_data_cfht",
                                          ignore=["decam", "unknown"])

        if 'ci_dataset' in self.args:
            self.selected_dataset = self.args['ci_dataset']
        else:
            self.selected_dataset = self.datasets['default']

        # Verification Packages
        self.packages = self.get_packages(default='validate_drp')

        if 'package' in self.args:
            self.selected_package = self.args['package']
        else:
            self.selected_package = self.packages['default']

        # Metrics
        self.metrics = self.get_metrics(package=self.selected_package,
                                        default='validate_drp.AM1')

        if 'metric' in self.args:
            self.selected_metric = self.args['metric']
        else:
            self.selected_metric = self.metrics['default']

        self.metrics_meta = self.get_metrics_meta(self.selected_package)

        # Period
        self.periods = {'periods': ['All', 'Last Year', 'Last 6 Months',
                                    'Last Month'],
                        'default': 'Last 6 Months'}

        if 'period' in self.args:
            self.selected_period = self.args['period']
        else:
            self.selected_period = self.periods['default']

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
        else:
            self.cds.data = self.empty

    def set_title(self, title):
        self.doc.title = title

    def add_layout(self, layout):
        self.doc.add_root(layout)
