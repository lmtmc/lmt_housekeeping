TolTEC Dashboard
================
Overview
--------
TolTEC Dashboard is a web application that provides a user-friendly interface to access TolTEC data products. The dashboard is built using the Dash framework, which is a Python web application framework that is built on top of Flask, Plotly.js, and React.js. The dashboard is designed to be user-friendly and intuitive, and it provides a variety of tools to visualize and analyze TolTEC data products (e.g., Thermetry, Dilution Fridg, Cryocmp etc.).

Features
--------
- Interactive data visualization
- File upload functionality for data input
- Time range selection for data display
- seperate dashboards for Thermetry, Dilution Fridg, Cryocmp etc.

Installation
------------
```
git clone https://github.com/lmtmc/netcdf_plot.git
cd netcdf_plot
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Project Structure
-----------------
```netcdf_plot/
│
├── app.py
├── assets (css, images, js)
├── layouts (dash layout for each dashboard)
├── data_files (class to read netcdf files)
├── callbacks (dash callbacks for each dashboard)
├── requirements.txt
└── README.md
```
Adding a new dashboard
----------------------
1. Create a new layout file in the layouts directory and add it to the menubar.
2. Create a new callback file in the callbacks directory and add it to callbacks.py.
3. Create a new class in the data_files directory to read the netCDF file.
4. Add the new layout and callback to the app.py file.
5. Add the new path in the config.yaml file.
Running the application
-----------------------
```
python app.py
```
The application will be running on http://127.0.0.1:8050/

Usage
-----
1. Use the vertical tabs on the left side of the dashboard to navigate between different data products.
2. In each dashboard:
   - Use the file select to select a netCDF file.
   - Select the time range for data display.
   - Additional options are available for each dashboard.
3. The data will be displayed in the form of a plot.


