from bokeh.models import ColumnDataSource
from bokeh.models import Plot
from bokeh.models.markers import Circle
from bokeh.models import BasicTicker, NumeralTickFormatter
from bokeh.models import LinearAxis

from bokeh.layouts import column

from base import BaseApp

class SourceCtMetric(BaseApp):

    def __init__(self):
        self.data = get_api_data(endpoint='blob')
        data = ColumnDataSource({'ra':data['ra_rad'],
                                 'dec':data['dec_rad']})

        plot = Plot()
        sources = Circle(x='ra', y='dec', line_color=None, size=5)
        plot.add_glyp(data, sources)
        ra_axis = LinearAxis(formatter=NumeralTickFormatters(format="0.00"),
                             ticker=BasicTicker(desired_num_ticks=4),
                             minor_tick_line_width=2,
                             major_tick_line_width=4,
                             major_tick_out=30,
                             minor_tick_out=5,
                             axis_label='RA (radians)')

        dec_axis = LinearAxis(formatter=NumeralTickFormatters(format="0.00"),
                             ticker=BasicTicker(desired_num_ticks=4),
                             minor_tick_line_width=2,
                             major_tick_line_width=4,
                             major_tick_out=30,
                             minor_tick_out=5,
                             axis_label='Dec (radians)')

        plot.add_layout(ra_axis, 'below')
        plot.add_layout(dec_axis, 'left')

        col = column(plot)
        self.add_layout(col)


###### ACTUALLY EXECUTE ########

SourceCtMetric()
