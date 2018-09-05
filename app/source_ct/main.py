import os
import sys
import numpy as np
# This is needed to import the api_helper module
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.append(os.path.join(BASE_DIR, 'monitor'))

from bokeh.models.annotations import Title
from bokeh.models import ColumnDataSource, LinearColorMapper
from bokeh.models import Plot
from bokeh.models.markers import Circle
from bokeh.models import ColorBar
from bokeh.models import BasicTicker, NumeralTickFormatter
from bokeh.models import LinearAxis, DataRange1d
import bokeh.models.tools as bokeh_tools

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
        snr_arr = np.array(data['flux']['value'])/np.array(data['flux_sigma']['value'])
        column_data = ColumnDataSource({'ra':data['ra_rad']['value'],
                                        'dec':data['dec_rad']['value'],
                                        'mag':mag_arr,
                                        'snr':snr_arr})



        color_mapper = LinearColorMapper(palette='Magma256',
                                         low=min(mag_arr),
                                         high=max(mag_arr))


        title = Title(text='log(flux)')
        flux_plot = Plot(title=title)
        flux_dots = Circle(x='ra', y='dec', size=5,
                      line_color=None,
                      fill_color={'field':'mag', 'transform':color_mapper})

        color_bar = ColorBar(color_mapper=color_mapper, ticker=BasicTicker())
        flux_plot.add_glyph(column_data, flux_dots)
        flux_plot.add_layout(color_bar, 'right')

        color_mapper = LinearColorMapper(palette='Magma256',
                                         low=min(snr_arr),
                                         high=max(snr_arr))


        title = Title(text='SNR')
        snr_plot = Plot(title=title)

        snr_dots = Circle(x='ra', y='dec', size=5,
                      line_color=None,
                      fill_color={'field':'snr', 'transform':color_mapper})

        color_bar = ColorBar(color_mapper=color_mapper, ticker=BasicTicker())
        snr_plot.add_glyph(column_data, snr_dots)
        snr_plot.add_layout(color_bar, 'right')

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

        flux_plot.add_layout(ra_axis, 'below')
        flux_plot.add_layout(dec_axis, 'left')
        flux_plot.x_range = DataRange1d()
        flux_plot.y_range = DataRange1d()

        flux_plot.add_tools(bokeh_tools.BoxZoomTool())
        flux_plot.add_tools(bokeh_tools.ResetTool())
        flux_plot.add_tools(bokeh_tools.LassoSelectTool())


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

        snr_plot.add_layout(ra_axis, 'below')
        snr_plot.add_layout(dec_axis, 'left')
        snr_plot.x_range = DataRange1d()
        snr_plot.y_range = DataRange1d()

        snr_plot.add_tools(bokeh_tools.BoxZoomTool())
        snr_plot.add_tools(bokeh_tools.ResetTool())
        snr_plot.add_tools(bokeh_tools.LassoSelectTool())


        col = column(flux_plot)
        self.add_layout(col)
        col = column(snr_plot)
        self.add_layout(col)


###### ACTUALLY EXECUTE ########

SourceCtMetric()
