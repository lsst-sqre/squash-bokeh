import numpy as np
from bokeh.models.ranges import Range1d


from amx_layout import Layout

class AstrometryCheck(Layout):
    """Add app interactions
    See https://bokeh.pydata.org/en/latest/docs/user_guide/
    interaction.html
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.snr_slider.on_change('value', self.on_change_slider)
        self.datasets_widget.on_change('value', self.on_change_datasets)
        self.filters_widget.on_change('value', self.on_change_filters)
        self.plot_widget.on_click(self.on_plot_click)


    def redraw_full_histogram(self):

        # Redraw the selected histogram
        frequencies, _ = np.histogram(self.cds.data['dist'],
                                      self.edges)

        self.full_hist.data_source.data['right'] = frequencies

        # attempt to adjust x_range
        hmax = max(frequencies) * 1.1
        self.hist.x_range = Range1d(0, hmax)


    def redraw_selected_histogram(self):

        # Redraw the selected histogram
        frequencies, _ = np.histogram(self.selected_cds.data['dist'],
                                      self.edges)

        self.selected_hist.data_source.data['right'] = frequencies

        # Recompute n, median and rms
        n = self.selected_cds.data['dist'].size
        median = np.median(self.selected_cds.data['dist'])
        rms = np.sqrt(np.mean(np.square(self.selected_cds.data['dist'])))

        # Update annotations
        self.snr_span.location = self.snr_cut
        self.rms_span.location = rms

        self.n_label.text = 'N = {}'.format(n)
        self.median_label.text = 'Median = {:3.2f} marcsec'.format(median)
        self.snr_label.text = 'SNR > {:3.2f}'.format(self.snr_cut)

        self.rms_label.text = "RMS = {:3.2f} marcsec".format(rms)

    def on_change_slider(self, attr, old, new):
        """ Update scatter plot, histogram and
        annotations based on the new SNR value.
        """
        self.snr_cut = new

        self.message = str()
        self.update_header()

        # Update the selected sample
        index = np.array(self.cds.data['snr']) > float(self.snr_cut)

        snr = np.array(self.cds.data['snr'])[index]
        dist = np.array(self.cds.data['dist'])[index]

        self.selected_cds.data = dict(snr=snr, dist=dist)

        self.redraw_selected_histogram()

    def on_change_datasets(self, attr, old, new):

        self.selected_dataset = new
        self.message = str()
        self.update_filters_widget()
        
    def on_change_filters(self, attr, old, new):

        self.selected_filter = new
        self.message = str()
       
    def on_plot_click(self):
       
        self.update_header()

        self.load_data()
       
        self.redraw_full_histogram()
        self.redraw_selected_histogram()
