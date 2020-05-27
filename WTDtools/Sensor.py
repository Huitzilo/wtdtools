# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 15:58:31 2014

@author: viktor

plumy.Sensor - A Metal-Oxide-Sensor representation

The Sensor Class is the lowest link in our Object Oriented Data Model, thus
representing the smallest possible contributor to the Dataset.
There are 6 x 9 x 8 = 432 Sensors in the plumy setup.

"""

import numpy as np
import pandas as pd
import scipy.signal as sp
from WTDtools.base import base


class Sensor(base):
    def __init__(self, gas, loc, voltage, speed, trial, _args, 
                 name, time, readout, baseline, extremum, filt):
                     
        self.is_valid = True
        self.set_name(name)  # assign name
        self.set_time(time)  # assign time
        self.set_data(readout)  # assign data
        self.get_min = extremum[0]
        self.get_max = extremum[1]
        self.get_mean = self._Data.mean()
        self.get_var = self._Data.var()
        super(Sensor, self).__init__(gas=gas, loc=loc, voltage=voltage,
                                     speed=speed, trial=trial, _args=_args)
        #  TODO: Remove ugly double call
        self.set_data(readout)
        self.set_time(time)
        self.set_filter(data=filt)
        

    def __call__(self):
        """
        If instance is called, return Sensor readout as numpy.ndarray.
        """
        return self._Data.get_values()

    def __str__(self):
        """
        If instance is printed, display Sensor information.
        """
        if self.is_valid:
            valid = ''
        else:
            valid = ' -> Invalid!'
        return '> %s |  Mean: %d  | Var: %f  | Min: %d  | Max: %d%s' % \
            (self.Name, self.get_mean, self.get_var, self.get_min, self.get_max, valid)


    def set_valid(self, status=False):
        """
        is_valid attribute setter method, called by SensorBoard validitor.
        """
        assert isinstance(status, bool)
        self.is_valid = status

    property(fset=set_valid, doc='Sensor outlier flag setter.')

    def normalize(self, data, _min, _max):
        """
        Return normalized Sensor readout.
        """
        return (data-_min)/(_max-_min)

    def get_data(self):
        """
        Instance Data getter.
        """
        if hasattr(self, '_Data'):
            return self._Data

    def set_data(self, data):
        """
        Instance Data setter
        """
        assert isinstance(data, (list, np.ndarray, pd.Series))
        # TODO: More robust assertion for data setter.
        self._Data = data

    property(fget=get_data, fset=set_data, doc='Board wide data desciptors.')

    def get_baseline(self):
        if hasattr(self, '_Baseline'):
            return self._Baseline

    def set_baseline(self, baseline):
        """
        Column wide baseline setter. Update child objects when called.
        """
        assert isinstance(baseline, (tuple, list))
        assert len(baseline) == 2
        self._Baseline = (baseline[0], baseline[1])

    property(fget=get_baseline, fset=set_baseline,
             doc='Board wide baseline descriptors.')

    def set_filter(self, order=2, cutoff=None, _btype='low', data=None):
        if isinstance(data, list):
            self._Filter = data
        else:
            super(Sensor, self).set_filter(order, cutoff, _btype)

    property(fget=base.get_filter, fset=set_filter,
             doc='Board wide filter parameter descriptor.')

    @property
    def get_normal(self):
        """
        Normalized Sensor readout getter method.
        """
        return self.normalize(self._Data, self.get_min, self.get_max)

    @property
    def get_filtered(self):
        """
        Low-Pass filtered Sensor readout getter method.
        """
        return sp.filtfilt(self._Filter[0], self._Filter[1], self._Data)

    @property
    def get_fano(self):
        """
        Get fano factor, variance / mean.
        """
        return float(self.get_var / self.get_mean)

    def load(self):
        raise NotImplementedError



