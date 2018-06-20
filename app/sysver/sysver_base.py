import os
import sys

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource

# This is needed to import the api_helper module
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.append(os.path.join(BASE_DIR))
from api_helper import APIHelper # noqa


class BaseApp(APIHelper):

    # Metrics associated with this app
    METRICS = ["sysver.CameraBodySurfaceTemp"]

    def __init__(self):
        super().__init__()
        self.doc = curdoc()
        self.args = self.parse_args()
        self.message = str()
        self.validate_inputs()
        self.cds = ColumnDataSource(data={'body_position': [], 'body_angle': [], 'temperatures': []})
        self.load_data(self.job_id, self.selected_metric)

    def load_data(self, job_id, metric):
        """Load the data blobs from the SQuaSH API for
        the the selected job
        """
        print("Job ID:", job_id)
        df = self.get_api_data_as_pandas_df(endpoint='blob', item=job_id,
                                            params={'metric': metric,
                                                    'name': metric})

        temperatures = []
        if 'cameraBody_temperature_grid' in df:
            temperatures = df['cameraBody_temperature_grid']['value']

        positions = []
        if 'cameraBody_positions' in df:
            positions = df['cameraBody_positions']['value']

        angles = []
        if 'cameraBody_angles' in df:
            angles = df['cameraBody_angles']['value']

        self.cds.data = {'temperatures': temperatures, 'body_angle': angles, 'body_position': positions}

        # Get average temperature from job data
        self.metric_value = {}
        job_data = self.get_api_data(endpoint='job', item=job_id)
        measurements = job_data['measurements']
        for measurement in measurements:
            if measurement['metric'] == metric:
                self.metric_value['value'] = measurement['value']
                self.metric_value['units'] = measurement['unit']

    def parse_args(self):
        """Returns a dictionary with the URL parameters
        used to configure the app.

        See https://bokeh.pydata.org/en/latest/docs/user_guide/
        server.html#accessing-the-http-request
        """
        args = self.doc.session_context.request.arguments

        parsed_args = {}
        for key in args:
            parsed_args[key] = args[key][0].decode("utf-8")

        return parsed_args

    def set_title(self, title):
        """Set the app title.
        """
        self.doc.title = title

    def validate_inputs(self):
        """Make sure input parameters are valid."""

        # default metric
        self.selected_metric = BaseApp.METRICS[0]
        print("G:", self.args)
        if 'metric' in self.args:
            metric = self.args['metric']
            if metric in BaseApp.METRICS:
                self.selected_metric = metric
            else:
                self.message = "<strong>{}</strong> metric is invalid "\
                               "for this app, using <strong>{}</strong> "\
                               "instead.".format(metric, self.selected_metric)

        self.job_id = None

        if 'job_id' in self.args:
            self.job_id = self.args['job_id']
        else:
            self.message = "Missing job_id in the URL query parameters."
