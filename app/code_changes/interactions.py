from layout import Layout


class Interactions(Layout):
    def __init__(self):
        super().__init__()

        self.datasets_widget.on_change('value', self.on_change_dataset)
        self.filters_widget.on_change('value', self.on_change_filter)
        self.packages_widget.on_change('value', self.on_change_package)
        self.metrics_widget.on_change('value', self.on_change_metric)
        self.period_widget.on_change('active', self.on_change_period)

    def on_change_package(self, attr, old, new):

        self.selected_package = new

        self.logger.debug("Changed package: {}".format(self.selected_package))

        self.metrics = self.get_metrics(package=self.selected_package)

        self.selected_metric = self.metrics['metrics'][0]

        self.metrics_meta = self.get_metrics_meta(self.selected_package)

        self.metrics_widget.options = self.metrics['metrics']
        self.selected_metric = self.metrics['metrics'][0]

        # This will trigger a metric change
        self.metrics_widget.value = self.selected_metric

    def on_change_dataset(self, attr, old, new):

        self.selected_dataset = new
        self.logger.debug("Changed dataset: {}".format(self.selected_dataset))

        self.filters = self.get_dataset_filters(self.selected_dataset)
        self.filters_widget.options = self.filters

        self.selected_filter = self.filters[0]

        # This will trigger a filter change
        self.filters_widget.value = self.selected_filter

    def on_change_filter(self, attr, old, new):

        self.selected_filter = new
        self.logger.debug("Changed filter: {}".format(self.selected_filter))

        self.load_data()

        self.update_plot()
        self.update_table()

    def on_change_period(self, attr, old, new):

        self.selected_period = self.periods['periods'][new]
        self.logger.debug("Changed period: {}".format(self.selected_period))

        self.load_data()

        self.update_plot()
        self.update_table()

    def on_change_metric(self, attr, old, new):

        self.selected_metric = new
        self.logger.debug("Changed metric: {}".format(self.selected_metric))

        self.load_measurements()
        self.update_datasource()

        self.update_plot_title()
        self.update_plot()
        self.update_footnote()
        self.update_table()
