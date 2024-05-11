"""Lab 6: Observability module
See study note-taking at
    assets/observability/README.md
    assets/observability/outcome/README.md
"""

from aws_cdk import (
    aws_cloudwatch as cloudwatch,
    Duration as duration
)
from constructs import Construct


class CloudwatchDashboardConstruct(Construct):

    def __init__(self, scope: Construct, id_: str):
        super().__init__(scope, id_)

        build_rate = cloudwatch.GraphWidget(
            title="Build Successes and Failures",
            width=6,
            height=6,
            view=cloudwatch.GraphWidgetView.PIE,
            left=[
                cloudwatch.Metric(
                    namespace="AWS/CodeBuild",
                    metric_name="SucceededBuilds",
                    statistic='sum',
                    label='Succeeded Builds',
                    period=duration.days(30)
                ),
                cloudwatch.Metric(
                    namespace="AWS/CodeBuild",
                    metric_name="FailedBuilds",
                    statistic='sum',
                    label='Failed Builds',
                    period=duration.days(30)
                )
            ]
        )

        self.dashboard = cloudwatch.Dashboard(
            self, 'CICD_Dashboard',
            dashboard_name='CICD_Dashboard',
            widgets=[
                [build_rate]
            ]
        )

        self.add_additional_widget()

    def add_additional_widget(self):
        """
        Add Additional Widgets

        Now that we have defined our dashboard and added a sample widget, we are going to explore additional
        out-of-the-box Amazon CloudWatch visualizations that are available from AWS CodeBuild. In this section,
        we will describe the additional visualization types and provide code snippets to add to your existing
        dashboard. Feel free to add any or all of the visualizations listed below to your existing dashboard.
        """

        # Single Value Widget
        #
        # First off, we will start with the SingleValueWidget which allows users to post a numerical value to
        # a dashboard. In our example, it will be the total number of builds over the user-specified time period.
        # You will also need to add the new widget to the dashboard, which is highlighted below. Each widget added
        # to the dashboard will be separated by a comma.

        builds_count = cloudwatch.SingleValueWidget(
            title="Total Builds",
            width=6,
            height=6,
            metrics=[
                cloudwatch.Metric(
                    namespace="AWS/CodeBuild",
                    metric_name="Builds",
                    statistic='sum',
                    label='Builds',
                    period=duration.days(30)
                )
            ]
        )
        self.dashboard.add_widgets(builds_count)

        # Gauge Widget
        #
        # For our next addition, we will be adding two widgets that both use the GaugeWidget type. The first will
        # display the average duration of build times, and the second will show the average time the build is in
        # the Queued state.

        average_duration = cloudwatch.GaugeWidget(
            title="Average Build Time",
            width=6,
            height=6,
            metrics=[
                cloudwatch.Metric(
                    namespace="AWS/CodeBuild",
                    metric_name="Duration",
                    statistic='Average',
                    label='Duration',
                    period=duration.hours(1)
                )
            ],
            left_y_axis={
                'min': 0,
                'max': 300,
            }
        )

        queued_duration = cloudwatch.GaugeWidget(
            title="Build Queue Duration",
            width=6,
            height=6,
            metrics=[
                cloudwatch.Metric(
                    namespace="AWS/CodeBuild",
                    metric_name="QueuedDuration",
                    statistic='Average',
                    label='Duration',
                    period=duration.hours(1)
                )
            ],
            left_y_axis={
                'min': 0,
                'max': 60,
            }
        )
        self.dashboard.add_widgets(average_duration, queued_duration)

        # Graph Widget
        #
        # Another important widget type is the Graph. The Graph will let you plot data over time and let you visualize
        # the changes. One scenario where this would be useful is keeping track of pipeline stages watching for the
        # time taken for a given step to grow.
        #
        # In this example we will graph the code checkout duration over time.
        #
        # Add the GraphWidget.

        download_duration = cloudwatch.GraphWidget(
            title="Checkout Duration",
            width=24,
            height=5,
            left=[
                cloudwatch.Metric(
                    namespace="AWS/CodeBuild",
                    metric_name="DownloadSourceDuration",
                    statistic='max',
                    label='Duration',
                    period=duration.minutes(5),
                    color=cloudwatch.Color.PURPLE
                )
            ]
        )
        self.dashboard.add_widgets(download_duration)
