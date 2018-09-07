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

        self.pcircle.data_source.on_change('selected', self.calculate_avg_temp)
        callback = CustomJS(args=dict(div=self.ave_temp_widget),
                            code="div.text = '{}'".format(self.format_ave_temp_text()))

        self.plot.js_on_event('reset', callback)

    def calculate_avg_temp(self, attr, old, new):

        index = new['1d']['indices']
        if len(index) == 0:
            return

        index.sort()
        self.update_ave_temp(np.mean(np.array(self.cds.data['z'])[index]))
