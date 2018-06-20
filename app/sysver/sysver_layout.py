from bokeh.layouts import column, widgetbox
from bokeh.models.widgets import Div, Paragraph
from bokeh.plotting import figure
import matplotlib as mpl
from matplotlib import cm

from sysver_base import BaseApp

class Layout(BaseApp):

    # Default sizes for widgets
    SMALL = 175
    MEDIUM = 350
    LARGE = 1000

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
        ave_temp = widgetbox(self.ave_temp_widget, width=Layout.SMALL)
        layout = column(ave_temp, self.plot)
        self.doc.add_root(layout)

    def make_paragraph(self):
        self.ave_temp_widget = Paragraph()
        self.update_ave_temp()

    def make_scatterplot(self):
        self.plot = figure(tools="pan, box_zoom, wheel_zoom, reset",
                           active_scroll="wheel_zoom", x_axis_label="Body Position [mm]",
                           y_axis_label="Body Angle [deg]")

        temperatures = self.cds.data['temperatures']
        color_temps = mpl.colors.Normalize()(temperatures)
        hex_color = "#{:02x}{:02x}{:02x}"
        colors = [
            hex_color.format(int(r), int(g), int(b)) for r, g, b, _ in 255 * cm.plasma(color_temps)
        ]
        self.cds.data['colors'] = colors

        self.plot.circle('body_position', 'body_angle', size=10, fill_color='colors', line_color=None,
                         source=self.cds.data)

    def update_ave_temp(self):
        avg_value = self.metric_value.get('value', '')
        value_units = self.metric_value.get('units', '')
        message = "Average Temperature: {} {}".format(avg_value, value_units)
        print("Q:", message)
        self.ave_temp_widget.text = message

    def update_header(self):
        self.header_widget.text = "<p style='color:red;'>{}</p>".format(self.message)
