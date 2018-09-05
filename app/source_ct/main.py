import os
import sys
import numpy as np
# This is needed to import the api_helper module
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.append(os.path.join(BASE_DIR, 'monitor'))

from bokeh.models import ColumnDataSource, LinearColorMapper
from bokeh.plotting import figure
from bokeh.models.markers import Circle
from bokeh.models import BasicTicker, NumeralTickFormatter
from bokeh.models import LinearAxis, DataRange1d

from bokeh.layouts import column

from base import BaseApp

class SourceCtMetric(BaseApp):

    def __init__(self):
        super().__init__()
        args = self.parse_args()
        self.selected_metric = args['metric']
        print('\n')
        print('selected_metric: ',self.selected_metric)
        print('\n')
        data = self.get_api_data(endpoint='blob', item=args['job_id'],
                                 params={'name': self.selected_metric,
                                         'metric': self.selected_metric})
        print('\ndata stats')
        for kk in data.keys():
            print(kk)
        mag_arr = -2.5*np.log10(data['flux']['value'])
        column_data = ColumnDataSource({'ra':data['ra_rad']['value'],
                                        'dec':data['dec_rad']['value'],
                                        'flux':data['flux']['value'],
                                        'mag':mag_arr,
                                        'flux_sigma':data['flux_sigma']['value']})



        color_mapper = LinearColorMapper(palette='Magma256',
                                         low=min(mag_arr),
                                         high=max(mag_arr))


        plot = figure()
        plot.circle(x='ra', y='dec', source=column_data, size=5,
                    color={'field':'mag', 'transform':color_mapper})

        #plot.legend.location = "top_right"

        ra_axis = LinearAxis(formatter=NumeralTickFormatter(format="0.00"),
                             ticker=BasicTicker(desired_num_ticks=4),
                             minor_tick_line_width=2,
                             major_tick_line_width=4,
                             major_tick_out=30,
                             minor_tick_out=5,
                             axis_label='RA (radians)')

        dec_axis = LinearAxis(formatter=NumeralTickFormatter(format="0.00"),
                             ticker=BasicTicker(desired_num_ticks=4),
                             minor_tick_line_width=2,
                             major_tick_line_width=4,
                             major_tick_out=30,
                             minor_tick_out=5,
                             axis_label='Dec (radians)')

        plot.add_layout(ra_axis, 'below')
        plot.add_layout(dec_axis, 'left')
        plot.x_range = DataRange1d()
        plot.y_range = DataRange1d()

        col = column(plot)
        self.add_layout(col)


###### ACTUALLY EXECUTE ########

SourceCtMetric()
