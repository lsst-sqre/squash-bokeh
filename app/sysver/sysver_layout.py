from bokeh.core.enums import Orientation
from bokeh.layouts import column, widgetbox
from bokeh.models import ColorBar
from bokeh.models.widgets import Div
from bokeh.palettes import Plasma256
from bokeh.plotting import figure
from bokeh.transform import linear_cmap

from sysver_base import BaseApp


class Layout(BaseApp):

    # Default sizes for widgets
    SMALL = 175
    MEDIUM = 350
    LARGE = 1000
    XLARGE = 3000

    def __init__(self):
        super().__init__()
        self.make_header()
        self.make_paragraph()
        self.make_scatterplot()

    def make_header(self):
        """Header area for the app, include a title and
        a generic message."""

        self.header_widget = Div()
        self.update_header()

    def make_layout(self):
        header = widgetbox(self.header_widget, width=Layout.LARGE)
        metric = widgetbox(self.metric_widget, width=Layout.LARGE)
        layout = column(header, metric, self.plot)
        self.doc.add_root(layout)

    def make_paragraph(self):
        self.metric_widget = Div()
        self.update_metric_display()

    def make_scatterplot(self):
        x_label = "{} [{}]".format(self.x_axis['label'],
                                   self.x_axis['units'].to_string())
        y_label = "{} [{}]".format(self.y_axis['label'],
                                   self.y_axis['units'].to_string())
        z_label = "{} [{}]".format(self.z_axis['label'],
                                   self.z_axis['units'].to_string())

        tool_list = "box_select, pan, box_zoom, wheel_zoom, reset"
        self.plot = figure(tools=tool_list,
                           active_scroll="wheel_zoom", x_axis_label=x_label,
                           y_axis_label=y_label)

        z_values = self.cds.data['z']
        mapper = linear_cmap(field_name='z', palette=Plasma256,
                             low=min(z_values), high=max(z_values))

        self.pcircle = self.plot.circle('x', 'y', size=5,
                                        color=mapper,
                                        line_color=mapper,
                                        source=self.cds.data)

        color_bar = ColorBar(color_mapper=mapper['transform'], location=(0, 0),
                             title=z_label,
                             label_standoff=5, title_standoff=5,
                             orientation=Orientation.horizontal)

        self.plot.add_layout(color_bar, 'below')

    def format_metric_text(self, value=None):
        if value is None:
            value = self.metric_value.get('value', '')
        value_units = self.metric_value.get('units', '')

        text = "Average Temperature: {:.3f} {}".format(value,
                                                       value_units.strip())
        return text

    def update_metric_display(self, value=None):
        self.metric_widget.text = self.format_metric_text(value)

    def update_header(self):
        template = "<p style='color:red;'>{}</p>"
        self.header_widget.text = template.format(self.message)
