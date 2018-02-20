import os
import pandas as pd
import requests


class APIHelper:

    # The URL for the SQuaSH RESTful API
    SQUASH_API_URL = os.environ.get('SQUASH_API_URL',
                                    'http://localhost:5000')

    def __init__(self):
        self.session = requests.Session()
        self.session.mount('https://',
                           requests.adapters.HTTPAdapter(max_retries=5))

    def sublist(self, list1, list2):
        return set(list1) <= set(list2)

    def get_api_endpoint_urls(self):
        """Lookup for SQuaSH API endpoints and return the
        corresponding URLs

        Return
        ------
        endpoint_urls: dict
            a dict with API endpoints and URLs
        """
        endpoint_urls = None
        try:
            r = self.session.get(APIHelper.SQUASH_API_URL)
            endpoint_urls = r.json()
        except requests.exceptions.RequestException as e:
            print(e)

        return endpoint_urls

    def get_api_data(self, endpoint, params=None):
        """Return data from an SQuaSH API endpoint as a python
        dictionary.

        Parameters
        ----------
        endpoint: str
            an endpoint in the SQuaSH API
            see https://sqr-009.lsst.io/#documentation
        params: dict
            a query parameter available for this endpoint
            and its value.

        Return
        ------
        data: dict
            a python dictionary with the content returned
            from the API.
        """
        endpoint_urls = self.get_api_endpoint_urls()

        data = None
        if endpoint_urls:
            try:
                r = self.session.get(endpoint_urls[endpoint],
                                     params=params)
                data = r.json()
            except requests.exceptions.RequestException as e:
                print(e)

        return data

    def get_api_data_as_pandas_df(self, endpoint, params=None):
        """Return data from a SQuaSH API endpoint as a pandas
        dataframe.

        Parameters
        ----------
        endpoint: str
            an endpoint in the SQuaSH API
            see https://sqr-009.lsst.io/#documentation
        params: dict
            a query parameter available for this endpoint
            and its value.

        Return
        ------
        df: pandas dataframe
            a pandas dataframe with the contend returned
            from the API.
        """
        data = self.get_api_data(endpoint, params)

        df = pd.DataFrame()
        if data:
            df = pd.DataFrame.from_dict(data, orient='index').transpose()

        return df

    def get_packages(self, default=None):
        """Get a list of packages from the SQuaSH API.

        Parameters
        ----------
        default: str
            the default package to be used.

        Return
        ------
        packages : list
            list of package names.
        default : str
            the default package, if the default package
            provided as parameter is valid then use that
            instead of the default package obtained from
            the API.
        """
        packages = self.get_api_data('packages')['packages']

        default_package = None

        if packages:
            sorted_packages = sorted(packages, key=str.lower)
            default_package = sorted_packages[0]

            if default and default in sorted_packages:
                default_package = default

        return {'packages': sorted_packages,
                'default': default_package}

    def get_datasets(self, default=None):
        """Get a list of datasets from the SQuaSH API.

        Parameters
        ----------
        default: str
            the default dataset to be used.

        Return
        ------
        datasets : list
            list of dataset names.
        default : str
            the default dataset, if the default dataset
            provided as parameter is valid then use that
            instead of the default dataset obtained from
            the API.
        """
        datasets = self.get_api_data('datasets')['datasets']

        default_dataset = None

        if datasets:
            sorted_datasets = sorted(datasets, key=str.lower)
            default_dataset = sorted_datasets[0]

            if default and default in datasets:
                default_dataset = default

        return {'datasets': sorted_datasets,
                'default': default_dataset}

    def get_metrics(self, package):
        """Get a list of metric objects for a given
        verification package and return a dict indexed
        by the metric name

        Parameters
        ----------
        package: str
            name of the verification package, e.g. `validate_drp`

        Return
        ------
        metrics : list
            a list of metric objects associated to this package
        """
        data = self.get_api_data('metrics',
                                 params={'package': package})

        metrics = dict()

        for metric in data['metrics']:
            metrics[metric['name']] = metric

        return metrics

    def get_specs(self, metric, default=None):
        """Get the list of specification names for a given
        metric.

        Parameters
        ----------
        metric: str
            a full qualified metric name, e.g. `validate_drp.AM1`
        default: str
            a full qualified name for the metric specification to
            be used as default, e.g. `validate_drp.AM1.minimum_gri`

        Return
        ------
        specs: list
            list of specification names
        default: str
            the default specification, if the the default specification
            provided as parameter is valid then use it instead of the
            default specification obtained from the API
        """
        data = self.get_api_data('specs', params={'metric': metric})['specs']

        specs = []
        default_spec = None

        if data:
            specs = [s['name'] for s in data]
            default_spec = specs[0]

            if default and default in specs:
                default_spec = default

        return {'specs': specs, 'default': default_spec}