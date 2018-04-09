from bokeh.models.widgets import Select, Div, RadioButtonGroup
from bokeh.layouts import widgetbox, row, column
from bokeh.plotting import Figure
from bokeh.models import HoverTool, Range1d, CustomJS, \
    LinearAxis, Label

from bokeh.models.widgets import DataTable, TableColumn, HTMLTemplateFormatter

from base import BaseApp


class Layout(BaseApp):
    """Define the Monitor App widgets and the Bokeh document layout.
    """
    # default sizes for widgets
    SMALL = 175
    MEDIUM = 350
    LARGE = 1000
    XLARGE = 3000

    def __init__(self):
        super().__init__()

        # generic message shown in the header area
        self.message = str()

        self.make_input_widgets()
        self.make_header()

        self.load_data(self.selected_dataset,
                       self.selected_metric,
                       self.selected_period)

        self.make_plot_title()
        self.make_plot()
        self.make_footnote()
        self.make_table()

        self.make_layout()

    @staticmethod
    def get_sorted(data, key):
        """Extract a list of values from a dict
        and sort them alphabetically.

        Parameters
        ----------
        data: dict
            a dictionary from which we want
            to extract the values
        key: str
            the corresponding dictionary key

        Return
        ------
        s: list
            a list of values sorted alphabetically
        """
        values = [data[d][key] for d in data]

        return sorted(values)

    def make_input_widgets(self):
        """Define the widgets to select dataset, verification package,
        metrics and period
        """
        # Datasets
        self.datasets = self.get_datasets(default="hsc")

        if 'ci_dataset' in self.args:
            self.selected_dataset = self.args['ci_dataset']
        else:
            self.selected_dataset = self.datasets['default']

        self.datasets_widget = Select(title="Dataset:",
                                      value=self.selected_dataset,
                                      options=self.datasets['datasets'])
        # Verification Packages
        self.packages = self.get_packages(default='validate_drp')

        if 'package' in self.args:
            self.selected_package = self.args['package']
        else:
            self.selected_package = self.packages['default']

        self.packages_widget = Select(title="Verification package:",
                                      value=self.selected_package,
                                      options=self.packages['packages'])
        # Metrics
        self.metrics = self.get_metrics(package=self.selected_package)

        metric_names = self.get_sorted(data=self.metrics,
                                       key='name')

        if 'metric' in self.args:
            self.selected_metric = self.args['metric']
        else:
            self.selected_metric = metric_names[0]

        self.metrics_widget = Select(title="Metric:",
                                     value=self.selected_metric,
                                     options=metric_names)
        # Period
        self.periods = {'periods': ['All', 'Last Year', 'Last 6 Months',
                                    'Last Month'],
                        'default': 'Last 6 Months'}

        if 'period' in self.args:
            self.selected_period = self.args['period']
        else:
            self.selected_period = self.periods['default']

        active = self.periods['periods'].index(self.selected_period)

        self.period_widget = RadioButtonGroup(labels=self.periods['periods'],
                                              active=active)

    def make_header(self):
        """Header area including a title and message text"""

        self.header_widget = Div()
        self.update_header()

    def update_header(self):

        title_text = "<h2>The impact of code changes on" \
                     " Key Performance Metrics</h2>"

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

        display_name = self.metrics[metric_name]['display_name']
        description = self.metrics[metric_name]['description']

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
                                    ("Job ID", "@ci_id"),
                                    ("Metric measurement", "@value"),
                                    ("# of packages changed", "@count")])

        self.plot.add_tools(hover)

        # Measurements
        self.plot.line(x='time', y='value', source=self.cds,
                       legend="Measurements", color="gray")

        self.plot.circle(x='time', y='value', source=self.cds,
                         color="gray", fill_color="white", size=12,
                         legend="Measurements")

        # Code changes
        self.plot.add_layout(LinearAxis(y_range_name="pkgs_changed",
                                        axis_label="# of packages changed"),
                             'right')

        max_count = 0
        if 'count' in self.cds.data:
            max_count = max(self.cds.data['count'])

        self.plot.extra_y_ranges = {'pkgs_changed':
                                    Range1d(start=0, end=max_count)}

        self.plot.line(x='time', y='count', y_range_name='pkgs_changed',
                       source=self.cds, line_width=1, color='lightblue',
                       legend="Code changes")

        # This callback is used to reset the range of the extra y-axis
        # to its original value when zoom or pan

        args = {'range': self.plot.extra_y_ranges['pkgs_changed']}
        code = """
            range.start = 0;
            range.end = parseInt({});
            """.format(max_count)

        callback = CustomJS(args=args, code=code)

        self.plot.extra_y_ranges['pkgs_changed'].js_on_change('start',
                                                              callback)

        self.status = Label(x=350, y=75, x_units='screen', y_units='screen',
                            text="", text_color="lightgray",
                            text_font_size='24pt',
                            text_font_style='normal')

        self.plot.add_layout(self.status)

        self.update_plot()

    def update_plot(self):

        metric_name = self.selected_metric

        display_name = self.metrics[metric_name]['display_name']
        unit = self.metrics[metric_name]['unit']

        if unit:
            self.plot.yaxis[0].axis_label = "{} [{}]".format(display_name,
                                                             unit)
        else:
            self.plot.yaxis[0].axis_label = "{}".format(display_name)

        self.status.text = ""

        if self.cds.to_df().size < 2:
            self.status.text = "No data to display"

    def make_footnote(self):
        """Footnote area to include reference info
        """
        self.footnote = Div()
        self.update_footnote()

    def update_footnote(self):

        metric_name = self.selected_metric

        reference = self.metrics[metric_name]['reference']

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
                               fit_columns=False, scroll_to_selection=True)

        self.update_table()

    def update_table(self):

        metric_name = self.selected_metric

        display_name = self.metrics[metric_name]['display_name']
        unit = self.metrics[metric_name]['unit']
        if unit:
            title = "{} [{}]".format(display_name, unit)
        else:
            title = "{}".format(display_name)

        # Job ID
        template = '<a href="<%= ci_url %>" target=_blank ><%= value %></a>'
        ci_url_formatter = HTMLTemplateFormatter(template=template)

        # Packages
        template = """<% for (x in git_urls) {
                      if (x>0) print(", ");
                      print("<a href=" + git_urls[x] + " target=_blank>"
                      + value[x] + "</a>")
                      }; %>
                   """

        git_url_formatter = HTMLTemplateFormatter(template=template)

        columns = [
            TableColumn(field="date_created", title="Time (UTC)",
                        sortable=True, default_sort='descending',
                        width=Layout.SMALL),
            TableColumn(field="ci_id", formatter=ci_url_formatter,
                        title="Job ID", sortable=False,
                        width=Layout.SMALL),
            TableColumn(field='value', title=title, sortable=False,
                        width=Layout.SMALL),
            # Give room for a large list of package names
            TableColumn(field="package_names", title="Code changes",
                        formatter=git_url_formatter, width=Layout.XLARGE,
                        sortable=False)
        ]

        self.table.columns = columns

    def make_layout(self):
        """App layout
        """
        datasets = widgetbox(self.datasets_widget, width=Layout.SMALL)
        packages = widgetbox(self.packages_widget, width=Layout.SMALL)
        metrics = widgetbox(self.metrics_widget, width=Layout.MEDIUM)

        header = widgetbox(self.header_widget, width=Layout.LARGE)
        period = widgetbox(self.period_widget, width=Layout.LARGE)

        plot_title = widgetbox(self.plot_title, width=Layout.LARGE)

        footnote = widgetbox(self.footnote, width=Layout.LARGE)

        l = column(header,
                   row(datasets, packages, metrics),
                   period, plot_title, self.plot,
                   footnote, self.table)

        self.add_layout(l)
