import os
import sys
# This is needed to import the api_helper module
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.append(os.path.join(BASE_DIR, 'monitor'))

from bokeh.models import ColumnDataSource
from bokeh.models import Plot
from bokeh.models.markers import Circle
from bokeh.models import BasicTicker, NumeralTickFormatter
from bokeh.models import LinearAxis

from bokeh.layouts import column

from base import BaseApp

class SourceCtMetric(BaseApp):

    def __init__(self):
        super().__init__()
        self.selected_metric = 'dummy_ct_metric.SrcCt2'
        print('\n')
        print('selected_metric: ',self.selected_metric)
        print('\n')
        data = self.get_api_data(endpoint='blob', item=56,
                                 params={'name': self.selected_metric,
                                         'metric': self.selected_metric})
        print('\ndata stats')
        for kk in data.keys():
            print(kk)
        data = ColumnDataSource({'ra':data['ra_rad']['value'],
                                 'dec':data['dec_rad']['value']})

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
