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
source venv/bin/activate
pip install -r requirements.txt
```

Project Structure
-----------------
```netcdf_plot/
│
├── app.py
├── layouts (dash layout for each dashboard)
├── toltec_files (class to read netcdf files)
├── callbacks (dash callbacks for each dashboard)
├── requirements.txt
└── README.md
```
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
   - Use the file upload button to upload a netCDF file.
   - Select the time range for data display.
   - Additional options are available for each dashboard.
3. The data will be displayed in the form of a plot.


