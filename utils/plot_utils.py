import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np

group_gap = 100

def update_plot(title, plot_data, hours, options, split_value):

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
        title_text=f"{title} - Last {hours} hours" if hours > 0 else "TolTEC Thermetry - All Data",
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
    return fig