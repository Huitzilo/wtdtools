# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 11:43:35 2014

@author: viktor

plumy.SensorBoard - SensorBoard repsresentation holding plumy.Sensor instances

The SensorBoard class is the middle link in our Object Oriented Data Model.
After construction a SensorBoard instance holds 8 Sensor class instances.
There are a total of 6 x 9 = 54 SensorBoards in the plumy setup.  
"""

import numpy as np
from .base import base
from .Sensor import Sensor


class SensorBoard(base):

    def __init__(self, gas, loc, voltage, speed, trial, _args,
                 name, time, readout, baseline, filt):
        self._init = False

        self.set_name(name)  # assign name
        
        super(SensorBoard, self).__init__(gas=gas, loc=loc, voltage=voltage,
                                         speed=speed, trial=trial, _args=_args)
        self.set_data(readout)  # assign data
        self.set_time(time)  # assign time
        self.set_baseline(baseline)  # assign baseline
        self.set_filter(data=filt)  # assign filter
        self.update()  # construct Sensor instances

        self = self.validate()  # find baaad sensors
        self._init = True

    def __call__(self):
        """
        If instance is called, return SensorBoard readout as numpy.ndarray.
        """
        if hasattr(self, '_Data'):
            return self.get_all
        else:
            print('\nNo data for', self)

    def __str__(self):
        """
        If instance is printed, display SensorBoard information.
        """
        if self._init:
            return '\n\n'+'#'*60+'\n\n  %s:\n\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s \
                    \n\nMin.: %i Ohm (Sensor %d)\tMax.: %i Ohm (Sensor %d)\tMax. Variance: %d (Sensor %i)' % \
                    (self.Name, self.Sensor1, self.Sensor2, self.Sensor3,
                     self.Sensor4, self.Sensor5, self.Sensor6, self.Sensor7,
                     self.Sensor8, self.get_min[1], self.get_min[0], self.get_max[1],
                     self.get_max[0], self.get_var[1], self.get_var[0])
        else:
            return '\n\n'+'#'*60+'\n\n  %s:\n' % self.Name

    def update(self):
        """
        Initialize eight instances of plumy.Sensor objects.
        """

        if self._init:
            del self.Sensor1
            del self.Sensor2
            del self.Sensor3
            del self.Sensor4
            del self.Sensor5
            del self.Sensor6
            del self.Sensor7
            del self.Sensor8

        self.Sensor1 = Sensor(self.Gas,
                              self.Location, self.SensorVoltage,
                              self.FanSpeed, self.Trial, self._args, 'Sensor 1',
                              self._Time, self._Data[0], self._Baseline,
                              self._Extrema[1], self._Filter)

        self.Sensor2 = Sensor(self.Gas,
                              self.Location, self.SensorVoltage,
                              self.FanSpeed, self.Trial, self._args, 'Sensor 2',
                              self._Time, self._Data[1], self._Baseline,
                              self._Extrema[2], self._Filter)

        self.Sensor3 = Sensor(self.Gas,
                              self.Location, self.SensorVoltage,
                              self.FanSpeed, self.Trial, self._args, 'Sensor 3',
                              self._Time, self._Data[2], self._Baseline,
                              self._Extrema[3], self._Filter)

        self.Sensor4 = Sensor(self.Gas,
                              self.Location, self.SensorVoltage,
                              self.FanSpeed, self.Trial, self._args, 'Sensor 4',
                              self._Time, self._Data[3], self._Baseline,
                              self._Extrema[4], self._Filter)

        self.Sensor5 = Sensor(self.Gas,
                              self.Location, self.SensorVoltage,
                              self.FanSpeed, self.Trial, self._args, 'Sensor 5',
                              self._Time, self._Data[4], self._Baseline,
                              self._Extrema[5], self._Filter)

        self.Sensor6 = Sensor(self.Gas,
                              self.Location, self.SensorVoltage,
                              self.FanSpeed, self.Trial, self._args, 'Sensor 6',
                              self._Time, self._Data[5], self._Baseline,
                              self._Extrema[6], self._Filter)

        self.Sensor7 = Sensor(self.Gas,
                              self.Location, self.SensorVoltage,
                              self.FanSpeed, self.Trial, self._args, 'Sensor 7',
                              self._Time, self._Data[6], self._Baseline,
                              self._Extrema[7], self._Filter)

        self.Sensor8 = Sensor(self.Gas,
                              self.Location, self.SensorVoltage,
                              self.FanSpeed, self.Trial, self._args, 'Sensor 8',
                              self._Time, self._Data[7], self._Baseline,
                              self._Extrema[8], self._Filter)

    def validate(self):
        """
        Find outliers by constraining board-wide Sensor responses to
        +/- factor 3 of the centroid mean. For every min/max, pop processed
        from stack and proceed with remaining readouts. Repeat until stack
        contains single element.
        """
        up_mins = [ex[0] for ex in list(self._Extrema.values())]
        lo_mins = list(up_mins)
        while len(up_mins) > 1:
            max_min = max(up_mins)
            min_min = min(lo_mins)
            max_idx = up_mins.index(max(up_mins))
            min_idx = lo_mins.index(min(lo_mins))
            del up_mins[max_idx]
            del lo_mins[min_idx]
            max_mean = np.mean(up_mins)
            min_mean = np.mean(lo_mins)
            if max_min >= 3*max_mean:
                obj = getattr(self, 'Sensor%i' % (max_idx+1))
                obj.set_valid(False)
            elif min_min <= min_mean/3:
                obj = getattr(self, 'Sensor%i' % (min_idx+1))
                obj.set_valid(False)
        return self

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
        assert isinstance(data, (list, np.ndarray))
        # TODO: More robust assertion for data setter.
        self._Data = data
        if self._init:
            self.update()

    property(fget=get_data, fset=set_data, doc='Board wide data desciptors.')

    @property
    def get_time(self):
        if hasattr(self, '_Time'):
            return self._Time

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
        self._Extrema = self.get_extrema
        if self._init:
            self.update()

    property(fget=get_baseline, fset=set_baseline,
             doc='Board wide baseline descriptors.')

    @property
    def get_extrema(self):
        # bl = range(self._Baseline[0], self._Baseline[-1])
        # dl = range(self._Baseline[-1]+1, len(self._Data[0]))
        return {1: (self._Data[0].min(),
                    self._Data[0].max()),
                2: (self._Data[1].min(),
                    self._Data[1].max()),
                3: (self._Data[2].min(),
                    self._Data[2].max()),
                4: (self._Data[3].min(),
                    self._Data[3].max()),
                5: (self._Data[4].min(),
                    self._Data[4].max()),
                6: (self._Data[5].min(),
                    self._Data[5].max()),
                7: (self._Data[6].min(),
                    self._Data[6].max()),
                8: (self._Data[7].min(),
                    self._Data[7].max())}

    def set_filter(self, order=2, cutoff=None, _btype='low', data=None):
        """
        Overwrite base-class setter. Updates child objects when called.
        """
        if isinstance(data, list):
            self._Filter = data
            if self._init:
                self.Sensor1.set_filter(data=data)
                self.Sensor2.set_filter(data=data)
                self.Sensor3.set_filter(data=data)
                self.Sensor4.set_filter(data=data)
                self.Sensor5.set_filter(data=data)
                self.Sensor6.set_filter(data=data)
                self.Sensor7.set_filter(data=data)
                self.Sensor1.set_filter(data=data)
        else:
            super(SensorBoard, self).set_filter(order, cutoff, _btype)
            if self._init:
                self.Sensor1.set_filter(order, cutoff, _btype)
                self.Sensor2.set_filter(order, cutoff, _btype)
                self.Sensor3.set_filter(order, cutoff, _btype)
                self.Sensor4.set_filter(order, cutoff, _btype)
                self.Sensor5.set_filter(order, cutoff, _btype)
                self.Sensor6.set_filter(order, cutoff, _btype)
                self.Sensor7.set_filter(order, cutoff, _btype)
                self.Sensor8.set_filter(order, cutoff, _btype)

    property(fget=base.get_filter, fset=set_filter,
             doc='Board wide filter parameter descriptor.')

    @property
    def get_normal(self):
        """
        Normalized Sensor readout getter method. Board-wide parameters.
        """
        return self.normalize(self.get_all, self.get_min[1], self.get_max[1])

    @property
    def get_max(self):
        """
        The board-wide maximum Sensor response. Is returned as a tuple of
        (Sensor, value).
        """
        valid = self.get_valid
        maxs = [ex[1] for i, ex in enumerate(self._Extrema.values()) if valid[i]]
        return (maxs.index(max(maxs))+1,max(maxs))


    @property
    def get_min(self):
        """
        The board-wide minimum Sensor response. Is returned as a tuple of
        (Sensor, value).
        """
        valid = self.get_valid
        mins = [ex[0] for i, ex in enumerate(self._Extrema.values()) if valid[i]]
        return (mins.index(min(mins))+1, min(mins))

    @property
    def get_filtered(self):
        """
        Low-Pass filtered Sensor readout getter method.
        """
        import scipy.signal as sp

        filt = []
        for i in self._Data:
            filt.append(sp.filtfilt(self._Filter[0],
                                    self._Filter[1],
                                    i))
        return np.transpose(filt)

    @property
    def get_valid(self):
        """
        Getter for a board-wide list of Sensor.is_valid attributes.
        """
        valid = [self.Sensor1.is_valid, self.Sensor2.is_valid, self.Sensor3.is_valid,
                 self.Sensor4.is_valid, self.Sensor5.is_valid, self.Sensor6.is_valid,
                 self.Sensor7.is_valid, self.Sensor8.is_valid]
        return valid

    @property
    def get_var(self):
        """
        Getter for a board-wide list of Sensor.var (variance).
        Returns a tuple of (Sensor Position, Max. Variance).
        """
        var = [self.Sensor1.get_var, self.Sensor2.get_var, self.Sensor3.get_var,
               self.Sensor4.get_var, self.Sensor5.get_var, self.Sensor6.get_var,
               self.Sensor7.get_var, self.Sensor8.get_var]
        return (var.index(max(var))+1, max(var))

    @property
    def get_mean(self):
        """
        Getter for a board-wide list of Sensor.mean .
        Returns a tuple of (Sensor Position, Max. Mean).
        """
        mean = [self.Sensor1.get_mean, self.Sensor2.get_mean, self.Sensor3.get_mean,
               self.Sensor4.get_mean, self.Sensor5.get_mean, self.Sensor6.get_mean,
               self.Sensor7.get_mean, self.Sensor8.get_mean]
        return (mean.index(max(mean))+1, max(mean))

    @property
    def get_fano(self):
        """
        Getter for a board-wide list of Fano factor (var/mean).
        Returns a tuple of (Sensor Position, Max. fano factor).
        """
        fano = [self.Sensor1.get_fano, self.Sensor2.get_fano, self.Sensor3.get_fano,
               self.Sensor4.get_fano, self.Sensor5.get_fano, self.Sensor6.get_fano,
               self.Sensor7.get_fano, self.Sensor8.get_fano]
        return (fano.index(max(fano))+1, max(fano))

    @property
    def get_all(self):
        """
        Getter for a baord-wide list of Sensor readouts.
        Columns correspond with (Sensor position - 1).
        """
        allSensors = np.transpose(np.array([self.Sensor1(),
                                  self.Sensor2(),
                                  self.Sensor3(),
                                  self.Sensor4(),
                                  self.Sensor5(),
                                  self.Sensor6(),
                                  self.Sensor7(),
                                  self.Sensor8()]))
        return allSensors

    @property
    def iter_sensors(self):
        """
        Return iterator over all Sensor objects.
        """
        if self._init:
            return iter([self.Sensor1,
                         self.Sensor2,
                         self.Sensor3,
                         self.Sensor4,
                         self.Sensor5,
                         self.Sensor6,
                         self.Sensor7,
                         self.Sensor8])



