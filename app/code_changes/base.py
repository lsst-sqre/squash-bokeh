import os
import sys
import pandas as pd

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.append(os.path.join(BASE_DIR))
from api_helper import APIHelper  # noqa


class BaseApp(APIHelper):

    def __init__(self):
        super().__init__()
        self.doc = curdoc()

        self.message = str()

        self.empty = {'job_id': [], 'time': [], 'date_created': [],
                      'value': [], 'formatted_value': [], 'ci_id': [],
                      'ci_url': [], 'count': [], 'filter_name': [],
                      'color': [], 'package_names': [], 'git_urls': []}

        self.cds = ColumnDataSource(data=self.empty)

        self.args = self.parse_args()

        self.validate_inputs()

        self.load_data()

    def parse_args(self):

        args = self.doc.session_context.request.arguments

        parsed_args = {}
        for key in args:
            parsed_args[key] = args[key][0].decode("utf-8")

        return parsed_args

    def get_dataset_filters(self, dataset):

        dataset_filters = {'validation_data_cfht': ['r'],
                           'validation_data_hsc': ['HSC-R', 'HSC-I', 'HSC-Y'],
                           'HSC RC2': ['HSC-G', 'HSC-R', 'HSC-I', 'HSC-Z',
                                       'HSC-Y', 'NB0921'],
                           'CI-HiTS2015': ['g']}

        return dataset_filters[dataset]

    def validate_inputs(self):

        # Datasets
        self.datasets = self.get_datasets(default="validation_data_cfht",
                                          ignore=["decam", "unknown"])

        if 'ci_dataset' in self.args:
            self.selected_dataset = self.args['ci_dataset']
        else:
            self.selected_dataset = self.datasets['default']

        # Filters
        # TODO filter should be a dataset property see DM-15317
        # self.filters = self.get_filters()

        self.filters = self.get_dataset_filters(self.selected_dataset)

        self.selected_filter = self.filters[0]

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

    def load_data(self):

        self.load_measurements()
        self.load_code_changes()
        self.update_datasource()

    def load_code_changes(self):

        self.code_changes = self.get_api_data_as_pandas_df(
            endpoint='code_changes',
            params={'ci_dataset': self.selected_dataset,
                    'filter_name': self.selected_filter,
                    'period': self.selected_period})

    @staticmethod
    def get_filter_color(filter_name):
        """Assign a color based on the filter_name. Unknown filters
        will be displayed in gray."""

        color = 'gray'

        if filter_name is None:
            return color

        name = filter_name.lower()

        if 'u' in name:
            color = 'magenta'
        elif 'g' in name:
            color = 'blue'
        elif 'r' in name:
            color = 'green'
        elif 'i' in name:
            color = 'gold'
        elif 'z' in name:
            color = 'orange'
        elif 'y' in name:
            color = 'red'

        return color

    def load_measurements(self):

        df = self.get_api_data_as_pandas_df(
            endpoint='monitor',
            params={'ci_dataset': self.selected_dataset,
                    'filter_name': self.selected_filter,
                    'metric': self.selected_metric,
                    'period': self.selected_period})

        # Add datetime objects from the string representation
        df['time'] = pd.to_datetime(df['date_created'],
                                    format="%Y-%m-%dT%H:%M:%SZ",
                                    utc=True)

        df['date_created'] = [x.replace('T', ' ').replace('Z', ' ')
                              for x in df['date_created']]

        # Assign a color for the selected_filter
        color = self.get_filter_color(self.selected_filter)

        df['color'] = [color] * len(df['time'])

        # DM-14376
        # for displaying the five most significant digits
        formatted_value = ["{0:.5g}".format(value)
                           for value in df['value']]

        df['formatted_value'] = formatted_value

        self.measurements = df

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
        """ Merge measurements and code_changes, and
        create a bokeh column data source
        """

        if self.measurements.size > 0:

            if self.code_changes.size > 0:
                # Add packages and count columns
                df = self.measurements.merge(self.code_changes,
                                             on='ci_id', how='inner')

                # Replace NaN with zeros in count
                df['count'] = df['count'].fillna(0)

                # Add list of package names and git urls
                package_data = self.format_package_data(df['packages'])

                df['package_names'], df['git_urls'] = package_data

                self.cds.data = df.to_dict(orient='list')
            else:
                self.cds.data = self.measurements.to_dict(orient='list')
        else:
            self.cds.data = self.empty

    def set_title(self, title):
        self.doc.title = title

    def add_layout(self, layout):
        self.doc.add_root(layout)
