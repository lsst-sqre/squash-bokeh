import os
import pandas as pd
import requests
from bokeh.models import Span, Label


SQUASH_API_URL = os.environ.get('SQUASH_API_URL', None)

def get_api_endpoint_urls():
    """
    Return lookup for api endpoints and urls
    """

    api = None
    if SQUASH_API_URL:
        r = requests.get(SQUASH_API_URL)
        r.raise_for_status()
        api = r.json()

    return api


def get_data(endpoint, params=None):
    """Return data as a dict from
    an API endpoint """

    api = get_api_endpoint_urls()

    data = None
    if api:
        r = requests.get(api[endpoint],
                         params=params)
        r.raise_for_status()
        data = r.json()

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


def get_url_args(doc, defaults=None):
    """Return url args recovered from bokeh document.
    Defaults values can be provided.
    """

    return {'metric': 'None', 'ci_dataset': 'None',
            'ci_id': 'None', 'snr_cut': '0'}


def add_span_annotation(plot, value, text, color):
    """ Add span annotation, used for metric specification
    thresholds.
    """

    span = Span(location=value, dimension='width',
                line_color=color, line_dash='dotted',
                line_width=2)

    label = Label(x=plot.plot_width-300, y=value+0.5, x_units='screen',
                  y_units='data', text=text, text_color=color,
                  text_font_size='11pt', text_font_style='normal',
                  render_mode='canvas')

    plot.add_layout(span)
    plot.add_layout(label)


