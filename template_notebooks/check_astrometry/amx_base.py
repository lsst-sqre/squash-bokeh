import os
import sys

import numpy as np

from bokeh.models import ColumnDataSource

from api_helper import APIHelper # noqa

import requests


INFLUXDB_API_URL = "https://influxdb-demo.lsst.codes"
INFLUXDB_DATABASE = "squash-demo"

def get_squash_data(run_id, package='validate_drp'):

    query = 'SELECT "squash_id", "run_id", "filter", "dataset" FROM "{}\"."autogen"."{}" WHERE "run_id"=\'{}\''.format(INFLUXDB_DATABASE, package, run_id)

    params={'q': query}
    r = requests.post(url=INFLUXDB_API_URL + "/query", params=params)

    result = {'timestamp':[], 'squash_id':[], 'filter':[], 'dataset':[]}
    id_map = {}
    for record in r.json()['results'][0]['series'][0]['values']:
        result['timestamp'].append(record[0])
        result['squash_id'].append(record[1])
        result['filter'].append(record[3])
        result['dataset'].append(record[4])
        id_map[(record[4], record[3])] = record[1]
    return result, id_map


class BaseApp(APIHelper):

    # Dataset used by this app
    DATASET_NAME = "MatchedMultiVisitDataset"

    # App parameters
    SNR_CUT = 100

    # example metric to use to retrieve data
    METRIC = "validate_drp.AM1"

    # Example URL query string taken from an actual SQUaSH session.
    # ?job_id=1967&metric=validate_drp.AM1&ci_id=1453&ci_dataset=validation_data_hsc

    def __init__(self, job_id):
        super().__init__()

        jobs, id_map = get_squash_data(str(job_id))

        self.jobs = jobs
        self.id_map = id_map

        self.job_id = job_id

        self.message = str()

        self.validate_inputs()

        self.cds = ColumnDataSource(data={'snr': [], 'dist': []})
        self.selected_cds = ColumnDataSource(data={'snr': [], 'dist': []})

        self.load_data()

    def validate_inputs(self):
        """Make sure input parameters are valid."""

        # default dataset and filter
        self.datasets = sorted(list(set(self.jobs['dataset'])))

        self.selected_dataset = self.datasets[0]
        self.filters = [self.jobs['filter'][i] for i in range(len(self.jobs['filter']))
                        if self.jobs['dataset'][i] == self.selected_dataset]
        self.selected_filter = self.filters[0]
        self.squash_id = self.id_map[(self.selected_dataset, self.selected_filter)]

        # default snr cut
        self.snr_cut = BaseApp.SNR_CUT

    def load_data(self):
        """Load the data blobs from the SQuaSH API for
        the the selected job
        """

        squash_id = self.id_map[(self.selected_dataset, self.selected_filter)]

        # e.g. /blob/885?metric=validate_drp.AM1&name=MatchedMultiVisitDataset
        df = self.get_api_data_as_pandas_df(endpoint='blob', item=squash_id,
                                            params={'metric':BaseApp.METRIC, 'name': BaseApp.DATASET_NAME})

        snr = []
        if 'snr' in df:
            snr = df['snr']['value']

        dist = []
        if 'dist' in df:
            dist = df['dist']['value']

        # Full dataset
        self.cds.data = {'snr': snr, 'dist': dist}

        # Select objects with SNR > 100
        index = np.array(snr) > float(self.snr_cut)

        selected_snr = np.array(snr)[index]
        selected_dist = np.array(dist)[index]

        self.selected_cds.data = {'snr': selected_snr,
                                  'dist': selected_dist}

    def set_title(self, title):
        """Set the app title.
        """
        self.doc.title = title
