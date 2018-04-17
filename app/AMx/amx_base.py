import os
import sys

import numpy as np

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource

# This is needed to import the api_helper module
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.append(os.path.join(BASE_DIR))
from api_helper import APIHelper # noqa


class BaseApp(APIHelper):

    # Dataset used by this app
    DATASET = "MatchedMultiVisitDataset"

    # Metrics associated with this app
    METRICS = ["validate_drp.AM1", "validate_drp.AM2"]

    # App parameters
    SNR_CUT = 100

    def __init__(self):
        super().__init__()
        self.doc = curdoc()
        self.args = self.parse_args()

        self.message = str()

        self.validate_inputs()

        self.cds = ColumnDataSource(data={'snr': [], 'dist': []})
        self.selected_cds = ColumnDataSource(data={'snr': [], 'dist': []})

        self.load_data(self.job_id, self.selected_metric, self.snr_cut)

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

    def validate_inputs(self):
        """Make sure input parameters are valid."""

        # default metric
        self.selected_metric = BaseApp.METRICS[0]

        if 'metric' in self.args:
            metric = self.args['metric']
            if metric in BaseApp.METRICS:
                self.selected_metric = metric
            else:
                self.message = "<strong>{}</strong> metric is invalid "\
                               "for this app, using <strong>{}</strong> "\
                               "instead.".format(metric, self.selected_metric)
        # default snr cut
        self.snr_cut = BaseApp.SNR_CUT

        # TODO: get a list of valid jobs, use latest as default
        self.job_id = None

        if 'job_id' in self.args:
            self.job_id = self.args['job_id']
        else:
            self.message = "Missing job_id in the URL query parameters."

        self.ci_id = None
        if 'ci_id' in self.args:
            self.ci_id = self.args['ci_id']

        self.ci_dataset = None
        if 'ci_dataset' in self.args:
            self.ci_dataset = self.args['ci_dataset']

    def load_data(self, job_id, metric, snr_cut):
        """Load the data blobs from the SQuaSH API for
        the the selected job
        """

        # e.g. /blob/885?metric=validate_drp.AM1&name=MatchedMultiVisitDataset
        df = self.get_api_data_as_pandas_df(endpoint='blob', item=job_id,
                                            params={'metric': metric,
                                                    'name': BaseApp.DATASET})

        snr = []
        if 'snr' in df:
            snr = df['snr']['value']

        dist = []
        if 'dist' in df:
            dist = df['dist']['value']

        # Full dataset
        self.cds.data = {'snr': snr, 'dist': dist}

        # Select objects with SNR > 100
        index = np.array(snr) > float(snr_cut)

        selected_snr = np.array(snr)[index]
        selected_dist = np.array(dist)[index]

        self.selected_cds.data = {'snr': selected_snr,
                                  'dist': selected_dist}

    def set_title(self, title):
        """Set the app title.
        """
        self.doc.title = title
