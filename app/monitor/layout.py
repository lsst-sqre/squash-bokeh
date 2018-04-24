from bokeh.models.widgets import Select, Div, RadioButtonGroup
from bokeh.layouts import widgetbox, row, column
from bokeh.plotting import Figure
from bokeh.models import HoverTool, Label

from bokeh.models.widgets import DataTable, TableColumn
from base import BaseApp


class Layout(BaseApp):
    """Define the Monitor App widgets and the Bokeh document layout.
    """
    # default sizes for widgets
    SMALL = 250
    MEDIUM = 500
    LARGE = 1000

    def __init__(self):
        super().__init__()

        self.make_input_widgets()
        self.make_header()

        self.make_plot_title()
        self.make_plot()
        self.make_footnote()
        self.make_table()

        self.make_layout()

    def make_input_widgets(self):
        """Define the widgets to select dataset, verification package,
        metrics and period
        """

        self.packages_widget = Select(title="Verification package:",
                                      value=self.selected_package,
                                      options=self.packages['packages'])

        self.metrics_widget = Select(title="Metric:",
                                     value=self.selected_metric,
                                     options=self.metrics['metrics'])

        active = self.periods['periods'].index(self.selected_period)

        self.period_widget = RadioButtonGroup(labels=self.periods['periods'],
                                              active=active)

    def make_header(self):
        """Header area including a title and a message text"""

        self.header_widget = Div()
        self.update_header()

    def update_header(self):

        title_text = "<h2>Monitoring Verification Metrics</h2>"

        message_text = "<center><p style='color:red;'>{}</p>" \
                       "</center>".format(self.message)

        self.header_widget.text = "{}{}".format(title_text, message_text)

    def make_plot_title(self):
        """Plot title including metric display name and a description
        """
        self.plot_title = Div()
        self.update_plot_title()

    def update_plot_title(self):

        metric_name = self.selected_metric

        display_name = None
        description = None

        if metric_name in self.metrics_meta:
            display_name = self.metrics_meta[metric_name]['display_name']
            description = self.metrics_meta[metric_name]['description']

        self.plot_title.text = "<p align='center'><strong>" \
                               "{}:</strong> {}</p>".format(display_name,
                                                            description)

    def make_plot(self):
        """Time series plot with a hover and other bokeh tools.
        """
        self.plot = Figure(x_axis_type="datetime",
                           tools="pan, wheel_zoom, xbox_zoom, \
                                  save, reset, tap",
                           active_scroll="wheel_zoom")

        self.plot.x_range.follow = 'end'
        self.plot.x_range.range_padding = 0
        self.plot.xaxis.axis_label = 'Time (UTC)'

        self.plot.legend.click_policy = 'hide'
        self.plot.legend.location = 'top_right'

        hover = HoverTool(tooltips=[("Time (UTC)", "@date_created"),
                                    ("Metric measurement", "@value")])

        self.plot.add_tools(hover)

        # Measurements
        self.plot.line(x='time', y='value', source=self.cds,
                       legend="Metric Measurement", color="gray")

        self.plot.circle(x='time', y='value', source=self.cds,
                         color="gray", fill_color="white", size=12,
                         legend="Metric Measurement")

        self.status = Label(x=350, y=75, x_units='screen', y_units='screen',
                            text="", text_color="lightgray",
                            text_font_size='24pt',
                            text_font_style='normal')

        self.plot.add_layout(self.status)

        self.update_plot()

    def update_plot(self):

        metric_name = self.selected_metric

        display_name = None
        unit = None

        if metric_name in self.metrics_meta:
            display_name = self.metrics_meta[metric_name]['display_name']
            unit = self.metrics_meta[metric_name]['unit']

        if unit:
            self.plot.yaxis[0].axis_label = "{} [{}]".format(display_name,
                                                             unit)
        else:
            if display_name:
                self.plot.yaxis[0].axis_label = "{}".format(display_name)

        self.status.text = ""

        if self.cds.to_df().size < 1:
            self.status.text = "No data to display"

    def make_footnote(self):
        """Footnote area to include reference info
        """
        self.footnote = Div()
        self.update_footnote()

    def update_footnote(self):

        metric_name = self.selected_metric

        url = None
        doc = None
        page = None

        if metric_name in self.metrics_meta:
            reference = self.metrics_meta[metric_name]['reference']

            url = reference['url']
            doc = reference['doc']
            page = reference['page']

        self.footnote.text = ""

        if url and doc and page:
            self.footnote.text = "<p align='right'>Ref.: " \
                                 "<a href='{}'>{}</a>, " \
                                 "page {}.</p>".format(url, doc, page)

    def make_table(self):
        """Make a table synched with the plot
        """
        self.table = DataTable(source=self.cds, columns=[],
                               width=Layout.LARGE, height=Layout.SMALL,
                               editable=False, selectable=True,
                               fit_columns=True, scroll_to_selection=True)

        self.update_table()

    def update_table(self):

        metric_name = self.selected_metric

        display_name = None
        unit = None

        if metric_name in self.metrics_meta:
            display_name = self.metrics_meta[metric_name]['display_name']
            unit = self.metrics_meta[metric_name]['unit']

        title = None
        if unit:
            title = "{} [{}]".format(display_name, unit)
        else:
            if display_name:
                title = "{}".format(display_name)

        columns = [
            TableColumn(field="date_created", title="Time (UTC)",
                        sortable=True, default_sort='descending',
                        width=Layout.SMALL),
            TableColumn(field='value',
                        title=title, sortable=False, width=Layout.SMALL),
            ]

        self.table.columns = columns

    def make_layout(self):
        """App layout
        """
        packages = widgetbox(self.packages_widget, width=Layout.SMALL)
        metrics = widgetbox(self.metrics_widget, width=Layout.MEDIUM)

        header = widgetbox(self.header_widget, width=Layout.LARGE)
        period = widgetbox(self.period_widget, width=Layout.LARGE)

        plot_title = widgetbox(self.plot_title, width=Layout.LARGE)

        footnote = widgetbox(self.footnote, width=Layout.LARGE)

        l = column(header,
                   row(packages, metrics),
                   period, plot_title, self.plot,
                   footnote, self.table)

        self.add_layout(l)
