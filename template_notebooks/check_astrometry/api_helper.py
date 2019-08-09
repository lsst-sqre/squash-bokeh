import os
import pandas as pd
import requests


class APIHelper:

    def __init__(self):

        self.session = requests.Session()
        self.session.mount('https://',
                           requests.adapters.HTTPAdapter(max_retries=5))
        self.squash_api_url = 'https://squash-restful-api.lsst.codes'


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
        r = self.session.get(self.squash_api_url)

        endpoint_urls = r.json()


        return endpoint_urls

    def get_api_data(self, endpoint, item=None, params=None):
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

        url = endpoint_urls[endpoint]

        if item:
            url = "{}/{}".format(url, item)

        data = None
        if endpoint_urls:
            try:
                r = self.session.get(url, params=params)
                data = r.json()
            except requests.exceptions.RequestException as e:
                print(e)

        return data

    def get_api_data_as_pandas_df(self, endpoint, item=None, params=None):
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
        data = self.get_api_data(endpoint, item, params)

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
        sorted_packages = []

        if packages:
            sorted_packages = sorted(packages, key=str.lower)
            default_package = sorted_packages[0]

            if default and default in sorted_packages:
                default_package = default

        return {'packages': sorted_packages,
                'default': default_package}

    def get_datasets(self, default=None, ignore=None):
        """Get a list of datasets from the SQuaSH API.

        Parameters
        ----------
        default: str
            the default dataset to be used.

        Return
        ------
        datasets: list
            list of dataset names.
        default: str
            the default dataset, if the default dataset
            provided as parameter is valid then use that
            instead of the default dataset obtained from
            the API.
        ignore: list
            list of dataset names to remove from the list
            of datasets returned from the SQuaSH API
        """
        datasets = self.get_api_data('datasets')['datasets']

        default_dataset = None

        if datasets:

            if ignore:
                datasets = [dataset for dataset in datasets
                            if dataset not in ignore]

            sorted_datasets = sorted(datasets, key=str.lower)

            default_dataset = sorted_datasets[0]

            if default and default in datasets:
                default_dataset = default

        return {'datasets': sorted_datasets,
                'default': default_dataset}

    def get_metrics(self, package, default=None):
        """Get a list of metrics for a given
        verification package from the SQuaSH API

        Parameters
        ----------
        package: str
            name of the verification package, e.g. `validate_drp`

        default: str
            the default metric to be used.

        Return
        ------
        metrics : list
            a list of metric objects associated to this package
        """
        data = self.get_api_data('metrics',
                                 params={'package': package})

        metrics = [metric['name'] for metric in data['metrics']]

        sorted_metrics = metrics
        default_metric = None

        if metrics:
            sorted_metrics = sorted(metrics, key=str.lower)
            default_metric = sorted_metrics[0]

            if default and default in metrics:
                default_metric = default

        return {'metrics': sorted_metrics,
                'default': default_metric}

    def get_metrics_meta(self, package):
        """Returns a dict index by metric name with
        metric metadata for a give package

        Parameters
        ----------
        package: str
            name of the verification package, e.g. `validate_drp`

        Return
        ------
        metrics meta: dict
            a dict indexed by metric name
        """

        data = self.get_api_data('metrics',
                                 params={'package': package})

        return {metric['name']: metric for metric in data['metrics']}

    def get_specs(self, dataset_name, filter_name, metric):
        """Get the list of specification names for a given
        metric.

        Parameters
        ----------
        dataset_name: str
            name of the dataset, e.g. `validation_data_hsc`
        filter_name: str
            name of filter, e.g. `r`
        metric: str
            a full qualified metric name, e.g. `validate_drp.AM1`
        Return
        ------
        specs: list
            list of specification names
        thresholds: list
            list of threshold values
        """
        data = self.get_api_data('specs',
                                 params={'metric': metric,
                                         'dataset_name': dataset_name,
                                         'filter_name': filter_name})

        specs = data['specs']

        if not specs:
            # relax constraint on filter_name
            data = self.get_api_data('specs',
                                     params={'metric': metric,
                                             'dataset_name': dataset_name})
            specs = data['specs']

        names = []
        thresholds = []

        def pretty(s):
            return s.replace(metric + ".", "").replace("_", " ").lower()

        if specs:
            names = [pretty(s['name']) for s in specs]
            thresholds = [t['threshold']['value'] for t in specs]

        return {'names': names, 'thresholds': thresholds}
