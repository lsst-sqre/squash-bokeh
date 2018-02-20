from bokeh.models.widgets import Select, Div, MultiSelect, RadioButtonGroup, \
    Panel, Tabs
from bokeh.layouts import widgetbox, row, column
from bokeh.plotting import Figure
from bokeh.models import HoverTool, GroupFilter, CDSView
from bokeh.models.widgets import DataTable, TableColumn, HTMLTemplateFormatter

from base import BaseApp


class Layout(BaseApp):
    """Define the Monitor App widgets and the Bokeh document layout.
    """
    SMALL = 175
    MEDIUM = 350
    LARGE = 1000

    def __init__(self):
        super().__init__()

        # generic message shown in the header area
        self.message = str()

        self.inputs()
        self.header()
        self.period()
        self.tabs()
        self.layout()

    def get_sorted(self, data, key):
        """Return a list of values sorted alphabetically.

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

    def inputs(self):
        """Define the widgets to select dataset, package,
        metric and tags.
        """

        # Dataset widget
        self.datasets = self.get_datasets(default='cfht')

        if 'dataset' in self.args:
            self.selected_dataset = self.args['dataset']
        else:
            self.selected_dataset = self.datasets['default']

        self.datasets_widget = Select(title="Dataset:",
                                      value=self.selected_dataset,
                                      options=self.datasets['datasets'])
        # Package widget
        self.packages = self.get_packages(default='validate_drp')

        if 'package' in self.args:
            self.selected_package = self.args['package']
        else:
            self.selected_package = self.packages['default']

        self.packages_widget = Select(title="Verification package:",
                                      value=self.selected_package,
                                      options=self.packages['packages'])
        # Metric widget
        self.metrics = self.get_metrics(package=self.selected_package)

        metric_names = self.get_sorted(data=self.metrics,
                                       key='name')

        self.selected_metrics = [metric_names[0]]

        self.metrics_widget = MultiSelect(title="Metrics:",
                                          value=self.selected_metrics,
                                          options=metric_names)
        # Tags widget
        if 'tags' in self.args:
            self.selected_tags = self.args['tags']
        else:
            self.selected_tags = self.get_sorted(self.metrics,
                                                 key='tags')

        self.tags_widget = MultiSelect(title="Filter by tag:",
                                       value=[],
                                       options=[])

    def header(self):

        self.header_widget = Div()
        self.update_header()

    def update_header(self):

        message_text = "<center><p style='color:red;'>{}</p>" \
                       "</center>".format(self.message)

        title_text = "<h2>Measurements from <em>{}</em> package on " \
                     "<em>{}</em> dataset</h2>".format(self.selected_package,
                                                       self.selected_dataset)

        self.header_widget.text = "{}{}".format(message_text, title_text)

    def period(self):
        """Configure the period selection widget.
        """
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

    def make_plot_title(self, display_name, description):
        """Plot title with metric display name and a description
        """

        title = Div(text="<p align='center'><strong>{}:</strong> "
                    "{}</p>".format(display_name, description))

        return title

    def make_plot(self, metric_name, display_name, unit, ref_plot=None):
        """Time series plot with a hover and other bokeh tools.

        Parameters
        ----------
        metric_name: str
            the metric measurements to display
        display_name: str
            the metric display name
        unit: str
            the metric unit
        ref_plot:
            a reference plot used to link the x axis

        Return
        ------
        plot: a bokeh Figure object
        """
        filter = GroupFilter(column_name='metric_name', group=metric_name)

        view = CDSView(source=self.cds, filters=[filter])

        # TODO: Add unit and package counts
        # hover = HoverTool(tooltips=[("Time (UTC)", "@date_created"),
        #                             ("Metric measurement", "@value (@unit)"),
        #                            ("# of packages changed", "@count")])

        hover = HoverTool(tooltips=[("Time (UTC)", "@date_created"),
                                    ("Job ID", "@ci_id"),
                                    ("Metric measurement", "@value")])

        plot = Figure(x_axis_type='datetime',
                      tools='pan, wheel_zoom, xbox_zoom, save, reset, tap',
                      active_scroll='wheel_zoom')

        if ref_plot:
            plot.x_range = ref_plot.x_range

        plot.x_range.follow = 'end'
        plot.x_range.range_padding = 0
        plot.xaxis.axis_label = 'Time (UTC)'

        plot.add_tools(hover)

        plot.line(x='time', y='value', source=self.cds, view=view,
                  legend='Metric measurements', color="gray")

        plot.circle(x='time', y='value', source=self.cds, view=view,
                    color="gray", fill_color="white", size=12,
                    legend="Metric measurements")

        if unit:
            plot.yaxis[0].axis_label = "{} [{}]".format(display_name, unit)
        else:
            plot.yaxis[0].axis_label = "{}".format(display_name)

        plot.legend.click_policy = 'hide'
        plot.legend.location = 'top_right'

        # TODO: enable code changes

        # max_count = max(self.source.data['count'])

        # self.plot.extra_y_ranges = {"count": Range1d(start=0, end=max_count)}

        # use a callback to reset the range of the extra y-axis to its original
        # value when zoom or pan is executed

        # jscode = """range.set('start', parseInt({}));
        #            range.set('end', parseInt({}));
        #         """

        # self.plot.extra_y_ranges["count"].callback = CustomJS(
        #    args=dict(range=self.plot.extra_y_ranges['count']),
        #    code=jscode.format(self.plot.extra_y_ranges['count'].start,
        #                       self.plot.extra_y_ranges['count'].end)
        # )

        # self.plot.line(x='x', y='count', y_range_name='count',
        #                source=self.source,
        #               line_width=1, color='lightblue',
        #               legend="Code changes")

        # self.plot.add_layout(LinearAxis(y_range_name="count",
        #                                axis_label="# of packages changed"),
        #                     'right')

        # self.plot.yaxis[1].axis_label = "# of packages changed"

        # update threshold and status annotations

        # self.make_annotations()
        # self.update_annotations()

        return plot

    def make_footnote(self, reference):

        footnote = Div(text="")

        url = reference['url']
        doc = reference['doc']
        page = reference['page']

        if url and doc and page:
            footnote.text = "<p align='right'>Ref.: <a href='{}'>{}</a>, " \
                            "page {}.</p>".format(url, doc, page)

        return footnote

    def graph_view(self):
        """Make the graph view panel with a list of bokeh widgets and plots
        """
        graph_view = []

        ref_plot = None

        # used the reversed order to show the latest metric selected first
        for metric_name in reversed(self.selected_metrics):

            display_name = self.metrics[metric_name]['display_name']
            unit = self.metrics[metric_name]['unit']
            description = self.metrics[metric_name]['description']
            reference = self.metrics[metric_name]['reference']

            title = self.make_plot_title(display_name, description)
            plot = self.make_plot(metric_name, display_name,
                                  unit, ref_plot)

            # the first plot is used to link the x_range of the
            # time series plots displayed in the graph view panel
            if ref_plot is None:
                ref_plot = plot

            footnote = self.make_footnote(reference)

            graph_view.append(widgetbox(title, width=Layout.LARGE))
            graph_view.append(plot)
            graph_view.append(widgetbox(footnote, width=Layout.LARGE))

        n = len(self.selected_metrics)
        self.graph_view_panel = Panel(child=column(graph_view),
                                      title="Graph View ({})".format(n))

    def table_view(self):
        """Make the table view panel with a table showing the selected metrics
        """

        # Job ID
        template = '<a href="<%= ci_url %>" target=_blank ><%= value %></a>'
        ci_url_formatter = HTMLTemplateFormatter(template=template)

        columns = [
            TableColumn(field="date_created", title="Time (UTC)",
                        sortable=True, default_sort='descending'),
            TableColumn(field="ci_id", formatter=ci_url_formatter,
                        title="Job ID", sortable=False)
        ]

        # Display only the latest metric selected
        metric_name = self.selected_metrics[-1]

        display_name = self.metrics[metric_name]['display_name']
        unit = self.metrics[metric_name]['unit']

        if unit:
            title = "{} [{}]".format(display_name, unit)
        else:
            title = "{}".format(display_name)

        columns.append(TableColumn(field='value', title=title, sortable=False))

        filter = GroupFilter(column_name='metric_name', group=metric_name)

        view = CDSView(source=self.cds, filters=[filter])

        table_view = DataTable(source=self.cds, view=view, columns=columns,
                               width=Layout.LARGE, height=Layout.MEDIUM,
                               editable=False, selectable=True,
                               scroll_to_selection=True)

        self.table_view_panel = Panel(child=table_view, title="Table View")

    def tabs(self):

        self.load_monitor_data(self.selected_dataset, self.selected_period)
        self.tabs = Tabs()
        self.update_tabs()

    def update_tabs(self):

        self.status = Div(text="<center><h2>Loading...</h2></center>")

        self.graph_view_panel = Panel(child=self.status, title="Graph View")
        self.table_view_panel = Panel(child=self.status, title="Table View")

        # Update panels with the Loading... message content
        self.tabs.tabs = [self.graph_view_panel, self.table_view_panel]

        self.table_view()
        self.graph_view()

        # Update panels with the plots and table
        self.tabs.tabs = [self.graph_view_panel, self.table_view_panel]

    def layout(self):

        # Define the app layout
        datasets = widgetbox(self.datasets_widget, width=Layout.SMALL)
        packages = widgetbox(self.packages_widget, width=Layout.SMALL)
        metrics = widgetbox(self.metrics_widget, width=Layout.MEDIUM)
        tags = widgetbox(self.tags_widget, width=Layout.MEDIUM)

        header = widgetbox(self.header_widget, width=Layout.LARGE)
        period = widgetbox(self.period_widget, width=Layout.LARGE)
        tabs = widgetbox(self.tabs, width=Layout.LARGE)

        l = column(row(datasets, packages, metrics, tags),
                   header, period, tabs)

        self.add_layout(l)
