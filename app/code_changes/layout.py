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
    TINY = 175
    SMALL = 250
    MEDIUM = 500
    LARGE = 1000
    XLARGE = 3000

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

        self.datasets_widget = Select(title="Dataset:",
                                      value=self.selected_dataset,
                                      options=self.datasets['datasets'])

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

        hover = HoverTool(tooltips=[("Time (UTC)", "@date_created"),
                                    ("CI ID", "@ci_id"),
                                    ("Metric measurement", "@value"),
                                    ("Filter", "@filter_name"),
                                    ("# of packages changed", "@count")])

        self.plot.add_tools(hover)

        self.plot.circle(x='time', y='value',
                         color='color', legend='filter_name',
                         source=self.cds, fill_color='white', size=12)

        # Legend
        self.plot.background_fill_alpha = 0
        self.plot.legend.location = 'top_right'
        self.plot.legend.click_policy = 'hide'
        self.plot.legend.orientation = 'horizontal'

        # Toolbar
        self.plot.toolbar.logo = None

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

        display_name = self.metrics_meta[metric_name]['display_name']
        unit = self.metrics_meta[metric_name]['unit']

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
                               width=Layout.LARGE, height=Layout.TINY,
                               editable=False, selectable=True,
                               fit_columns=False, scroll_to_selection=True)

        self.update_table()

    def update_table(self):

        metric_name = self.selected_metric

        display_name = self.metrics_meta[metric_name]['display_name']
        unit = self.metrics_meta[metric_name]['unit']
        if unit:
            title = "{} [{}]".format(display_name, unit)
        else:
            title = "{}".format(display_name)

        # CI ID
        template = '<a href="<%= ci_url %>" target=_blank ><%= value %></a>'
        ci_url_formatter = HTMLTemplateFormatter(template=template)

        if self.selected_metric == "validate_drp.AM1" or \
           self.selected_metric == "validate_drp.AM2":

            # Drill down app, it uses the job_id to access the data blobs
            app_url = "/dash/AMx?job_id=<%= job_id %>" \
                     "&metric={}&ci_id=<%= ci_id %>" \
                     "&ci_dataset={}".format(self.selected_metric,
                                             self.selected_dataset)

            template = '<a href="{}" ><%= parseFloat(value).toFixed(3) %>' \
                       '</a>'.format(app_url)

        else:
            template = "<%= parseFloat(value).toFixed(3) %>"

        # https://squash-restful-api-demo.lsst.codes/AMx?job_id=885
        # &metric=validate_drp.AM1

        app_url_formatter = HTMLTemplateFormatter(template=template)

        # Packages
        template = """<% for (x in git_urls) {
                      if (x>0) print(", ");
                      print("<a href=" + git_urls[x] + " target=_blank>"
                      + value[x] + "</a>")
                      }; %>
                   """

        git_url_formatter = HTMLTemplateFormatter(template=template)

        columns = [
            TableColumn(field="created_date", title="Time (UTC)",
                        sortable=True, default_sor  t='descending',
                        width=Layout.TINY),
            TableColumn(field="ci_id", formatter=ci_url_formatter,
                        title="CI ID", sortable=False,
                        width=Layout.TINY),
            TableColumn(field='value', formatter=app_url_formatter,
                        title=title, sortable=False, width=Layout.TINY),
            # Give room for a large list of package names
            TableColumn(field="package_names", title="Code changes",
                        formatter=git_url_formatter, width=Layout.XLARGE,
                        sortable=False)
        ]

        self.table.columns = columns

    def make_layout(self):
        """App layout
        """
        datasets = widgetbox(self.datasets_widget, width=Layout.TINY)
        packages = widgetbox(self.packages_widget, width=Layout.SMALL)
        metrics = widgetbox(self.metrics_widget, width=Layout.SMALL)

        header = widgetbox(self.header_widget, width=Layout.LARGE)
        period = widgetbox(self.period_widget, width=Layout.LARGE)

        plot_title = widgetbox(self.plot_title, width=Layout.LARGE)

        footnote = widgetbox(self.footnote, width=Layout.LARGE)

        l = column(header,
                   row(datasets, packages, metrics),
                   period, plot_title, self.plot,
                   footnote, self.table)

        self.add_layout(l)
