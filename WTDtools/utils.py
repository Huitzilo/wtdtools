# 2015.03.24 16:16:04 GMT
import os
import time
from .SensorColumn import SensorColumn
import zipfile

class DataSelector(object):
    GasNames = {  # gas_conc(ppm)
        1: 'Acetaldehyde_500',
        2: 'Acetone_2500',
        3: 'Ammonia_10000',
        4: 'Benzene_200',
        5: 'Butanol_100',
        6: 'CO_1000',
        7: 'CO_4000',
        8: 'Ethylene_500',
        9: 'Methane_1000',
        10: 'Methanol_200',
        11: 'Toluene_200'}

    Locs = {
        1: 'L1',  # 0.25m
        2: 'L2',  # 0.50m
        3: 'L3',  # 0.98m
        4: 'L4',  # 1.18m
        5: 'L5',  # 1.40m
        6: 'L6'}  # 1.45m

    AltLocs = {  # redundant encoding of board location in file name.
        1: '1',  # closest to source
        2: '3',
        3: '5',
        4: '7',
        5: '9',
        6: '11'}  # farthest from source
    
    SensorVoltages = {
        1: '400V',  # 4.0V
        2: '450V',  # 4.5V
        3: '500V',  # 5.0V
        4: '550V',  # 5.5V
        5: '600V'}  # 6.0V

    FanSpeeds = {
        1: '000',   # 1500rpm
        2: '060',   # 3900rpm
        3: '100'}   # 5500rpm
    
    AltFanSpeeds = {
        1: '1500rpm',
        2: '3900rpm',
        3: '5500rpm'}


    def __init__(self, 
                 data_location, 
                 drop_duplicates=True, 
                 fill_gaps=True, 
                 resample=True, 
                 verbose=False, 
                 use_HDFcache=False):
                     
        if not os.path.exists(data_location):
            raise Exception('Data location does not exist: \n' + data_location)
        else:
            self.dataloc_prefix = 'file://'
            self.data_location = data_location
            self._args = {'verbose': verbose,
                          'drop_duplicates': drop_duplicates,
                          'resample': resample,
                          'fill_gaps': fill_gaps,
                          'use_HDFcache': use_HDFcache}
            if use_HDFcache:
                self._args['HDF_cache_location'] = os.path.join(
                                        self.data_location, '.HDFcache')

    def select(self, gas=list(range(1, 12)), loc=list(range(1, 7)),
               voltage=list(range(1, 6)), speed=list(range(1, 4)), trial=list(range(1,21)), 
               from_HDFcache=False):
        """
         Return all filepaths matching input constraints

         Keyword arguments:
         gas -- int of range(1,12), gas name identifier
         loc -- int of range(1,7) , sensor array column number
         voltage -- int of range(1,6) , sensor voltage identifier
         speed -- int of range(1,4) , fan speed identifier
         trial -- int of range(1,21), experiment repetitions
         from_HDFcache -- load the data directly from HDFcache, if present
        """
        # cast int entries to list
        if isinstance(gas, int):
            gas = [gas]
        if isinstance(loc, int):
            loc = [loc]
        if isinstance(voltage, int):
            voltage = [voltage]
        if isinstance(speed, int):
            speed = [speed]
        if isinstance(trial,int):
            trial = [trial]

        # validate input
        assert min(gas) > 0 and max(gas) in list(self.GasNames.keys()), \
            'Wrong gas name: {}'.format(gas)
        assert min(loc) > 0 and max(loc) in list(self.Locs.keys()), \
            'Wrong board location: {}'.format(loc)
        assert min(voltage) > 0 and max(voltage) in list(self.SensorVoltages.keys()), \
            'Wrong sensor voltage: {}'.format(voltage)
        assert min(speed) > 0 and max(speed) in list(self.FanSpeeds.keys()), \
            'Wrong fan speed: {}'.format(speed)
        assert min(trial) > 0 and max(trial) in range(1,21), \
            'Trial number out of range, must be [1,20], is [{},{}]'.format(
                            min(trial), max(trial))

        cols = self._get_data(gas, loc, voltage, speed, trial)
        return cols    

    def _get_data(self, gas, loc, voltage, speed, trial):
        """parsing data directory to reconstruct filenames"""
        cols = []
        for g in gas:
            for l in loc:
                try:
                    (sub, files) = self._get_sensor_col_files(g, l)
                except OSError as e:
                    print('{}\n Keeping calm and carrying on.'.format(e))
                    continue
                for v in voltage:
                    for s in speed:
                        end = "_board_setPoint_%s_fan_setPoint_%s_mfc_setPoint_%sppm_p%s" % (
                            self.SensorVoltages[v],
                            self.FanSpeeds[s],
                            self.GasNames[g],
                            self.AltLocs[l])
                        filtered = [f for f in files if f.endswith(end)]
                        if not filtered:
                            if self._args['verbose']:
                                print('No valid files found for "%s", skipping!' % sub)
                            continue
                        timeStamp = [filt.split('_', 1)[0] for filt in filtered]
                        date = [time.strptime(ts, '%Y%m%d%H%M') for ts in timeStamp]
                        date = [time.strftime('%Y-%m-%d %H:%M', d) for d in date]
                        filtered = [os.path.join(sub, f) for f in filtered]
                        for i, filt in enumerate(filtered):
                            j = i + 1
                            if j in trial:
                                p = os.path.sep.join([self.dataloc_prefix, 
                                                 self.data_location, 
                                                 filt])

                                cols.append(SensorColumn(data_location=p, 
                                                gas=self.GasNames[g],
                                                loc=self.Locs[l], 
                                                voltage=self.SensorVoltages[v], 
                                                speed=self.AltFanSpeeds[s], 
                                                trial=j, 
                                                _args=self._args))

        if self._args['verbose']:
            print('\nSelected %i single trial SensorColumns!' % len(cols))
        return cols



    def _get_sensor_col_files(self, gas, loc):
        """
        lists the files in the directory corresponding to the gas and location.
        """
        sub = os.path.join(self.GasNames[gas], self.Locs[loc])
        files = os.listdir(os.path.join(self.data_location, sub))
        files.sort()
        return (sub, files)




