import os
import sys
from datetime import datetime
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, HoverTool, Span, Label
from bokeh.models.widgets import Select, Div, DataTable, TableColumn,\
    HTMLTemplateFormatter
from bokeh.layouts import row, widgetbox, column
from bokeh.plotting import Figure

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.append(os.path.join(BASE_DIR))

from helper import get_datasets, get_metrics, get_specs, get_data_as_pandas_df # noqa


class Monitor(object):
    """The monitor app consists of a time series plot showing measurements
    for a given selected ci_dataset and metric. It also displays code changes
    comparing the list of packages and their git shas between two consecutive
    ci_jobs
    """

    def __init__(self):

        # Measurements for the selected dataset and metric
        self.data = {}

        # Used to control the display if there's no data
        self.empty = True

        # Column data source used by the bokeh app
        self.source = ColumnDataSource(data={'x': [],
                                             'y': [],
                                             'time': [],
                                             'ci_ids': [],
                                             'ci_urls': [],
                                             'units': [],
                                             'names': [],
                                             'git_urls': [],
                                             })
        self.compose_layout()

    def compose_layout(self):
        """Compose the app layout, the main elements are the widgets to
        select the ci_dataset, the metric, a div for the app header, a
        plot and a table
        """

        # Load  metrics and datasets and use the default ones
        self.metrics = get_metrics()
        self.datasets = get_datasets()

        self.selected_metric = self.metrics['default']
        self.selected_dataset = self.datasets['default']

        # Configure the dataset selection widget
        dataset_selection = Select(title="Data Set:",
                                   value=self.selected_dataset,
                                   options=self.datasets['datasets'],
                                   width=100)

        dataset_selection.on_change("value", self.on_dataset_change)

        # Configure the metric selection widget
        metric_selection = Select(title="Metric:",
                                  value=self.selected_metric,
                                  options=self.metrics['metrics'],
                                  width=100)

        metric_selection.on_change("value", self.on_metric_change)

        self.load_data()

        self.make_header()

        self.make_plot()

        self.make_table()

        self.layout = column(row(widgetbox(metric_selection, width=150),
                                 widgetbox(dataset_selection, width=150)),
                             widgetbox(self.title, width=1000),
                             self.plot,
                             widgetbox(self.table_title, width=1000),
                             self.table)

    def on_dataset_change(self, attr, old, new):
        """Handle dataset selection event, it reloads the measurements
        when another dataset set is selected and updates the app

        Parameters
        ----------
        attr : str
            refers to the changed attribute’s name, not used
        old : str
            previous value, not used
        new : str
            new value

        See also
        --------
        http://bokeh.pydata.org/en/latest/docs/user_guide/interaction
        /widgets.html#userguide-interaction-widgets
        """

        # set new status for the app
        self.status.text = "Loading..."

        # load data for the selected dataset
        self.selected_dataset = new
        self.load_data()

        self.update_header()

        self.update_plot()

        # Update data table content, the url to the bokeh apps
        # depends on the selected dataset
        self.table.columns = self.update_table()

    def on_metric_change(self, attr, old, new):
        """Handle metric selection event,  it reloads the measurements
        when another metric is selected and updates the app

        Parameters
        ----------
        attr : str
            refers to the changed attribute’s name, not used
        old : str
            previous value, not used
        new : str
            new value

        See also
        --------
        http://bokeh.pydata.org/en/latest/docs/user_guide/interaction
        /widgets.html#userguide-interaction-widgets
        """

        # set new status for the app
        self.status.text = "Loading..."

        # load data for the selected metric
        self.selected_metric = new
        self.load_data()

        self.update_header()

        self.update_plot()

        # Update data table content, the url to the bokeh apps
        # depends on the selected metric
        self.table.columns = self.update_table()

    def load_data(self):
        """ Load data and update the bokeh column data source with
        measurements for the selected dataset and metric
        """

        # load specifications for the selected metric
        self.specs = get_specs(self.selected_metric)

        # load measurements and code changes for the selected
        # metric and dataset

        # the separation in two distinct API endpoints helps to improve
        # the performance here cache is enabled in the API and we don't
        # need to reload the code changes data when a different metric
        # is selected

        self.measurements = get_data_as_pandas_df(
            endpoint='measurements',
            params={'ci_dataset': self.selected_dataset,
                    'metric': self.selected_metric})

        # in the current implementation we have a job matrix in ci so
        # the same ci_id have runs for different ci_datasets thus we
        # need to filter here

        self.code_changes = get_data_as_pandas_df(
            endpoint='code_changes',
            params={'ci_dataset': self.selected_dataset})

        # now we merge the two data frames on 'ci_id' keeping all ci_id's
        # in the measurements data frame (left) and preserving the original
        # order

        self.data = self.measurements.merge(self.code_changes,
                                            on='ci_id', how='left')

        # we need at least two data points to draw a line
        size = len(self.data['value'])
        if size > 2:
            self.empty = False

        # one requirement of bokeh is that all the attributes of a column data
        # source must have the same size
        units = [self.specs['unit']] * size

        # TODO: perhaps this manipulation could be done in the view

        # list of package names and git urls from the code changes API endpoint
        package_names = []
        git_urls = []

        for i, sublist in enumerate(self.data['packages']):
            package_names.append([])
            git_urls.append([])
            # can be a list or a nan (i.e, a pandas missing value)
            if type(sublist) == list:
                for package in sublist:
                    package_names[i].append(package[0])
                    git_urls[i].append(
                        "{}/commit/{}".format(package[2].strip('.git'),
                                              package[1]))

        self.source.data = dict(x=[datetime.strptime(x.split('.')[0],
                                                     "%Y-%m-%dT%H:%M:%S")
                                   for x in self.data['date']],
                                y=self.data['value'],
                                time=[x.replace('T', ' ').split('.')[0]
                                      for x in self.data['date']],
                                ci_ids=self.data['ci_id'],
                                ci_urls=self.data['ci_url'],
                                units=units,
                                names=package_names,
                                git_urls=git_urls)

    def make_header(self):
        """Make the app title"""

        self.title = Div(text="")
        self.update_header()

    def update_header(self):
        """ Plot title and description must be updated each time
        the metric or dataset changes
        """

        title = "{} measurements for {} dataset".format(self.selected_metric,
                                                        self.selected_dataset)
        description = self.specs['description']

        self.title.text = """<left><h3>{}</h3>{}</left>""".format(title,
                                                                  description)

    def make_plot(self):
        """Make a line-circle-line plot with a hover, other bokeh tools
        annotate metric thresholds and the app status
        """

        hover = HoverTool(tooltips=[("Time", "@time"),
                                    ("Value", "@y (@units)"),
                                    ("Job ID", "@ci_ids")])

        self.plot = Figure(x_axis_type='datetime',
                           tools='pan, wheel_zoom, xbox_zoom, reset, tap',
                           active_scroll='wheel_zoom')

        self.plot.add_tools(hover)

        # TODO: configure the x_range to display last week, month or year

        self.plot.x_range.follow = 'end'
        self.plot.x_range.range_padding = 0
        self.plot.xaxis.axis_label = 'Time'

        self.plot.line(
            x='x', y='y', source=self.source,
            line_width=2, color='black')

        self.plot.circle(x='x', y='y', source=self.source,
                         color="black", fill_color="white", size=16)

        self.make_annotations()

        self.update_plot()

    def update_plot(self):

        # set y-axis label
        self.plot.yaxis.axis_label = "{} [{}]".format(self.selected_metric,
                                                      self.specs['unit'])

        # update threshold and status annotations

        self.update_annotations()

    def make_table(self):
        """Make a data table to list the packages that changed with respect to
        the previous ci build, add links to diagnostic plots associated with
        the measurements, to the corresponding ci build and git urls
        """
        title = "Code Changes"

        description = "The table lists measurements values for each job " \
                      "and packages that have changed with respect "\
                      "to the pevious job." \
                      " Tap on the job ID, on the values or on the package" \
                      " names for more information."

        self.table_title = Div(text="""<left><h3>{}
        </h3>{}</left>""".format(title, description))

        columns = self.update_table()

        self.table = DataTable(
            source=self.source, columns=columns, width=1000, height=200,
            row_headers=True, fit_columns=False, scroll_to_selection=True,
            editable=False
        )

    def update_table(self):
        """Update content of the data table"""

        # FIX: get app url from the monitor api endpoint, for now
        # use this name convention for the apps, e.g. the bokeh app for
        # displaying diagnostic plots for metrics AM1, AM2, AM3 is named AMx

        bokeh_app = self.selected_metric.replace(self.selected_metric[-1], 'x')
        bokeh_app_url = "{}".format(bokeh_app)

        # job id is selected from the table
        params = "?metric={}&" \
                 "ci_dataset={}&" \
                 "ci_id=<%= ci_ids %>".format(self.selected_metric,
                                              self.selected_dataset)

        bokeh_app_url = "{}/{}".format(bokeh_app_url, params)

        template = '<a href="{}"><%= value %></a>'.format(bokeh_app_url)
        value_url_formatter = HTMLTemplateFormatter(template=template)

        template = '<a href="<%= ci_urls %>"><%= value %></a>'
        ci_url_formatter = HTMLTemplateFormatter(template=template)

        template = '<% for (x in git_urls) { ' \
                   '       if (x>0) print(", "); ' \
                   '       print("<a href=" + git_urls[x] + ">" ' \
                   '              + value[x] + "</a>")' \
                   '   }; ' \
                   '%>'
        git_url_formatter = HTMLTemplateFormatter(template=template)

        columns = [
            TableColumn(field="time", title="Time",
                        width=200),
            TableColumn(field="ci_ids", title="Job ID",
                        formatter=ci_url_formatter, width=100),
            TableColumn(field="y", title="Value",
                        formatter=value_url_formatter,
                        width=100, sortable=False),
            TableColumn(field="names", title="Packages",
                        formatter=git_url_formatter, width=600,
                        sortable=False),
        ]

        return columns

    def draw_status_annotation(self):
        """Draw a text label in the middle of the plot to indicate its
        status
        """

        self.status = Label(x=350,
                            y=200,
                            x_units='screen',
                            y_units='screen',
                            text="",
                            text_color="lightgray",
                            text_font_size='36pt',
                            text_font_style='normal')

        self.plot.add_layout(self.status)

    def configure_thresholds(self):
        """Thresholds have values for each metric, a text and color
        """
        self.thresholds = {}
        self.thresholds['minimum'] = {'value': self.specs['minimum'],
                                      'text': 'Minimum',
                                      'color': 'red'}

        self.thresholds['design'] = {'value': self.specs['design'],
                                     'text': 'Design',
                                     'color': 'blue'}

        self.thresholds['stretch'] = {'value': self.specs['stretch'],
                                      'text': 'Stretch',
                                      'color': 'green'}

    def draw_threshold_annotation(self, threshold):
        """Draw a span annotation with a label for metric thresholds
        """
        location = threshold['value']
        color = threshold['color']

        span = Span(location=location, dimension='width',
                    line_width=2, line_color=color, line_dash='dotted',)

        self.plot.add_layout(span)

        text = threshold['text']

        label = Label(x=70, y=location, x_units='screen',
                      y_units='data', text=text, text_color=color,
                      text_font_size='11pt', text_font_style='normal')

        self.plot.add_layout(label)

        return {'span': span, 'label': label}

    def make_annotations(self):
        """ Make annotations for all metric thresholds
        """

        # TODO: add option to control display of threshold annotations

        # threshold annotations
        self.configure_thresholds()
        self.annotations = {}

        for t in self.thresholds:
            self.annotations[t] = self.draw_threshold_annotation(
                self.thresholds[t])

        # status annotations
        self.draw_status_annotation()

    def update_annotations(self):
        """ Threshold annotations must be updated with new specs each time a new metric
        is selected
        """
        # threshold annotations
        self.configure_thresholds()

        for t in self.annotations:
            self.annotations[t]['span'].location = self.thresholds[t]['value']
            self.annotations[t]['label'].y = self.thresholds[t]['value']

        # status annotations
        self.status.text = ""

        if self.empty:
            self.status.text = "No data to display"


curdoc().add_root(Monitor().layout)
curdoc().title = "SQUASH"