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

        metric_names = self.get_sorted(data=self.metrics,
                                       key='name')

        self.metrics_widget.options = metric_names

        self.selected_metrics = [metric_names[0]]

        self.update_header()

        self.update_tabs()

    def on_change_dataset(self, attr, old, new):

        self.selected_dataset = new

        self.load_monitor_data(self.selected_dataset, self.selected_period)

        self.update_header()

        self.update_tabs()

    def on_change_period(self, attr, old, new):

        self.selected_period = self.periods['periods'][new]

        self.load_monitor_data(self.selected_dataset, self.selected_period)

        self.update_tabs()

    def on_change_metric(self, attr, old, new):

        metric = new[0]

        if metric in self.selected_metrics:
            self.selected_metrics.remove(metric)
        else:
            self.selected_metrics.append(metric)

        # Make sure at least one metric is selected
        if not self.selected_metrics:
            self.selected_metrics = [metric]

        self.update_tabs()
