from bokeh.core.enums import Orientation
from bokeh.layouts import column, widgetbox
from bokeh.models import ColorBar, LinearColorMapper
from bokeh.models.widgets import Div
from bokeh.plotting import figure
import matplotlib as mpl
from matplotlib import cm
import numpy as np

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
        self.make_layout()

    def make_header(self):
        """Header area for the app, include a title and
        a generic message."""

        self.header_widget = Div()
        self.update_header()

    def make_layout(self):
        header = widgetbox(self.header_widget, width=Layout.LARGE)
        ave_temp = widgetbox(self.ave_temp_widget, width=Layout.LARGE)
        layout = column(header, ave_temp, self.plot)
        self.doc.add_root(layout)

    def make_paragraph(self):
        self.ave_temp_widget = Div()
        self.update_ave_temp()

    def make_scatterplot(self):
        x_label = "{} [{}]".format(self.x_axis['label'], self.x_axis['units'].to_string())
        y_label = "{} [{}]".format(self.y_axis['label'], self.y_axis['units'].to_string())
        z_label = "{} [{}]".format(self.z_axis['label'], self.z_axis['units'].to_string())

        self.plot = figure(tools="box_select, pan, box_zoom, wheel_zoom, reset",
                           active_scroll="wheel_zoom", x_axis_label=x_label,
                           y_axis_label=y_label)

        temperatures = self.cds.data['temperatures']
        color_temps = mpl.colors.Normalize()(temperatures)
        hex_color = "#{:02x}{:02x}{:02x}"
        colors = [
            hex_color.format(int(r), int(g), int(b)) for r, g, b, _ in 255 * cm.plasma(color_temps)
        ]
        self.cds.data['colors'] = colors

        self.pcircle = self.plot.circle('body_position', 'body_angle', size=5, fill_color='colors',
                                        line_color=None,
                                        source=self.cds.data)

        palette = "{}256".format(cm.plasma.name.capitalize())
        color_mapper = LinearColorMapper(palette=palette, low=np.min(temperatures),
                                         high=np.max(temperatures))
        color_bar = ColorBar(color_mapper=color_mapper, location=(0, 0), title=z_label,
                             label_standoff=5, title_standoff=5,
                             orientation=Orientation.horizontal)

        self.plot.add_layout(color_bar, 'below')

    def update_ave_temp(self, average_value=None):
        if average_value is None:
            avg_value = self.metric_value.get('value', '')
        else:
            avg_value = average_value
        value_units = self.metric_value.get('units', '')
        message = "<p>Average Temperature: {:.3f} {}</p>".format(avg_value, value_units.strip())
        self.ave_temp_widget.text = message

    def update_header(self):
        self.header_widget.text = "<p style='color:red;'>{}</p>".format(self.message)
