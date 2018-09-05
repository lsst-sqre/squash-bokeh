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
from bokeh.models import CustomJS
import bokeh.models.tools as bokeh_tools

from bokeh.layouts import row

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
        orig_data = ColumnDataSource({'ra':data['ra_rad']['value'],
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
        flux_plot.add_glyph(orig_data, flux_dots)
        flux_plot.add_layout(color_bar, 'right')

        flux_plot.x_range = DataRange1d()
        flux_plot.y_range = DataRange1d()


        color_mapper = LinearColorMapper(palette='Magma256',
                                         low=min(snr_arr),
                                         high=max(snr_arr))


        title = Title(text='SNR')
        snr_plot = Plot(title=title)
        snr_plot.x_range = flux_plot.x_range
        snr_plot.y_range = flux_plot.y_range

        snr_dots = Circle(x='ra', y='dec', size=5,
                      line_color=None,
                      fill_color={'field':'snr', 'transform':color_mapper})

        color_bar = ColorBar(color_mapper=color_mapper, ticker=BasicTicker())
        snr_plot.add_glyph(orig_data, snr_dots)
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

        flux_plot.add_tools(bokeh_tools.BoxZoomTool())
        flux_plot.add_tools(bokeh_tools.ResetTool())
        flux_plot.add_tools(bokeh_tools.LassoSelectTool())
        flux_plot.add_tools(bokeh_tools.WheelZoomTool())
        flux_plot.add_tools(bokeh_tools.PanTool())

        hover = bokeh_tools.HoverTool()
        hover.tooltips= [('RightAscension', '@ra'),('Declination', '@dec'),
                         ('magnitude', '@mag'), ('Signal_to_noise', '@snr')]

        flux_plot.add_tools(hover)
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

        snr_plot.add_tools(bokeh_tools.BoxZoomTool())
        snr_plot.add_tools(bokeh_tools.ResetTool())
        snr_plot.add_tools(bokeh_tools.LassoSelectTool())
        snr_plot.add_tools(bokeh_tools.WheelZoomTool())
        snr_plot.add_tools(bokeh_tools.PanTool())


        s2 = ColumnDataSource({'mag':[],'snr':[]})
        flux_v_snr_plot = Plot()
        flux_v_snr_dots = Circle(x='mag', y='snr', size=5,
                      line_color=None,
                      fill_color='blue')


        flux_v_snr_plot.add_glyph(s2, flux_v_snr_dots)

        flux_axis = LinearAxis(formatter=NumeralTickFormatter(format="0.00"),
                             ticker=BasicTicker(desired_num_ticks=4),
                             minor_tick_line_width=2,
                             major_tick_line_width=4,
                             major_tick_out=30,
                             minor_tick_out=5,
                             axis_label='mag')

        snr_axis = LinearAxis(formatter=NumeralTickFormatter(format="0.00"),
                             ticker=BasicTicker(desired_num_ticks=4),
                             minor_tick_line_width=2,
                             major_tick_line_width=4,
                             major_tick_out=30,
                             minor_tick_out=5,
                             axis_label='SNR')

        flux_v_snr_plot.add_layout(flux_axis, 'below')
        flux_v_snr_plot.add_layout(snr_axis, 'left')
        flux_v_snr_plot.x_range = DataRange1d()
        flux_v_snr_plot.y_range = DataRange1d()

        #http://bokeh.pydata.org/en/latest/docs/user_guide/interaction/
        #callbacks.html#userguide-interaction-jscallbacks
        orig_data.callback = CustomJS(args=dict(s2=s2), code="""
            var inds = cb_obj.selected.indices;
            var d1 = cb_obj.data;
            var d2 = s2.data;
            d2['mag'] = [];
            d2['snr'] = [];
            for (var i = 0; i < inds.length; i++){
                d2['mag'].push(d1['mag'][inds[i]]);
                d2['snr'].push(d1['snr'][inds[i]]);
            }
            s2.change.emit();
            """)

        rr = row(flux_plot, snr_plot, flux_v_snr_plot)
        self.add_layout(rr)


###### ACTUALLY EXECUTE ########

SourceCtMetric()
