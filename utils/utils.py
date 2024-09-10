import numpy as np
import datetime

def filter_data_by_hours(xdata, ydata, hours):
    try:
        if hours > 0:
            xmax = max(np.max(x) for x in xdata if x.size > 0 and np.max(x) > 0)
            xmin = xmax - hours * 3600
        else:
            xmin = min(np.min(x) for x in xdata if x.size > 0 and np.min(x) > 0)
            xmax = max(np.max(x) for x in xdata if x.size > 0 and np.max(x) > 0)
    except ValueError as e:
        print(f"Error calculating xmax or xmin: {e}")
        return xdata, ydata

    mask = (xdata >= xmin) & (xdata <= xmax)
    x_filtered = xdata[mask]
    y_filtered = [y[mask] for y in ydata]

    return x_filtered, y_filtered

def prepare_plot_data(xdata, ydata, labels, hours):
    xdata, ydata = filter_data_by_hours(xdata, ydata, hours)
    x_datetime = [datetime.datetime.utcfromtimestamp(ts) for ts in xdata]
    plot_data = [{'x': x_datetime, 'y': y.tolist(), 'name': label} for y, label in zip(ydata, labels)]
    return plot_data

def get_data_and_labels(data, data_keys, label_mapping):
    xdata = data.get('time', [])
    ydata = []
    labels = []
    for key in data_keys:
        if key in data:
            ydata.append(data[key])
            labels.append(label_mapping.get(key, key))
    return xdata, ydata, labels