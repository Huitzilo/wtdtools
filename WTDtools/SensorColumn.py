# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 11:42:40 2014

@author: viktor

plumy.SensorColumn - SensorColumn respresentation holding SensorBoard instances

The SensorBoard class is the top link in our Object Oriented Data Model.
After construction a SensorColumn instance holds 9 SensorBoard class instances.
There are a total of 6 SensorColumns in the plumy setup.  
"""

import numpy as np
import pandas as pd
import scipy as sp
import os
from .SensorBoard import SensorBoard
from .base import base
import zipfile

class SensorColumn(base):

    def __init__(self, data_location, gas, loc, voltage, speed, trial, _args):
        """
        data_location: URL-style path to the location of the data. Currently
            supported are the following:
            file://<path> - <path> points to the location of the desired file, 
                i.e. the full path to the desired sensor column.
            hdf://<path> - <path> points to the location of the HDFcache with 
                the data. The location of the desired data in the HDFcache is 
                inferred from the gas, loc, voltage, speed, and trial params.
            zip://<path> - <path> contains the path to the WTD_upload.zip file,
                and continues with the path to the desired data in the zip 
                file. E.g.: /User/enose/WTD_upload.zip/CO_1000/L2/1234.csv .
        """
        self._init = False
        super(SensorColumn, self).__init__(gas=gas, 
                                            loc=loc, 
                                            voltage=voltage, 
                                            speed=speed, 
                                            trial=trial, 
                                            _args=_args)
        if _args['use_HDFcache']:
            try:
                self.HDFcache = _args['HDF_cache_location']
            except KeyError:
                raise Warning('Have been told to use the HDFcache, \n' +\
                    "but caller didn't disclose its location.\n" + \
                    'Continuing without HDFcache.')
                self.HDFcache = None
        else:
            self.HDFcache = None
            
        self.load(data_location)
        
        self.set_name('Column %s' % loc)

        self.set_time(self.get_time())
        self.set_filter()
        baseline = self.get_baseline()
        if baseline is None: # No readings from mfc sensor 
            print(('Warning:\n{}:'.format(data_location)))
            print("No readings from mass flow controller, don't expect useful data.")
            print("Assuming 10 s baseline.\n")
            baseline = (0,1000)
        self.set_baseline(baseline)
        
        if self._args['drop_duplicates']:
            self.drop_duplicates()
        if self._args['fill_gaps']:
            pass
            # self.fill_gaps(rate=20, window=150)
        if self._args['resample']:
            self.resample(rate=100)
        
        self.Board1 = SensorBoard(gas, loc, voltage, speed,
                                  trial, _args, 'Board 1', self._Time,
                                  [self._Data.B1S1, self._Data.B1S2,
                                   self._Data.B1S3, self._Data.B1S4,
                                   self._Data.B1S5, self._Data.B1S6,
                                   self._Data.B1S7, self._Data.B1S8],
                                  self._Baseline, self._Filter)

        self.Board2 = SensorBoard(gas, loc, voltage, speed,
                                  trial, _args, 'Board 2', self._Time,
                                  [self._Data.B2S1, self._Data.B2S2,
                                   self._Data.B2S3, self._Data.B2S4,
                                   self._Data.B2S5, self._Data.B2S6,
                                   self._Data.B2S7, self._Data.B2S8],
                                  self._Baseline, self._Filter)

        self.Board3 = SensorBoard(gas, loc, voltage, speed,
                                  trial, _args, 'Board 3', self._Time,
                                  [self._Data.B3S1, self._Data.B3S2,
                                   self._Data.B3S3, self._Data.B3S4,
                                   self._Data.B3S5, self._Data.B3S6,
                                   self._Data.B3S7, self._Data.B3S8],
                                  self._Baseline, self._Filter)

        self.Board4 = SensorBoard(gas, loc, voltage, speed,
                                  trial, _args, 'Board 4', self._Time,
                                  [self._Data.B4S1, self._Data.B4S2,
                                   self._Data.B4S3, self._Data.B4S4,
                                   self._Data.B4S5, self._Data.B4S6,
                                   self._Data.B4S7, self._Data.B4S8],
                                  self._Baseline, self._Filter)

        self.Board5 = SensorBoard(gas, loc, voltage, speed,
                                  trial, _args, 'Board 5', self._Time,
                                  [self._Data.B5S1, self._Data.B5S2,
                                   self._Data.B5S3, self._Data.B5S4,
                                   self._Data.B5S5, self._Data.B5S6,
                                   self._Data.B5S7, self._Data.B5S8],
                                  self._Baseline, self._Filter)

        self.Board6 = SensorBoard(gas, loc, voltage, speed,
                                  trial, _args, 'Board 6', self._Time,
                                  [self._Data.B6S1, self._Data.B6S2,
                                   self._Data.B6S3, self._Data.B6S4,
                                   self._Data.B6S5, self._Data.B6S6,
                                   self._Data.B6S7, self._Data.B6S8],
                                  self._Baseline, self._Filter)

        self.Board7 = SensorBoard(gas, loc, voltage, speed,
                                  trial, _args, 'Board 7', self._Time,
                                  [self._Data.B7S1, self._Data.B7S2,
                                   self._Data.B7S3, self._Data.B7S4,
                                   self._Data.B7S5, self._Data.B7S6,
                                   self._Data.B7S7, self._Data.B7S8],
                                  self._Baseline, self._Filter)

        self.Board8 = SensorBoard(gas, loc, voltage, speed,
                                  trial, _args, 'Board 8', self._Time,
                                  [self._Data.B8S1, self._Data.B8S2,
                                   self._Data.B8S3, self._Data.B8S4,
                                   self._Data.B8S5, self._Data.B8S6,
                                   self._Data.B8S7, self._Data.B8S8],
                                  self._Baseline, self._Filter)

        self.Board9 = SensorBoard(gas, loc, voltage, speed,
                                  trial, _args, 'Board 9', self._Time,
                                  [self._Data.B9S1, self._Data.B9S2,
                                   self._Data.B9S3, self._Data.B9S4,
                                   self._Data.B9S5, self._Data.B9S6,
                                   self._Data.B9S7, self._Data.B9S8],
                                  self._Baseline, self._Filter)
          
        if self.HDFcache is not None: # then save it in the cache
            self.save_hdf5(self.HDFcache, overwrite=False)
        self._init = True

    def __call__(self):
        if hasattr(self, '_Data'):
            return self.get_all
        print('\nNo data for', end=' ')
        print(self)

    def __str__(self):
        if self._init:
            return '\n\n  %s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s \
                    \n\n\n \
                    Min. Resistance:\t\t%i Ohm (Sensor %d, Board %i)\n \
                    Max. Resistance:\t\t%i Ohm (Sensor %d, Board %i)\n \
                    Max. Variance:\t\t%d Ohm (Sensor %i, Board %i )\n \
                    Max. Average:\t\t%d Ohm (Sensor %i, Board %i)\n \
                    Sampling Rate:\t\t%f Hz' % \
                    (self.get_name(), self.Board1, self.Board2, self.Board3,
                     self.Board4, self.Board5, self.Board6, self.Board7,
                     self.Board8, self.get_min()[2], self.get_min()[1], self.get_min()[0],
                     self.get_max()[2],self.get_max()[1], self.get_max()[0], self.get_var()[2],
                     self.get_var()[1], self.get_var()[0], self.get_mean()[2], self.get_mean()[1],
                     self.get_mean()[0], self.sample_rate)
        else:
            return '\n'+'_'*100+'\n\n  %s:\n\n\t+ '\
                '+ Gas: %s\n\t+ Location: %s\n\t+ SensorVoltage: %s\n\t' \
                '+ FanSpeed: %s\n\t+ Verbose: %s' % \
                (self.Type, self.Gas,
                 self.Location, self.SensorVoltage, self.FanSpeed, self._args['verbose'])




    def load(self, data_location):
        """
        Use pandas to load column-data from file.
        """
        load_successful = False
        if data_location.startswith('hdf://'): # load from HDF
            HDF_location = data_location[6:]
            self.load_hdf5(HDF_location)
            load_successful = True
            return 
            
        loaded_from_cache = False
        if self.HDFcache is not None:
            try:
                self.load_hdf5(self.HDFcache)
                loaded_from_cache = True
                load_successful = True
            except IOError as e:
                print('No HDFStore at {}.\n'.format(self.HDFcache) +\
                    'Creating one for you.\n'.format(self.__class__) + \
                    'Reverting to standard (slow) CSV parsing.')
                store = pd.HDFStore(self.HDFcache, 
                                    complevel=9, 
                                    complib='blosc')
                store.close()
            except KeyError:
                print('Data not found in HDF cache: \n' + \
                    '{}\n'.format(self._get_hd5_dataname()) + \
                    'Trying to parse from original data.')

        if not loaded_from_cache:
            user_cols = list(range(92))
            exclude = [11,20,29,38,47,56,65,74,83]
            for x in exclude:
                user_cols.remove(x)

            col_names = \
                    ['Time','FanSetPoint','FanReading','Mfc1_SetPoint',
                     'Mfc2_SetPoint','Mfc3_SetPoint','Mfc1_Read','Mfc2_Read',
                     'Mfc3_Read','Temp','RelHumid',
                     'B1S1','B1S2','B1S3','B1S4','B1S5','B1S6','B1S7','B1S8',
                     'B2S1','B2S2','B2S3','B2S4','B2S5','B2S6','B2S7','B2S8',
                     'B3S1','B3S2','B3S3','B3S4','B3S5','B3S6','B3S7','B3S8',
                     'B4S1','B4S2','B4S3','B4S4','B4S5','B4S6','B4S7','B4S8',
                     'B5S1','B5S2','B5S3','B5S4','B5S5','B5S6','B5S7','B5S8',
                     'B6S1','B6S2','B6S3','B6S4','B6S5','B6S6','B6S7','B6S8',
                     'B7S1','B7S2','B7S3','B7S4','B7S5','B7S6','B7S7','B7S8',
                     'B8S1','B8S2','B8S3','B8S4','B8S5','B8S6','B8S7','B8S8',
                     'B9S1','B9S2','B9S3','B9S4','B9S5','B9S6','B9S7','B9S8']
                     
            if data_location.startswith('zip://'):
                splitted = data_location[6:].split('.zip')
                if len(splitted) != 2:
                    raise Warning('Zip location contains multiple .zip ' + 
                    'extensions.\n Using the last .zip for parsing.')
                    splitted = splitted[-2:]
                zippath = splitted[0] + '.zip'
                filepath = splitted[1]
                while filepath.startswith('/'):
                    filepath = filepath[1:]
                    
                with zipfile.ZipFile(zippath) as zf:
                    with zf.open(filepath) as fp:
                        self._Data = pd.read_table(fp, 
                                                   names=col_names, 
                                                   header=0, 
                                                   index_col='Time', 
                                                   usecols=user_cols)
                        load_successful = True

            elif data_location.startswith('file://'):
                data_file = data_location[7:]
                if not os.path.exists(data_file):
                    raise AssertionError(
                        'File {} not found.'.format(data_file))
                self._Data = pd.read_table(data_file, 
                                           names=col_names, 
                                           header=0, 
                                           index_col='Time', 
                                           usecols=user_cols)
                load_successful = True
            else:
                raise Exception(
                    "Couldn't parse data type from {}...".format(
                    data_location[:10]))
        if not load_successful:
            raise Warning
        return 

    def save_hdf5(self, storepath, overwrite = True):
        """
        Saves this SensorColumn as HDF5 object in fixed format, i.e. 
        non-appendable and non-queryable, but fast.
        
        Parameters:
        storepath - the hdf5 store where to save the object.
        overwrite - replace existing data (default True).
        """
        if self._Data is None:
            raise Exception('No data to save. Call {}.load() first.'.format(self.__class__))
        dataname = self._get_hd5_dataname()
        with pd.io.pytables.get_store(storepath) as store:
            if not overwrite:
                node = store.get_node(dataname)
                if node is not None:
                    return 
            store.put(dataname, self._Data, format='table')



    def load_hdf5(self, storepath):
        """
        Loads the Data from an HDFstore instead of parsing it.
        Parameters:
        storepath - the path to the HDFStore.
        """
        if self._Data is not None:
            raise Exception('This {} already has data. \n'.format(self.__class__) + 'Refusing to overwrite it with data from HDF5 store.')
            return 
        self._Data = pd.read_hdf(storepath, self._get_hd5_dataname())



    def _get_hd5_dataname(self):
        return '{}/{}/Fan{}_{}_trial{}'.format(self.Gas, self.Location, self.FanSpeed, self.SensorVoltage, self.Trial)



    def find_duplicates(self):
        """
        Return index of duplicated Timestamps.
        """
        if not hasattr(self, '_Data'):
            raise AssertionError
        time = self._Time
        dupes_idx = np.where(time[1:] == time[:-1])[0]
        if dupes_idx.size == 0:
            if self._args['verbose']:
                print('No duplicates detected.')
            return None
        if self._args['verbose']:
            print('[%s] %s: Detected %i duplicate timestamps.' % (len(self.TimeStamp), self.get_name(), len(dupes_idx)))
        return dupes_idx



    def drop_duplicates(self):
        """
        Searches for duplicate Timestamps and drops them by reindexing the
        pandas DataFrame.
        """
        time = self._Time.copy()
        idx = self.find_duplicates()
        if idx is None:
            return 
        time = np.delete(time, idx)
        self._Data.index.is_unique = True
        self._Data = self._Data.reindex(index=time)
        self.set_time(time)
        if self._args['verbose']:
            print('[%s] %s: Removed %i duplicates.' % (self.TimeStamp, self.get_name(), idx.size))



    def find_gaps(self, thresh = 100):
        """
                Find periods of missing data ('gaps').
                Returns arrays of Start_Idx, (Start_Time, Stop_Time))
        
                Keyword arguments:
                thresh -- Gap threshold in ms.
                """
        assert hasattr(self, '_Time')
        assert isinstance(thresh, (int, float))
        time = self._Time
        diff = time[1:] - time[:-1]
        indx = np.where(diff > thresh)[0]
        start_time = time[indx]
        stop_time = time[(indx + 1)]
        return (indx, start_time, stop_time)



    def fill_gaps(self, rate = 20, window = 0):
        """
                Try to find and fill large periods of the missing Signal ('gaps')
                with white-noise. The statistical properties of the generated noise is
                sampled from the right and left edges of the gap. The Method iterates
                over every Sensor of the SensorColumn.
        
                Keyword arguments:
                rate -- Sample rate to use
                window -- Size of sampling window. If zero use dynamic window size.
        
                """
        assert isinstance(rate, int)
        assert isinstance(window, int)
        sample_rate = rate
        window_size = window
        nonuniform_x = self.get_time()
        (gap_indx, gap_start, gap_stop,) = self.find_gaps(100)
        board_names = [ 'B%iS%i' % (board, sensor) for board in range(1, 10) for sensor in range(1, 9) ]
        for n in board_names:
            unfiltered_y = getattr(self._Data, n).dropna().to_numpy()
            for (i, indx,) in enumerate(gap_indx):
                if i == 0:
                    fixed_x = nonuniform_x[:indx]
                    fixed_y = unfiltered_y[:indx]
                else:
                    win = slice(gap_indx[(i - 1)] + 1, indx)
                    fixed_x = np.append(fixed_x, nonuniform_x[win])
                    fixed_y = np.append(fixed_y, unfiltered_y[win])
                num_samples = (gap_stop[i] - gap_start[i]) / sample_rate
                if window_size is 0:
                    window_size = num_samples
                win_left = slice(indx - window_size, indx)
                left_unfiltered_y = unfiltered_y[win_left]
                win_right = slice(indx + 1, indx + window_size + 1)
                right_unfiltered_y = unfiltered_y[win_right]
                spl_left = sp.interpolate.splrep(nonuniform_x[win_left], left_unfiltered_y)
                spl_right = sp.interpolate.splrep(nonuniform_x[win_right], right_unfiltered_y)
                newx = np.arange(gap_start[i], gap_stop[i], sample_rate)
                if len(newx) == num_samples + 1:
                    newx = np.arange(gap_start[i], gap_stop[i] - sample_rate, sample_rate)
                (newx_left, newx_right,) = np.array_split(newx, 2)
                scopex_left = np.concatenate((nonuniform_x[win_left], newx_left))
                scopex_right = np.concatenate((newx_right, nonuniform_x[win_right]))
                scopey_left = sp.interpolate.splev(scopex_left, spl_left)
                scopey_right = sp.interpolate.splev(scopex_right, spl_right)
                new_win_left = slice(len(nonuniform_x[win_left]), len(scopex_left))
                new_win_right = slice(0, len(newx_right))
                newy = np.concatenate((scopey_left[new_win_left], scopey_right[new_win_right]))
                fixed_x = np.append(fixed_x, newx)
                fixed_y = np.append(fixed_y, newy)

            win = slice(gap_indx[-1] + 1, len(nonuniform_x))
            fixed_x = np.append(fixed_x, nonuniform_x[win])
            fixed_y = np.append(fixed_y, unfiltered_y[win])
            series = pd.Series(data=fixed_y, index=fixed_x)
            if n == 'B1S1':
                self._Data = self._Data.reindex(index=fixed_x)
            self._Data[n] = series
            if self._args['verbose']:
                print('%s: Reconstructed %i gaps.' % (self.get_name(), len(gap_indx)))




    def resample(self, rate=100):
        """
        Resample the signal to sample rate parameter (like it should be).

        Step I  : Create new time series (uniform sample rate).
        Step II : Interpolate old signal (Univariate Spline through all points)
        Step III: Update DataFrame (reindex, replace old Series with new ones)

        Keyword arguments:
        rate -- Target sample rate

        """
        step = rate / float(10)
        uniform_x = np.arange(step, 260000 + step, step)
        _Data = self._Data.reindex(index=pd.Index(uniform_x))
        board_names = [ 'B%iS%i' % (board, sensor) for board in range(1, 10) for sensor in range(1, 9) ]
        for n in board_names:
            f = sp.interpolate.UnivariateSpline(x=self._Data.index.to_numpy(), 
                                                y=self._Data[n].to_numpy(), s=0, k=1)
            uniform_y = f(uniform_x)
            _Data[n] = uniform_y

        self._Data = _Data
        self.set_time(uniform_x)



    def _save(self, path = None, key = 'Data', **kwargs):
        assert isinstance(path, (str, None))
        assert isinstance(key, str)
        import os
        if not path:
            path = os.path.join(os.path.dirname(self.FileName), key + '.h5')
        if os.path.isdir(path):
            path = os.path.join(path, key + '.h5')
        self._Data.to_hdf(path, key, **kwargs)
        if self._args['verbose']:
            print('Saved SensorColumn!\n Path:"%s"\nKey: %s' % (path, key))



    def get_data(self):
        """
        Instance Data getter.
        """
        if hasattr(self, '_Data'):
            return self._Data



    def set_data(self, data):
        """
        Instance Data setter. Update child objects when called.
        """
        assert isinstance(data, (list, np.ndarray))
        self._Data = data
        if self._init:
            self.Board1.set_data(data[0])
            self.Board2.set_data(data[1])
            self.Board3.set_data(data[2])
            self.Board4.set_data(data[3])
            self.Board5.set_data(data[4])
            self.Board6.set_data(data[5])
            self.Board7.set_data(data[6])
            self.Board8.set_data(data[7])
            self.Board9.set_data(data[8])


    property(fget=get_data, fset=set_data, doc='Object data descriptors.')

    def set_filter(self, order = 2, cutoff = None, _btype = 'low'):
        """
        Overwrite base-class setter. Updates child objects when called.
        """
        super(SensorColumn, self).set_filter(order, cutoff, _btype)
        if self._init:
            self.Board1.set_filter(order, cutoff, _btype)
            self.Board2.set_filter(order, cutoff, _btype)
            self.Board3.set_filter(order, cutoff, _btype)
            self.Board4.set_filter(order, cutoff, _btype)
            self.Board5.set_filter(order, cutoff, _btype)
            self.Board6.set_filter(order, cutoff, _btype)
            self.Board7.set_filter(order, cutoff, _btype)
            self.Board8.set_filter(order, cutoff, _btype)
            self.Board9.set_filter(order, cutoff, _btype)


    property(fget=base.get_filter, fset=set_filter, doc='Object filter descriptors.')

    def get_min(self):
        """
        The column-wide minimum Sensor response. Is returned as a 3-tuple of
        (Board, Sensor, value).
        """
        min_lst = [self.Board1.get_min,
         self.Board2.get_min,
         self.Board3.get_min,
         self.Board4.get_min,
         self.Board5.get_min,
         self.Board6.get_min,
         self.Board7.get_min,
         self.Board8.get_min,
         self.Board9.get_min]
        mins = [ x[1] for x in min_lst ]
        idx = mins.index(min(mins))
        return (idx + 1, min_lst[idx][0], min(mins))


    property(fget=get_min, doc='Column wide minima getter.')

    def get_max(self):
        """
        The column-wide maximum Sensor response. Is returned as a 3-tuple of
        (Board, Sensor, value).
        """
        max_lst = [self.Board1.get_max,
         self.Board2.get_max,
         self.Board3.get_max,
         self.Board4.get_max,
         self.Board5.get_max,
         self.Board6.get_max,
         self.Board7.get_max,
         self.Board8.get_max,
         self.Board9.get_max]
        maxs = [ x[1] for x in max_lst ]
        idx = maxs.index(max(maxs))
        return (idx + 1, max_lst[idx][0], max(maxs))


    property(fget=get_max, doc='Column wide maxima getter.')

    def get_var(self):
        """
        The column-wide maximum board Variance. Is returned as tuple
        of (Board, Sensor, value)
        """
        var_lst = [self.Board1.get_var,
         self.Board2.get_var,
         self.Board3.get_var,
         self.Board4.get_var,
         self.Board5.get_var,
         self.Board6.get_var,
         self.Board7.get_var,
         self.Board8.get_var,
         self.Board9.get_var]
        var = [ x[1] for x in var_lst ]
        idx = var.index(max(var))
        return (idx + 1, var_lst[idx][0], max(var))


    property(fget=get_var, doc='Column wide max. variance getter.')

    def get_mean(self):
        """
        The column-wide maximum board averaged Variance. Is returned as tuple
        of (Board, Sensor, value)
        """
        mean_lst = [self.Board1.get_mean,
         self.Board2.get_mean,
         self.Board3.get_mean,
         self.Board4.get_mean,
         self.Board5.get_mean,
         self.Board6.get_mean,
         self.Board7.get_mean,
         self.Board8.get_mean,
         self.Board9.get_mean]
        mean = [ x[1] for x in mean_lst ]
        idx = mean.index(max(mean))
        return (idx + 1, mean_lst[idx][0], max(mean))


    property(fget=get_mean, doc='Column wide max. mean getter.')

    def get_fano(self):
        """
        The column-wide maximum board averaged Fano factor (var/mean).
        Is returned as tuple of (Board, Sensor, value)
        """
        fano_lst = [self.Board1.get_fano,
         self.Board2.get_fano,
         self.Board3.get_fano,
         self.Board4.get_fano,
         self.Board5.get_fano,
         self.Board6.get_fano,
         self.Board7.get_fano,
         self.Board8.get_fano,
         self.Board9.get_fano]
        mean = [ x[1] for x in fano_lst ]
        idx = mean.index(max(mean))
        return (idx + 1, fano_lst[idx][0], max(mean))



    def get_baseline(self):
        """
        Column wide baseline recording. Usually first 10 seconds of experiment.
        Determined by selecting the time index where the first of all 3 mass flow
        controllers registers the introduction of the target gas.
        Returns a range of time indices for the determined baseline period.
        """
        end = []
        try:
            end.append(np.where(self.get_mfc1_read > self.get_mfc1_read.max() / 2)[0][0])
        except:
            pass
        try:
            end.append(np.where(self.get_mfc2_read > self.get_mfc2_read.max() / 2)[0][0])
        except:
            pass
        try:
            end.append(np.where(self.get_mfc3_read > self.get_mfc3_read.max() / 2)[0][0])
        except:
            pass
        if not end:
            return None
        else:
            return (0, min(end))



    def set_baseline(self, baseline):
        """
        Column wide baseline setter. Update child objects when called.
        """
        assert isinstance(baseline, (tuple, list))
        self._Baseline = (baseline[0], baseline[1])
        if self._init:
            self.Board1.set_baseline(baseline)
            self.Board2.set_baseline(baseline)
            self.Board3.set_baseline(baseline)
            self.Board4.set_baseline(baseline)
            self.Board5.set_baseline(baseline)
            self.Board6.set_baseline(baseline)
            self.Board7.set_baseline(baseline)
            self.Board8.set_baseline(baseline)
            self.Board9.set_baseline(baseline)


    property(fget=get_baseline, fset=set_baseline, doc='Column wide baseline descriptors.')

    @property
    def get_fan_setpoint(self):
        """
        contains the set point for the exhaust fan.
        """
        if hasattr(self, '_Data'):
            return self._Data.FanSetPoint



    @property
    def get_fan_reading(self):
        """
        contains the reading from the exhaust fan.
        """
        if hasattr(self, '_Data'):
            return self._Data.FanReading



    @property
    def get_mfc1_setpoint(self):
        """
        The set point for MFC1.
        """
        if hasattr(self, '_Data'):
            return self._Data.Mfc1_SetPoint



    @property
    def get_mfc1_read(self):
        """
        The reading from MFC1.
        """
        if hasattr(self, '_Data'):
            return self._Data.Mfc1_Read



    @property
    def get_mfc2_setpoint(self):
        """
        The set point for MFC2.
        """
        if hasattr(self, '_Data'):
            return self._Data.Mfc2_SetPoint



    @property
    def get_mfc2_read(self):
        """
        The reading from MFC2.
        """
        if hasattr(self, '_Data'):
            return self._Data.Mfc2_Read



    @property
    def get_mfc3_setpoint(self):
        """
        The set point for MFC3.
        """
        if hasattr(self, '_Data'):
            return self._Data.Mfc3_SetPoint



    @property
    def get_mfc3_read(self):
        """
        The reading from MFC3.
        """
        if hasattr(self, '_Data'):
            return self._Data.Mfc3_Read



    @property
    def get_temp(self):
        """
        Temperature reading.
        """
        if hasattr(self, '_Data'):
            return self._Data.Temp



    @property
    def get_humid(self):
        """
        Relative Humidity.
        """
        if hasattr(self, '_Data'):
            return self._Data.RelHumid



    @property
    def get_all(self):
        """
        an MxTxNx8 array with MOX sensor readings from M boards, 8 sensors and
        T selected trials and N time points.
        """
        ab = np.transpose(np.array([self.Board1(),
         self.Board2(),
         self.Board3(),
         self.Board4(),
         self.Board5(),
         self.Board6(),
         self.Board7(),
         self.Board8(),
         self.Board9()]))
        return ab



    @property
    def iter_boards(self):
        """
        Return iterator over all Boards.
        """
        if self._init:
            return iter([self.Board1,
             self.Board2,
             self.Board3,
             self.Board4,
             self.Board5,
             self.Board6,
             self.Board7,
             self.Board8,
             self.Board9])