class HDFDataSelector(DataSelector):
    """
    A DataSelector that operates directly on the HDFcache, without need for the 
    Directory structure from the original data.
    """
    def __init__(self, 
                 path_to_HDF, 
                 drop_duplicates=False, 
                 fill_gaps=False, 
                 resample=False, 
                 verbose=False, 
                 use_HDFcache=False):
        """
        Parameters: 
        path_to_HDFcache = path to the HDFcache
        drop_duplicates - drop duplicate time points
        fill_gaps - interpolate gaps in signal
        resample - resample to uniform time points
        verbose - be verbose
        """
        if use_HDFcache:
            print(('WARNING: Ignoring the requested caching in HDFcache, \n' + 
            "since we're already reading from the HDFcache."))
            
        self._args = {'verbose': verbose,
                      'drop_duplicates': drop_duplicates,
                      'resample': resample,
                      'fill_gaps': fill_gaps,
                      'use_HDFcache': False}
                      
        self.path_to_HDF = path_to_HDF
        self.dataloc_prefix = 'hdf://'



    def _get_data(self, gas, loc, voltage, speed, trial):
        cols = []
        for g in gas:
            for l in loc:
                for v in voltage:
                    for s in speed:
                        for t in trial:
                            p = self.dataloc_prefix + self.path_to_HDF
                            column = SensorColumn(data_location=p, 
                                                gas=self.GasNames[g], 
                                                loc=self.Locs[l], 
                                                voltage=self.SensorVoltages[v], 
                                                speed=self.AltFanSpeeds[s], 
                                                trial=t, 
                                                _args=self._args)
                                                
                            cols.append(column)
        return cols

class ZipFileDataSelector(DataSelector):
    """
    A DataSelector that operates directly on the zip file. No Unpacking needed.
    """


    def __init__(self, 
                 path_to_zipfile, 
                 drop_duplicates=True, 
                 fill_gaps=True, 
                 resample=True, 
                 verbose=False, 
                 use_HDFcache=False):
                     
        if not os.path.exists(path_to_zipfile):
            raise Exception('No zip file at {}.'.format(path_to_zipfile))

        self.data_location = path_to_zipfile

        self._args = {'verbose': verbose,
                      'drop_duplicates': drop_duplicates,
                      'resample': resample,
                      'fill_gaps': fill_gaps,
                      'use_HDFcache': use_HDFcache}
        if use_HDFcache:
            self._args['HDF_cache_location'] = os.path.join(
                                        os.path.dirname(self.data_location), 
                                        '{}_HDFcache'.format(os.path.basename(
                                                    self.data_location)))
        self.dataloc_prefix = 'zip://'

    def _get_sensor_col_files(self, gas, loc):
        """
        lists the files in the directory corresponding to the gas and location.
        Specially crafted for zip file access.
        """
        sub = os.path.join('WTD_upload', self.GasNames[gas], self.Locs[loc])
        with zipfile.ZipFile(self.data_location) as zf:
            files = filter(lambda p: p.startswith(sub) \
                                    and len(p) > len(sub), zf.namelist())
            files = [f.split("/")[-1] for f in files]
        files.sort()
        return (sub, files)

def copy_HDFcache(store, newstore):
    """
    Copy the HDFcache with the data into a new pandas.HDFstore, e.g. to change 
    compression settings. This method is a lot more efficient on large stores 
    with many tables (such as the one for the present data) than the pandas
    built-in methods, because it uses generators instead of lists. It runs in 
    O(n), while the pandas method runs in O(n^2) because it checks key 
    presence.
    
    Parameters:
    store - pandas.HDFstore instance of the source store
    newstore - pandas.HDFstore instance of the target store
    """
    ngit = (g for g in store._handle.walk_nodes())
    for n in ngit:
        try:
            type = n._v_attrs['pandas_type']
        except KeyError:
            continue
        #here we could to more checking if the node is actually a DataFrame
        # but it works for our purpose.
        path = n._v_pathname
        df = store.get(path)
        if df is not None:
            newstore.put(path, df)
            print(path)
