import netCDF4
import io
import os

class ToltecBaseFile:
    def __init__(self, file_input):
        self.nc = None
        self.data = {}

        if isinstance(file_input, str) and os.path.isfile(file_input):
            self.nc = netCDF4.Dataset(file_input)
        elif isinstance(file_input, io.BytesIO):
            self.nc = netCDF4.Dataset('inmemory', memory=file_input.read())
        else:
            raise ValueError("Invalid file input. Must be a valid file path or a BytesIO object.")

        self._read_variables()

    def _read_variables(self):
        raise NotImplementedError("Subclasses must implement this method")

    def __del__(self):
        if self.nc:
            self.nc.close()