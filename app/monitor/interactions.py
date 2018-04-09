from layout import Layout


class Interactions(Layout):
    def __init__(self):
        super().__init__()

        self.datasets_widget.on_change('value', self.on_change_dataset)
        self.packages_widget.on_change('value', self.on_change_package)
        self.metrics_widget.on_change('value', self.on_change_metric)
        self.period_widget.on_change('active', self.on_change_period)

    def on_change_package(self, attr, old, new):

        self.selected_package = new

        self.metrics = self.get_metrics(package=self.selected_package)
        metric_names = self.get_sorted(data=self.metrics, key='name')
        self.selected_metric = metric_names[0]

        # This will trigger a metric change, and will update the datasource
        # with measurements for the new selected metric.

        # We can preserve the code changes and the period selection

        self.metrics_widget.options = metric_names

        self.load_measurements(self.selected_dataset, self.selected_metric,
                               self.selected_period)

        self.update_datasource()

        self.update_header()
        self.update_plot()
        self.update_footnote()
        self.update_table()

    def on_change_dataset(self, attr, old, new):

        self.selected_dataset = new

        self.load_data(self.selected_dataset, self.selected_metric,
                       self.selected_period)

        self.update_plot()
        self.update_table()

    def on_change_period(self, attr, old, new):

        self.selected_period = self.periods['periods'][new]

        self.load_data(self.selected_dataset, self.selected_metric,
                       self.selected_period)

        self.update_plot()
        self.update_table()

    def on_change_metric(self, attr, old, new):

        self.selected_metric = new

        # No need to reload code changes here
        self.load_measurements(self.selected_dataset, self.selected_metric,
                               self.selected_period)

        self.update_datasource()

        self.update_plot_title()
        self.update_plot()
        self.update_footnote()
        self.update_table()
