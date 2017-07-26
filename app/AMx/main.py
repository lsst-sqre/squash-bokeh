import os
import sys
import numpy as np

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Span, Label, Slider
from bokeh.models.widgets import Div
from bokeh.models.glyphs import Circle
from bokeh.plotting import figure
from bokeh.layouts import row, column, widgetbox

BOKEH_BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.append(BOKEH_BASE_DIR)

from helper import get_url_args, get_data_as_pandas_df, add_span_annotation # noqa

# Get url query args
args = get_url_args(curdoc, defaults={'metric': 'AM1'})


# App title
title = Div(text="""<h2>{metric} plot for {ci_dataset} dataset from
                    CI job {ci_id}</h2>""".format_map(args))

# Get data
data = get_data_as_pandas_df(endpoint='apps',
                             params=args)

# Configure bokeh data sources with the full and
# selected data sets


snr = {'value': [], 'label': '', 'unit': ''}
selected_snr = []

dist = {'value': [], 'label': '', 'unit': ''}
selected_dist = []

if not data.empty:
    snr = data['matchedDataset']['snr']
    index = np.array(snr['value']) > float(args['snr_cut'])
    selected_snr = np.array(snr['value'])[index]

    dist = data['matchedDataset']['dist']
    index = np.array(snr['value']) > float(args['snr_cut'])
    selected_dist = np.array(dist['value'])[index]


full = ColumnDataSource(data={'snr': snr['value'], 'dist': dist['value']})
selected = ColumnDataSource(data={'snr': selected_snr, 'dist': selected_dist})

# Ranges used in the bokeh widgets
MIN_SNR = 0
MAX_SNR = 500
SNR_STEP = 1
MIN_DIST = 0
MAX_DIST = 100

# SNR slider
snr_slider = Slider(start=MIN_SNR, end=MAX_SNR, value=float(args['snr_cut']),
                    step=SNR_STEP, title="SNR")

# Scatter plot
x_axis_label = snr['label']

y_axis_label = "{label} [{unit}]".format_map(dist)

plot = figure(tools="pan, box_zoom, wheel_zoom, reset",
              active_scroll="wheel_zoom",
              y_range=(MIN_DIST, MAX_DIST), y_axis_location='left',
              x_axis_label=x_axis_label, x_axis_type='log',
              y_axis_label=y_axis_label)

# TODO: move size, fill alpha and line_color to plot styling configuration

scatter = plot.circle('snr', 'dist', size=5, fill_alpha=0.2,
                      source=full, color='lightgray',
                      line_color=None)

scatter.nonselection_glyph = Circle(fill_color='lightgray',
                                    line_color=None)

partial_scatter = plot.circle('snr', 'dist', size=5, fill_alpha=0.2,
                              line_color=None, source=selected)

# default bokeh blue color #1f77b4
partial_scatter.nonselection_glyph = Circle(fill_color="#1f77b4",
                                            fill_alpha=0.2,
                                            line_color=None)

# Add annotations to the scatter plot
# TODO: improve variable naming

span1 = Span(location=float(args['snr_cut']), dimension='height',
             line_color='black', line_dash='dashed', line_width=3)

plot.add_layout(span1)

label1 = Label(x=285, y=425, x_units='screen', y_units='screen',
               text='SNR > {:3.2f}'.format(span1.location),
               render_mode='css')

plot.add_layout(label1)

# Full histogram

full_hist, edges = np.histogram(full.data['dist'], bins=100)

hmax = max(full_hist) * 1.1

hist = figure(tools="ypan, ywheel_zoom, reset",
              active_scroll="ywheel_zoom",
              x_range=(0, hmax),
              y_axis_location='right',
              y_range=plot.y_range)

hist.ygrid.grid_line_color = None

hist.quad(left=0, bottom=edges[:-1], top=edges[1:], right=full_hist,
          color="lightgray", line_color='lightgray')

# Partial histogram

partial_hist, _ = np.histogram(selected.data['dist'],
                               bins=edges)

histogram = hist.quad(left=0, bottom=edges[:-1], top=edges[1:],
                      right=partial_hist)

# Add annotations to the histograms
n = len(selected.data['dist'])
median = np.median(selected.data['dist'])
rms = np.sqrt(np.mean(np.square(selected.data['dist'])))

label2 = Label(x=200, y=400, x_units='screen', y_units='screen',
               text='Median = {:3.2f} marcsec'.format(median),
               render_mode='css')

hist.add_layout(label2)

label3 = Label(x=200, y=375, x_units='screen', y_units='screen',
               text='RMS = {:3.2f} marcsec'.format(rms), render_mode='css')

hist.add_layout(label3)

label4 = Label(x=200, y=425, x_units='screen', y_units='screen',
               text='N = {}'.format(n), render_mode='css')

hist.add_layout(label4)

span2 = Span(location=rms,
             dimension='width', line_color="black",
             line_dash='dashed', line_width=3)

hist.add_layout(span2)

# TODO: obtain spec thresholds from the API

add_span_annotation(plot=hist, value=20, text="Minimum", color="red")
add_span_annotation(plot=hist, value=10, text="Design", color="blue")
add_span_annotation(plot=hist, value=5, text="Stretch", color="green")


# Callbacks
def update(attr, old, new):

    snr_cut = snr_slider.value

    # Update the selected sample

    # TODO: Use pandas notation here
    index = np.array(full.data['snr']) > float(snr_cut)

    # Update the bokeh data source in one step to avoid a warning
    # re mismatch in length of column data source columns

    tmp = dict(snr=np.array(full.data['snr'])[index],
               dist=np.array(full.data['dist'])[index])

    selected.data = tmp

    # Redraw the partial histogram
    partial_hist, _ = np.histogram(selected.data['dist'],
                                   bins=edges)

    histogram.data_source.data['right'] = partial_hist

    # Recompute n, median and rms
    n = len(selected.data['dist'])
    median = np.median(selected.data['dist'])
    rms = np.sqrt(np.mean(np.square(selected.data['dist'])))

    # Update span anotations
    span1.location = snr_cut
    span2.location = rms

    # Update labels
    label1.text = 'SNR > {:3.2f}'.format(snr_cut)
    label2.text = 'Median = {:3.2f} marcsec'.format(median)
    label3.text = 'RMS = {:3.2f} marcsec'.format(rms)
    label4.text = 'N = {}'.format(n)


snr_slider.on_change('value', update)

# App layout

if data.empty:
    layout = column(widgetbox(title, width=900),
                    widgetbox(Div(text="""<h4>No data to display.</h4>"""),
                              width=900))
else:
    layout = row(column(widgetbox(title, width=900),
                        widgetbox(snr_slider, width=900),
                        row(plot, hist)))

curdoc().add_root(layout)
curdoc().title = "SQuaSH"
