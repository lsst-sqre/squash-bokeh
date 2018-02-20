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
        self.args = self.parse_args()

    def parse_args(self):

        args = self.doc.session_context.request.arguments

        parsed_args = {}
        for key in args:
            parsed_args[key] = args[key][0].decode("utf-8")

        return parsed_args

    def load_monitor_data(self, dataset, period):
        """ Create a bokeh column data source for the
        selected dataset and period
        """
        df = self.get_api_data_as_pandas_df(
            endpoint='monitor',
            params={'ci_dataset': dataset, 'period': period})

        self.cds = ColumnDataSource(df)

        # we need the date_created field as python datetime
        time = [datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ")
                for x in df['date_created']]

        self.cds.data['time'] = time

    def set_title(self, title):
        self.doc.title = title

    def add_layout(self, layout):
        self.doc.add_root(layout)
