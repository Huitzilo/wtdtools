# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 13:25:19 2014

@author: viktor

plum.base - Template for plumy's SensorColumn & SensorBoard & Sensor class

Holds attributes and methods used in every one of the aformentioned classes. 
"""

import numpy as np
import scipy.signal as sp


class base(object):
    def __init__(self, gas, loc, voltage, speed, trial, _args):
        assert isinstance(gas, str)
        assert isinstance(loc, str)
        assert isinstance(voltage, str)
        assert isinstance(speed, str)
        assert isinstance(trial, int)
        assert isinstance(_args, dict)

        self.Gas = gas
        self.Location = loc
        self.SensorVoltage = voltage
        self.FanSpeed = speed
        self.Trial = trial
        self._args = _args

        self._Time = None
        self._Data = None
        self._Filter = None

        self.Type = self.__class__.__name__

        if self._args['verbose']:
            print(self)

    def __str__(self):
        return '> %s:\n\n\t+ ' \
            '+ Gas: %s\n\t+ Location: %s\n\t+ SensorVoltage: %s\n\t' \
            '+ FanSpeed: %s\n\t+ Verbose: %s' % \
            (self.Type, self.Gas, self.Location,
             self.SensorVoltage, self.FanSpeed, self._args['verbose'])

    def __call__(self):
        if hasattr(self, '_Data'):
            return self._Data
        else:
            print('\nNo data for', self)

    def get_name(self):
        """
        Istance name getter.
        """
        if hasattr(self, 'Name'):
            return self.Name

    def set_name(self, name):
        """
        Instance name setter.
        """
        assert isinstance(name, str)
        self.Name = name

    property(fget=get_name, fset=set_name, doc='Object name descriptors.')

    @property
    def sample_rate(self):
        if hasattr(self, '_Time'):
            return (self._Time.size/float(self._Time[-1]))*1000  # in Hz

    def get_time(self):
        if hasattr(self, '_Data'):
            return self._Data.index.to_numpy()

    def set_time(self, time):
        assert isinstance(time, (list, np.ndarray))
        self._Time = time

    property(fget=get_time, fset=set_time, doc='Base class time descriptors.')

    def get_filter(self):
        if hasattr(self, '_Filter'):
            return self._Filter

    def set_filter(self, order=2, cutoff=None, _btype='low'):
        """
        Change the parameters of the Butterworth filter.
        """
        assert isinstance(order, int)
        assert isinstance(cutoff, float) or not cutoff
        assert _btype in ['low', 'high', 'band']
        if not cutoff:
            cutoff = 1/(self.sample_rate / 2)
        self._Filter = sp.butter(order, cutoff, btype=_btype)

    property(fget=get_filter, fset=set_filter,
             doc='Base class filter paramter descriptor.')


