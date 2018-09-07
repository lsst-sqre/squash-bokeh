from bokeh.models import CustomJS
import numpy as np

from sysver_layout import Layout


class Interactions(Layout):
    """Add app interactions
    See https://bokeh.pydata.org/en/latest/docs/user_guide/
    interaction.html
    """

    def __init__(self):
        super().__init__()

        self.pcircle.data_source.on_change('selected', self.calculate_average)
        text = self.format_metric_text()
        callback = CustomJS(args=dict(div=self.metric_widget),
                            code="div.text = '{}'".format(text))

        self.plot.js_on_event('reset', callback)

    def calculate_average(self, attr, old, new):

        index = new['1d']['indices']
        if len(index) == 0:
            return

        index.sort()
        z_data = self.cds.data['z']
        self.update_metric_display(np.mean(np.array(z_data)[index]))
