import os
import pandas as pd
import requests
from furl import furl

from requests.adapters import HTTPAdapter

# the default url works for local tests of the api
SQUASH_API_URL = os.environ.get('SQUASH_API_URL',
                                'http://localhost:8000')

s = requests.Session()
s.mount('https://', HTTPAdapter(max_retries=5))


def get_api_endpoint_urls():
    """
    Return lookup for api endpoints and urls
    """

    api = None
    try:
        r = s.get(SQUASH_API_URL)
        api = r.json()
    except requests.exceptions.RequestException as e:
        print(e)

    return api


def get_data(endpoint, params=None):
    """Return data as a dict from
    an API endpoint """

    api = get_api_endpoint_urls()

    data = None
    if api:
        try:
            r = s.get(api[endpoint],
                      params=params)
            data = r.json()
        except requests.exceptions.RequestException as e:
            print(e)

    return data


def get_data_as_pandas_df(endpoint, params=None):
    """
    Return a pandas dataframe from an API endpoint
    """

    data = get_data(endpoint, params)

    df = pd.DataFrame()
    if data:
        df = pd.DataFrame.from_dict(data, orient='index').transpose()

    return df


def get_datasets(default=None):
    """Get a list of datasets from the API
    and a default value
    Returns
    -------
    datasets : list
        list of dataset names
    default : str
        if a valid default value is provided, overwrite
        the default value obtained from the API
    """

    data = get_data('datasets')

    datasets = []
    default_dataset = None

    if data:
        datasets = data
        default_dataset = get_data('defaults')['ci_dataset']

        if default:
            if default in datasets:
                default_dataset = default

    return {'datasets': datasets, 'default': default_dataset}


def get_metrics(default=None):
    """Get the list of metrics from the API
    and a default value
    Returns
    -------
    metrics : list
        list of metric names
    default : str
        if a valid default value is provided, overwrite
        the default value returned from the API
    """

    data = get_data('metrics')

    metrics = []
    default_metric = None

    if data:
        metrics = [m['metric'] for m in data]
        default_metric = get_data('defaults')['metric']

        if default:
            if default in metrics:
                default_metric = default

    return {'metrics': metrics, 'default': default_metric}


def get_value(specs, name):
    """ Helper function to unpack metric specification
    values
    Parameters
    ----------
    specs: dict
        a dict with keys value and name
    name: str
        the spec name
    Return
    ------
    value: float or None
        value of the spec if exists, None otherwise
    """

    value = None

    for s in specs:
        if s['name'] == name:
            value = s['value']
            break

    return value


def get_specs(metric):
    """Get metric specifications thresholds
    from its name
    Parameters
    ----------
    metric: str
        a valid metric name
    Returns
    -------
    unit: str
        metric unit
    description:
        metric description
    minimum: float
        metric minimum specification
    design: float
        metric design specification
    stretch: float
        metric stretch goal
    """

    data = get_data('metrics')

    unit = str()
    description = str()
    specs = []

    minimum = None
    design = None
    stretch = None

    if data:
        for m in data:
            if m['metric'] == metric:
                unit = m['unit']
                description = m['description']
                specs = eval(str(m['specs']))
                break

        if specs:
            minimum = get_value(specs, 'minimum')
            design = get_value(specs, 'design')
            stretch = get_value(specs, 'stretch')

    return {'unit': unit, 'description': description,
            'minimum': minimum, 'design': design, 'stretch': stretch}


def get_url_args(doc, defaults=None):
    """Return url args recovered from django_full_path cookie in
    the bokeh request header.

    If defaults values are provided, overwrite the default values
    obtained from the API
    """

    args = None
    data = get_data('defaults')

    if data:
        args = data
        # overwrite api default values
        if defaults:
            for key in defaults:
                args[key] = defaults[key]

        r = doc().session_context.request

        try:
            if 'squash_dash_full_path' in r.cookies:
                django_full_path = r.cookies['django_full_path'].value
                tmp = furl(django_full_path).args
                for key in tmp:
                    # overwrite default values with those passed
                    # as url args, make sure the url arg (key) is valid
                    if key in args:
                        args[key] = tmp[key]

                # the bokeh app name is the second segment of the url path
                args['bokeh_app'] = furl(django_full_path).path.segments[1]
        except AttributeError as e:
                print(e)

    return args
