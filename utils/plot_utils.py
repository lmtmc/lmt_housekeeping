import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np
import datetime

group_gap = 100
def add_watermark(fig, watermark_labels, ys, xs):
    now = datetime.datetime.now()
    watermark_index = -1
    for i, label in enumerate(fig.data):
        if label.name in watermark_labels:
            watermark_index = i
            break
    if watermark_index >= 0:
        y = ys[watermark_index]
        x = xs[watermark_index]
        if now - x[-1] > datetime.timedelta(hours=24):
            watermark, watercolor = 'STALE', 'black'
        else:
            watermark = 'WARM' if y[-1] > 0.21 else 'COLD'
            watercolor = 'red' if y[-1] > 0.21 else 'blue'
            if y[-1] == 0:
                watermark, watercolor = "OFF", 'black'

        fig.add_annotation(
            text=f'TolTEC {watermark}',
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=40, color=watercolor),
            opacity=0.5,
            textangle=-30,
            layer="above"
        )
    return fig

def update_plot(plot_data, hours, options, split_value, watermark_labels):

    if not plot_data:
        return go.Figure().add_annotation(text="No data available for the selected time range",
                                          showarrow=False,
                                          font=dict(size=20, color="red"))

    valid_traces = []
    ys, xs = [], []

    # Collect valid traces
    for trace in plot_data:
        temp_data = np.array(trace['y'])
        x_data = np.array(trace['x'])

        scatter = go.Scatter(
            x=x_data,
            y=temp_data,
            name=trace['name'],
            mode='lines',
        )
        valid_traces.append(scatter)
        ys.append(temp_data)
        xs.append(x_data)
    # Set up subplots based on split_value
    if split_value is not None:
        lower_traces = [trace for trace in valid_traces if trace.y[-1] <= split_value]
        upper_traces = [trace for trace in valid_traces if trace.y[-1] > split_value]
        if len(lower_traces) == 0 or len(upper_traces) == 0:
            num_subplots = 1
            subplot_titles = ["All Temperatures"]
        else:
            num_subplots = 2
            subplot_titles = [f"Temperature <= {split_value}", f"Temperature > {split_value}"]
    else:
        num_subplots = 1
        subplot_titles = ["All Temperatures"]

    fig = make_subplots(rows=num_subplots, cols=1, subplot_titles=subplot_titles, shared_xaxes=True)

    # Add traces to the appropriate subplot
    if num_subplots == 2:
        for trace in lower_traces:
            trace.update(legendgroup="lower", legendgrouptitle_text=f"Temperature <= {split_value}")
            fig.add_trace(trace, row=1, col=1)
        for trace in upper_traces:
            trace.update(legendgroup="upper", legendgrouptitle_text=f"Temperature > {split_value}")
            fig.add_trace(trace, row=2, col=1)
        height = 800
    else:
        for trace in valid_traces:
            fig.add_trace(trace, row=1, col=1)
        height = 600

    # Update layout for group and group gap
    fig.update_layout(
        height=height,
        title_text=f"TolTEC Thermetry - Last {hours} hours" if hours > 0 else "TolTEC Thermetry - All Data",
        showlegend=True,
        legend=dict(
            groupclick='toggleitem',
            tracegroupgap=250,  # Adjust this value to control the gap between groups
        ),
    )

    fig.update_xaxes(title_text="Time (UTC)", row=num_subplots, col=1)
    for i in range(1, num_subplots + 1):
        fig.update_yaxes(title_text="Temperature (K)", row=i, col=1)

    # Update axes
    if options and 'log' in options:
        for i in range(1, num_subplots + 1):
            fig.update_yaxes(type="log", row=i, col=1, title_text="Temperature (log K)")

    # Add watermark if necessary
    fig = add_watermark(fig, watermark_labels, ys, xs)

    return fig