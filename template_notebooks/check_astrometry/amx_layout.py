import numpy as np

from bokeh.models import Span, Label, Slider
from bokeh.models.widgets import Select, Div, Button
from bokeh.models.ranges import Range1d
from bokeh.models.glyphs import Circle

from bokeh.layouts import widgetbox, row, column
from bokeh.plotting import figure

from amx_base import BaseApp


class Layout(BaseApp):
    """Define the widgets and the app layout.
    """
    # Default sizes for widgets
    SMALL = 175
    MEDIUM = 350
    LARGE = 1000
    XLARGE = 3000

    # Slider parameters
    MIN_SNR = 0
    MAX_SNR = 500
    SNR_STEP = 10

    # Histogram parameters
    NBINS = 100

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.make_input_widgets()
        self.make_header()
        self.make_scatter_plot()
        self.make_histogram()
        self.make_layout()

    def make_input_widgets(self):
        """Selection widgets

        See Bokeh docs for all available widgets
        https://bokeh.pydata.org/en/latest/docs/user_guide/interaction/
        widgets.html
        """

        self.datasets_widget = Select(title="Dataset:",
                                    value=self.selected_dataset,
                                    options=self.datasets)

        self.filters_widget = Select(title="Filter:",
                                    value=self.selected_filter,
                                    options=self.filters)

        self.plot_widget = Button(label="Plot", button_type='success')

        self.snr_slider = Slider(start=Layout.MIN_SNR, end=Layout.MAX_SNR,
                                 value=float(self.snr_cut),
                                 step=Layout.SNR_STEP, title="SNR")

    def update_filters_widget(self):
        self.filters = [self.jobs['filter'][i] for i in range(len(self.jobs['filter']))
                        if self.jobs['dataset'][i] == self.selected_dataset]

        self.filters_widget.options = self.filters
        self.selected_filter = self.filters[0]
        self.filters_widget.value = self.selected_filter


    def make_header(self):
        """Header area for the app, include a title and
        a generic message."""

        self.header_widget = Div()
        self.update_header()

    def update_header(self):
        title = "Astrometry health check plots based on " \
                "<strong>{}</strong> dataset in the <strong>{}</strong> bandpass " \
                "by CI ID <strong>{}</strong>" \
                "</h2>".format(self.selected_dataset, self.selected_filter,
                               self.job_id)

        message = "<p style='color:red;'>{}</p>".format(self.message)

        self.header_widget.text = "{}{}".format(message, title)

    def make_scatter_plot(self):
        """Scatter plot `SNR vs. distance`, with a span
        annotation showing the current SNR cut.
        """

        self.plot = figure(tools="pan, box_zoom, wheel_zoom, reset",
                           active_scroll="wheel_zoom", x_axis_type="log",
                           y_axis_location="left", x_axis_label="SNR",
                           y_axis_label="d [marcsec]")

        self.plot.y_range = Range1d(0, 100)

        self.scatter = self.plot.circle('snr', 'dist', size=5, fill_alpha=0.2,
                                   source=self.cds, color='lightgray',
                                   line_color=None)

        self.scatter.nonselection_glyph = Circle(fill_color='lightgray',
                                            line_color=None)

        self.selected_scatter = self.plot.circle('snr', 'dist', size=5,
                                            fill_alpha=0.2,
                                            line_color=None,
                                            source=self.selected_cds)

        # default bokeh color #1f77b4 (blue)
        self.selected_scatter.nonselection_glyph = Circle(fill_color="#1f77b4",
                                                     fill_alpha=0.2,
                                                     line_color=None)

        # Add plot annotations
        self.snr_span = Span(location=float(self.snr_cut), dimension='height',
                             line_color='black', line_dash='dashed',
                             line_width=3)

        self.plot.add_layout(self.snr_span)

        text = 'SNR > {:3.2f}'.format(self.snr_span.location)

        self.snr_label = Label(x=275, y=375, x_units='screen',
                               y_units='screen',
                               text=text,
                               render_mode='css')

        self.plot.add_layout(self.snr_label)

    def make_histogram(self):

        # Full histogram
        frequencies, self.edges = np.histogram(self.cds.data['dist'],
                                               bins=Layout.NBINS)

        hmax = max(frequencies) * 1.1

        self.hist = figure(tools="ypan, ywheel_zoom, reset",
                           active_scroll="ywheel_zoom",
                           y_axis_location='right',
                           output_backend="webgl")

        self.hist.x_range = Range1d(0, hmax)

        # Link scatter plot and histogram
        self.hist.y_range = self.plot.y_range

        # TODO: move to theme.yaml
        self.hist.ygrid.grid_line_color = None

        self.full_hist = self.hist.quad(left=0, bottom=self.edges[:-1], top=self.edges[1:],
                                        right=frequencies, color="lightgray",
                                        line_color="lightgray")

        # Selected histogram
        frequencies, _ = np.histogram(self.selected_cds.data['dist'],
                                      bins=self.edges)

        self.selected_hist = self.hist.quad(left=0, bottom=self.edges[:-1],
                                            top=self.edges[1:],
                                            right=frequencies)

        # Median
        median = np.median(self.selected_cds.data['dist'])

        text = 'Median = {:3.2f} marcsec'.format(median)
        self.median_label = Label(x=150, y=350, x_units='screen',
                                  y_units='screen',
                                  text=text,
                                  render_mode='css')

        self.hist.add_layout(self.median_label)

        # RMS
        rms = np.sqrt(np.mean(np.square(self.selected_cds.data['dist'])))

        text = "RMS = {:3.2f} marcsec".format(rms)

        self.rms_label = Label(x=150, y=325, x_units='screen',
                               y_units='screen', text=text,
                               render_mode='css')

        self.hist.add_layout(self.rms_label)

        # N
        n = self.selected_cds.to_df().size

        self.n_label = Label(x=150, y=375, x_units='screen', y_units='screen',
                             text='N = {}'.format(n), render_mode='css')

        self.hist.add_layout(self.n_label)

        self.rms_span = Span(location=rms, dimension='width',
                             line_color="black", line_dash='dashed',
                             line_width=3)

        self.hist.add_layout(self.rms_span)


    def make_layout(self):
        """Make the app layout
        """
        dataset = widgetbox(self.datasets_widget, width=Layout.SMALL)
        filt = widgetbox(self.filters_widget, width=Layout.SMALL)
        plot = widgetbox(self.plot_widget)
        header = widgetbox(self.header_widget, width=Layout.LARGE)
        slider = widgetbox(self.snr_slider, width=Layout.LARGE)

        self.layout = column(
                        row(dataset, filt),
                        plot,
                        header,
                        slider,
                        row(self.plot, self.hist))
