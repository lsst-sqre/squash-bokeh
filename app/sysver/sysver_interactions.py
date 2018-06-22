#from bokeh import events
#from bokeh.models import CustomJS, ResetTool
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
        #callback = CustomJS(args={}, code="""console.log('Got Here!')""")
        #self.plot.js_on_event('reset', callback)
        #reset_tool = ResetTool()
        #reset_tool.js_event_callbacks = {'reset': [callback]}
        #self.plot.add_tools(reset_tool)

    #def reset_avg_temp(self, event):
    #    print("A:", event)
    #    self.update_ave_temp()

    def calculate_avg_temp(self, attr, old, new):

        index = new['1d']['indices']
        if len(index) == 0:
            return

        index.sort()
        self.update_ave_temp(np.mean(np.array(self.cds.data['temperatures'])[index]))
