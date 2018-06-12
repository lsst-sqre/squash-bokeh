from bokeh.models import Plot
from bokeh.models import ColumnDataSource
from bokeh.models import Range, Range1d, DataRange1d, FactorRange
from bokeh.models import LinearAxis, CategoricalAxis
from bokeh.models import LabelSet

from bokeh.models.scales import CategoricalScale
from bokeh.models.markers import Circle
from bokeh.models.glyphs import HBar, Segment
from bokeh.models.widgets import Div

from bokeh.palettes import OrRd, Blues
from bokeh.layouts import widgetbox, row, column


def make_kpm_plots(source):

    title_widget = Div(text="<h3>Astrometry</h3>")
    title = widgetbox(title_widget)

    p1 = Plot(x_range=Range1d(-100, 100),
              y_range=FactorRange(factors=source.data['metrics']))

    p1.plot_height = 400
    p1.plot_width = 400
    p1.y_scale = CategoricalScale()

    p1.outline_line_color = None
    p1.title.text = '% deviation from design'
    p1.title.align = 'center'

    source.data['deviation'] = [(value - design) / design * 100
                                for value, design in
                                zip(source.data['values'],
                                    source.data['design'])]

    source.data['color'] = [OrRd[3][1] if x > 0 else Blues[3][1]
                            for x in source.data['deviation']]

    height = 0.5

    hbar = HBar(y='metrics', left=0, right='deviation', line_color='color',
                fill_color='color', height=height)

    p1.add_glyph(source, hbar)

    yaxis = CategoricalAxis()

    yaxis.fixed_location = 0
    yaxis.major_label_standoff = 100
    yaxis.major_label_text_font_size = '14pt'

    p1.add_layout(yaxis, 'left')

    source.data['x_offset'] = [10 if x > 0 else -35 for x in
                               source.data['deviation']]

    source.data['percentage'] = ["{}%".format(int(x)) for x in
                                 source.data['deviation']]

    percentage = LabelSet(x='deviation', y='metrics', text='percentage',
                          x_offset='x_offset', text_font_size="10pt",
                          level='glyph', source=source)

    p1.add_layout(percentage)

    p1.toolbar.logo = None

    p2 = Plot(x_range=DataRange1d(),
              y_range=FactorRange(factors=source.data['metrics']))

    p2.plot_height = 400
    p2.plot_width = 400
    p2.outline_line_color = None

    p2.y_scale = CategoricalScale()

    height = 0.5
    hbar = HBar(y='metrics', left='stretch', right='minimum',
                line_color='lightgray', fill_color='lightgray',
                height=height)

    p2.add_glyph(source, hbar)

    source.data['y0'] = [(x, -height / 2) for x in source.data['metrics']]
    source.data['y1'] = [(x, height / 2) for x in source.data['metrics']]

    segment = Segment(x0='design', y0="y0", x1='design', y1='y1',
                      line_color='black', line_width=4)

    p2.add_glyph(source, segment)

    xaxis = LinearAxis()
    xaxis.axis_label = 'AMx (marcsec)'

    p2.add_layout(xaxis, 'below')

    circle = Circle(x='values', y='metrics', size=16,
                    line_color='color', fill_color='color')

    p2.add_glyph(source, circle)

    source.data['formated_values'] = ["{:.1f}".format(x) for x in
                                      source.data['values']]

    labels = LabelSet(x='values', y='metrics', text='formated_values',
                      text_font_size='10pt', x_offset='x_offset',
                      y_offset=-7.5, level='glyph', source=source)

    p2.add_layout(labels)

    p2.toolbar.logo = None

    return column(title, row(p1, p2))
