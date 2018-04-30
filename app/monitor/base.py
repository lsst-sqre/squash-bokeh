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

        self.empty = {'time': [],
                      'date_created': [],
                      'value': []}

        self.cds = ColumnDataSource(data=self.empty)

        self.args = self.parse_args()

        self.validate_inputs()

        self.load_data(self.selected_metric,
                       self.selected_period)

    def parse_args(self):

        args = self.doc.session_context.request.arguments

        parsed_args = {}
        for key in args:
            parsed_args[key] = args[key][0].decode("utf-8")

        return parsed_args

    def validate_inputs(self):

        # Verification Packages
        self.packages = self.get_packages(default='demo1')

        if 'package' in self.args:
            self.selected_package = self.args['package']
        else:
            self.selected_package = self.packages['default']

        # Metrics
        self.metrics = self.get_metrics(package=self.selected_package,
                                        default='demo1.ZeropointRMS')

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

    def load_data(self, selected_metric, selected_period):

        self.load_measurements(selected_metric, selected_period)

        self.update_datasource()

    def load_measurements(self, metric, period):

        self.measurements = self.get_api_data_as_pandas_df(
            endpoint='monitor',
            params={'metric': metric,
                    'period': period})

        # Add datetime object in addition to string representation
        time = [datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ")
                for x in self.measurements['date_created']]

        self.measurements['time'] = time

    def update_datasource(self):
        """ Create a bokeh column data source for the
        selected dataset and period
        """
        if self.measurements.size > 0:
            self.cds.data = self.measurements.to_dict(orient='list')
        else:
            self.cds.data = self.empty

    def set_title(self, title):
        self.doc.title = title

    def add_layout(self, layout):
        self.doc.add_root(layout)
