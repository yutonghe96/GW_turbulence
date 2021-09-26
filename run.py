"""
run.py is a Python routine that contains the class run used to store all the
variables associated to a specific run, as well as functions to initialize
and postprocess a set of runs given by an array of directories.
dirs.py contains lists of directories for specific sets of runs in the
literature.
The runs correspond to Pencil Code simulations of gravitational waves
generated by MHD turbulence in the early universe.
"""

def initialize_runs(R, dir0, dirs, quiet=True):

    """
    Function to initialize the dictionary with the list of runs pointing to
    the variables of the class run, which contains the spectra, the time
    series, and direct calculations.

    Arguments:
        R -- array with the name of the runs to be read
        dir0 -- directory that contains the runs to be read
        dirs -- dictionary with the name of the directories where the runs
                are contained
        quiet -- prints the list of read runs if False (default True)

    Returns:
        runs -- dictionary with the initialized values of the runs
    """

    runs = {}
    for i in R:
        dir_run = dirs.get(i)
        run_var = run(i, dir0, dir_run, quiet=quiet)
        runs.update({i:run_var})
    if not quiet:
        print('The runs that have been read are:')
        print([s for s in runs.keys()])
    return runs

def characterize_runs(runs, quiet=True):

    """
    Function that executes the characterize_run function contained
    within the class 'run' for each run within 'runs'.

    Arguments:
        runs -- dictionary of variables of the class run
        quiet -- prints the variables if False (default True)

    Returns:
        runs -- updated dictionary of variables of the class run
    """

    for i in runs:
        run = runs.get(i)
        run.characterize_run(quiet=quiet)

def load_runs(R, dir0, dirs, quiet=True):

    """
    Function to initialize the dictionary with the list of runs pointing to
    the variables of the class run, which contains the spectra, the time
    series, and direct calculations.
    It reads the stored pickle variable containing the data in run.

    Arguments:
        R -- array with the name of the runs to be read
        dir0 -- directory that contains the pickle variables
        dirs -- dictionary with the name of the directories where the runs
                are contained
        quiet -- prints the list of read runs if False (default True)

    Returns:
        runs -- dictionary with the values of the runs read from the pickle
                variables
    """

    import pickle

    runs = {}
    for i in R:
        dir_run = dirs.get(i)
        f = open(dir0 + dir_run + '/' + i + '.pckl', 'rb')
        run_var = pickle.load(f)
        f.close()
        runs.update({i:run_var})
    if not quiet:
        print('The runs that have been read are:')
        print([s for s in runs.keys()])
    return runs

class run():

    """
    Class that contains the variables corresponding to a single run of the
    Pencil Code of GW generation from early universe turbulence.
    """

    def __init__(self, name_run, dir0, dir_run, quiet_war=False, quiet=True):

        """
        Initialize class run and reads the spectra and the time series
        from the files power_#sp.dat and time_series.dat in the directory
        dir0 + dir_run + '/data/', where #sp corresponds to a specific
        spectrum.

        For a list of the spectra #sp, run:
            print(run.spectra_avail)

        Arguments:
            name_run -- name used to identify the specific run
            dir0 -- directory that contains the runs to be read
            dir_run -- specific directory of the run
            quiet_war -- used to ignore warnings if set to True (default False)
            quiet -- prints the list of the run spectra if False (default True)

        Returns:
            run -- initialized class run with the variables:
                   name_run -- name used to identify the specific run
                   dir_run -- specific directory of the run
                   spectra -- directory that includes the different spectra
                   spectra_avail -- list of available spectra within the
                                    spectra dictionary
                   ts -- dictionary that includes the different variables
                         in the time series data
                   ts_avail -- list of available variables within the ts
                               dictionary
        """

        import reading as re
        import numpy as np

        # Option to ignore warnings
        if quiet_war:
            np.warnings.filterwarnings('ignore',
                                       category=np.VisibleDeprecationWarning)
        else:
            np.warnings.filterwarnings('error',
                                       category=np.VisibleDeprecationWarning)
        self.name_run = name_run
        self.dir_run = dir_run
        print('Reading run ' + name_run + '\n')
        self.spectra = re.read_spectra_runs(dir0, self.dir_run)
        keys = self.spectra.keys()
        self.spectra_avail = [s for s in self.spectra.keys() if not s=="k"]
        self.spectra_avail = [s for s in self.spectra_avail if not s=="k0"]
        self.spectra_avail = [s for s in self.spectra_avail if not 't_' in s]
        if not quiet:
            print('Spectra computed: ')
            print(self.spectra_avail)
            print('\n')
        self.ts = re.read_ts(dir_data=dir0 + self.dir_run + '/data/')
        self.ts_avail = [s for s in self.ts.keys() if not s=='it']
        self.ts_avail = [s for s in self.ts_avail  if not s=='t']
        self.ts_avail = [s for s in self.ts_avail  if not s=='dt']

    def characterize_run(self, quiet=True):

        """
        Function that computes the results used to characterize the run
        using the spectra and the time series.

        Arguments:
            peaks -- option to compute mean values and different spectral peaks
                     (default False)

        Returns the updated variable run, which now contains:
            turb -- type of turbulence ('m' for magnetic or 'k' for kinetic)
            Ommax -- maximum turbulence energy density ('OmMmax' or 'OmKmax'),
                     obtained from the time series data as a fraction of the
                     radiation energy density
            tmax -- time at which the energy density has its maximum
                    ('tmaxM' or 'tmaxK')
            kf -- value of the spectral peak at the time of maximum
                  energy density ('kfM' or 'kfK')
            v -- Alfven speed ('vA') or plasma velocity ('vK')
            te -- eddy turnover time of the turbulence, characterized by kf and
                  Omega max ('teM' or 'teK')
            tini -- time at which the maximum energy density (either magnetic
                    or kinetic) reaches its maximum and when the decaying
                    turbulence stage starts

        Executes the following functions (see in each of them the corresponding
        variables, all stored within the variable of the class 'run'):
            update_Pi
            update_EGW
            compute_mean_max_spectra
            compute_rho
            compute_total_max_energies
        """

        import numpy as np

        # compute the Pi and EGW spectra
        self.update_Pi()
        self.update_EGW()

        # compute maximum and mean values of spectra and spectral peaks
        self.compute_mean_max_spectra()

        # compute the time at which EM and EK have their maxima and their
        # maximum values, as well as the position of the spectral peak at
        # that time
        self.OmMmax = 0
        self.OmKmax = 0
        self.OmMmax, self.tmaxM, self.kfM = \
                self.check_max_spectra_ts('mag', 'EEM')
        self.OmKmax, self.tmaxK, self.kfK = \
                self.check_max_spectra_ts('kin', 'EEK')
        # set maximum allowed Om to consider it a correct value and show a
        # warning if the value is over the allowed one
        max_allowed_OmM = 1e0
        if self.OmMmax > max_allowed_OmM:
            print('Maximum value of the magnetic energy density is too',
                  ' large: EEM = ', self.OmMmax, ' > ',
                  max_allowed_OmM, '(max allowed EEM).')
        max_allowed_OmK = 1e0
        if self.OmKmax > max_allowed_OmK:
            print('Maximum value of the kinetic energy density is too',
                  ' large: EEK = ', self.OmKmax, ' > ',
                  max_allowed_OmK, '(max allowed EEK).')

        # maximum Alfven and velocity speeds
        self.vA = np.sqrt(1.5*self.OmMmax)
        self.vK = np.sqrt(2*self.OmKmax)

        # eddy turnover times
        if self.kfM != 0 and self.vA != 0: self.teM = 1/self.kfM/self.vA
        else: self.teM = 1e10
        if self.kfK != 0 and self.vK != 0: self.teK = 1/self.kfK/self.vK
        else: self.teK = 1e10

        # check the nature of the turbulence (m for magnetic or
        # k for kinetic) based on Ommax, and define tini as the time at which
        # the dominant turbulent energy density is maximum
        self.turb = 'k'
        self.tini = self.tmaxK
        self.kf = self.kfK
        self.v = self.vK
        self.te = self.teK
        if self.OmMmax > self.OmKmax:
            self.turb = 'm'
            self.tini = self.tmaxM
            self.kf = self.kfM
            self.v = self.vA
            self.te = self.teM
        self.Ommax = max(self.OmMmax, self.OmKmax)

        # compute energy density time series
        self.compute_rho()
        # compute total turbulent and maximum energy densities from time
        # series
        self.compute_total_max_energies()
        if not quiet: self.print_characterize()

    def compute_mean_max_spectra(self):

        """
        Function that computes the mean and maximum values of the spectra, as
        well as the position of the spectral peak.

        Updates the content of the variable run with:
            #sp_max -- time dependent maximum value of each spectral function
            #sp_mean -- time dependent integrated value of the spectrum
            #sp_kpeak -- time dependent spectral peak
        """

        import numpy as np
        import spectra as sp

        k = self.spectra.get('k')[1:]
        for m in self.spectra_avail:
            t = self.spectra.get('t_'+ m)
            Nt = len(t)
            kpeak = np.zeros(Nt)
            Emax = np.zeros(Nt)
            Emean = np.zeros(Nt)
            E = self.spectra.get(m)[:,1:]
            for i in range(0, Nt):
                kpeak[i], Emax[i] = sp.compute_kpeak(k, E[i,:], quiet=True)
                Emean[i] = np.trapz(E[i,:], k)
            self.spectra.update({m + '_kpeak':kpeak})
            self.spectra.update({m + '_max':Emax})
            self.spectra.update({m + '_mean':Emean})

    def check_max_spectra_ts(self, E, EE):

        """
        Function that computes the maximum value of a field over time.
        It computes the maximum of the integrated spectrum E and the maximum
        of the averaged field EE and returns the largest value of the two.

        Arguments:
            E -- string that defines the name of the spectral function
                 (e.g., E = 'mag')
            EE -- string that defines the name of the time series variable
                  (e.g., EE = 'EEM')

        Returns:
            max -- maximum over time of the averaged value
            tmax -- time at which the field mean value is maximum
            kf -- spectral peak at tmax
        """

        import numpy as np

        max = 0
        t = self.ts.get('t')
        tmax = t[0]
        kf = 0
        if EE in self.ts_avail:
            EEm = self.ts.get(EE)
            indmax = np.argmax(EEm)
            max = EEm[indmax]
            tmax = t[indmax]
        if E in self.spectra_avail:
            mean = self.spectra.get(E + '_mean')
            t = self.spectra.get('t_' + E)
            indmax = np.argmax(mean)
            kpeak = self.spectra.get(E + '_kpeak')
            if mean[indmax] > max:
                max = mean[indmax]
                tmax = t[indmax]
                kf = kpeak[indmax]
            else: kf = np.interp(self.ts.get('t'), t, kpeak)[indmax]

        return max, tmax, kf

    def print_characterize(self):

        """
        Function that prints some of the output computed in the function
        characterize_run of the run.
        """

        if self.turb == 'm':
            print(self.name_run, '(', self.turb, '): Omega max: ', self.OmMmax,
                  ', kf: ', self.kfM, ', vA:', self.vA, ', te: ', self.teM)
        else:
            print(self.name_run, '(', self.turb, '): Omega max: ', self.OmKmax,
                  ', kf: ', self.kfK, ', vA:', self.vK, ', te: ', self.teK)

    def compute_rho(self):

        """
        Function that computes the energy density if urms and EEK are available
        in the time series.

        The ts dictionary of run is updated with:
            rho -- energy density
        """

        import numpy as np

        if 'urms' in self.ts_avail and 'EEK' in self.ts_avail:
            urms = self.ts.get('urms')
            good = np.where(urms != 0)
            EEK = self.ts.get('EEK')
            rho = EEK**0
            rho[good] = 2*EEK[good]/urms[good]**2
            self.ts.update({'rho':rho})
            self.ts_avail.append('rho')

    def compute_total_max_energies(self):

        """
        Function that updates run with the time series of the total turbulent
        energy density 'EEtot', and maximum kinetic 'EEKmax',
        magnetic 'EEMmax', and total 'EEtotmax' energy densities,
        when they are computed.

        The ts dictionary of run is updated with:
            EEtot -- total turbulent energy density (EEM + EEK)
            EEKmax -- maximum kinetic energy density
            EEMmax -- maximum magnetic energy density
            EEtotmax -- sum of maximum kinetic and magnetic energies
        """

        if 'EEM' in self.ts_avail and 'EEK' in self.ts_avail:
            EEK = self.ts.get('EEK')
            EEM = self.ts.get('EEM')
            self.ts.update({'EEtot':EEK + EEM})
            self.ts_avail.append('EEtot')

        # compute EEKmax, EEMmax and EEtotmax
        if 'umax' in self.ts_avail:
            EEKmax = self.ts.get('umax')**2/2
            self.ts.update({'EEKmax':EEKmax})
            self.ts_avail.append('EEKmax')
        if 'bmax' in self.ts_avail:
            EEMmax = self.ts.get('bmax')**2/2
            self.ts.update({'EEMmax':EEMmax})
            self.ts_avail.append('EEMmax')
            if 'umax' in self.ts_avail:
                self.ts.update({'EEtotmax':EEMmax + EEKmax})
                self.ts_avail.append('EEtotmax')

    def update_Pi(self):

        """
        Function that computes the spectrum Pi as the spectrum of the
        projected stress (Str) divided by k^2 (same for helical Str).

        The spectra dictionary of run is updated with:
            Pi -- spectrum Str divided by k^2
            t_Pi -- time array of spectrum Pi
            helPi -- spectrum helStr divided by k^2
            t_helPi -- time array of spectrum helPi
        """

        import numpy as np

        if 'Str' in self.spectra_avail:
            k = self.spectra.get('k')
            t = self.spectra.get('t_Str')
            sp = self.spectra.get('Str')
            tij, kij = np.meshgrid(t, k, indexing='ij')
            kij[np.where(kij == 0)] = 1.
            # Factor t^2/36 is needed because Str refers to the the term
            # 6 Tij/t
            Pi = sp/kij**2*tij**2/36
            Pi[np.where(kij == 0)] = 0.
            self.spectra.update({'Pi':Pi})
            self.spectra.update({'t_Pi':t})
            if 'Pi' not in self.spectra_avail:
                self.spectra_avail.append('Pi')
            if 'helStr' in self.spectra_avail:
                t=self.spectra.get('t_helStr')
                tij, kij = np.meshgrid(t, k, indexing='ij')
                kij[np.where(kij == 0)] = 1.
                sphel = self.spectra.get('helStr')
                helPi = sphel/kij**2
                helPi[np.where(kij == 0)] = 0.
                self.spectra.update({'helPi':helPi})
                self.spectra.update({'t_helPi':t})
                if 'helPi' not in self.spectra_avail:
                    self.spectra_avail.append('helPi')

    def update_EGW(self):

        """
        Function that computes the spectrum of the GW energy density, both
        from GWs and from the combination of GWs, GWh and the mixed term.

        The spectra dictionary of run are updated with:
            EGW -- GW energy density spectrum (linear interval) using only GWs
            OmGW -- GW energy density spectrum (logarithmic interval)
            EGW_tot -- GW energy density spectrum (linear interval)
                       using GWs and GWh and/or GWm
            OmGW_tot -- GW energy density spectrum (logarithmic interval)
                       using GWs and GWh and/or GWm
            helEGW -- helical analogous spectrum to EGW
            helOmGW -- helical analogous spectrum to OmGW
            helEGW_tot -- helical analogous spectrum to EGW_tot
            helOmGW_tot -- helical analogous spectrum to OmGW_tot
        and with the time arrays t_#sp
        """

        import numpy as np

        k = self.spectra.get('k')
        if 'GWs' in self.spectra_avail:
            t = self.spectra.get('t_GWs')
            tij, kij = np.meshgrid(t, k, indexing='ij')
            sp1 = self.spectra.get('GWs')
            EGW = sp1/6
            self.spectra.update({'EGW':EGW})
            self.spectra.update({'OmGW':kij*EGW})
            self.spectra.update({'t_EGW':t})
            self.spectra.update({'t_OmGW':t})
            if 'EGW' not in self.spectra_avail:
                self.spectra_avail.append('EGW')
            if 'OmGW' not in self.spectra_avail:
                self.spectra_avail.append('OmGW')
            # if GWh and/or GWm are computed, then combine them to compute
            # the total EGW during the simulation
            extra = False
            if 'GWh' in self.spectra_avail:
                extra = True
                sp2 = self.spectra.get('GWh')
                EGW += sp2/tij**2/6
            if 'GWm' in self.spectra_avail:
                extra = True
                sp3 = self.spectra.get('GWm')
                EGW -= sp3/tij/3
            if extra:
                self.spectra.update({'EGW_tot':EGW})
                self.spectra.update({'OmGW_tot':kij*EGW})
                self.spectra.update({'t_EGW_tot':t})
                self.spectra.update({'t_OmGW_tot':t})
                if 'EGW_tot' not in self.spectra_avail:
                    self.spectra_avail.append('EGW_tot')
                if 'OmGW_tot' not in self.spectra_avail:
                    self.spectra_avail.append('OmGW_tot')

        if 'helGWs' in self.spectra_avail:
            t = self.spectra.get('t_helGWs')
            tij, kij = np.meshgrid(t, k, indexing='ij')
            sphel1 = self.spectra.get('helGWs')
            helEGW = sphel1/6
            self.spectra.update({'helEGW':helEGW})
            self.spectra.update({'helOmGW':kij*helEGW})
            self.spectra.update({'t_helEGW':t})
            self.spectra.update({'t_helOmGW':t})
            if 'helEGW' not in self.spectra_avail:
                self.spectra_avail.append('helEGW')
            if 'helOmGW' not in self.spectra_avail:
                self.spectra_avail.append('helOmGW')
            # if helGWh and/or helGWm are computed, then combine them to
            # compute the total helEGW during the simulation
            extra = False
            if 'helGWh' in self.spectra_avail:
                extra = True
                sphel2 = self.spectra.get('helGWh')
                helEGW += sphel2/tij**2/6
            if 'helGWm' in self.spectra_avail:
                extra = True
                sphel3 = self.spectra.get('helGWm')
                helEGW -= sphel3/tij/3
            if extra:
                self.spectra.update({'helEGW_tot':helEGW})
                self.spectra.update({'helOmGW_tot':kij*helEGW})
                self.spectra.update({'t_helEGW_tot':t})
                self.spectra.update({'t_helOmGW_tot':t})
                if 'helEGW_tot' not in self.spectra_avail:
                    self.spectra_avail.append('helEGW_tot')
                if 'helOmGW_tot' not in self.spectra_avail:
                    self.spectra_avail.append('helOmGW_tot')

    def min_max_stat(self, sp='GWs', indt=0, plot=False, hel=False):

        """
        Function that computes the minimum, the maximum, and the
        averaged functions over time of a spectral function of the run.

        Arguments:
            sp -- string that indicates the spectral function
            indt -- index of time array to perform the average
                    from t[indt] to t[-1]
            plot -- option to overplot all spectral functions
                    from t[indt] to t[-1]
            hel --

        The updated spectral functions within the run.spectra dictionary
        are:
            #sp_min_sp -- minimum of the spectral function #sp over times
            #sp_max_sp -- maximum of the spectral function #sp over times
            #sp_stat_sp -- average of the spectral function #sp over times
                           from t[indt] to t[-1]
        """

        import spectra
        import numpy as np

        if sp in self.spectra_avail:
            t = self.spectra.get('t_' + sp)
            E = self.spectra.get(sp)[:, 1:]
            k = self.spectra.get('k')[1:]
            if hel:
                min_sp_pos, min_sp_neg, max_sp_pos, max_sp_neg, stat_sp = \
                        spectra.min_max_stat(t, k, E, indt=indt,
                                             plot=plot, hel=True)
                self.spectra.update({sp + '_pos_min_sp':min_sp_pos})
                self.spectra.update({sp + '_neg_min_sp':min_sp_neg})
                self.spectra.update({sp + '_pos_max_sp':max_sp_pos})
                self.spectra.update({sp + '_neg_max_sp':max_sp_neg})
                self.spectra.update({sp + '_min_sp': \
                                     np.minimum(min_sp_pos, min_sp_neg)})
                self.spectra.update({sp + '_max_sp': \
                                     np.maximum(max_sp_pos, max_sp_neg)})
                self.spectra.update({sp + '_stat_sp':stat_sp})
            else:
                min_sp, max_sp, stat_sp = \
                        spectra.min_max_stat(t, k, E, indt=indt, plot=plot)
                self.spectra.update({sp + '_min_sp':min_sp})
                self.spectra.update({sp + '_max_sp':max_sp})
                self.spectra.update({sp + '_stat_sp':stat_sp})
        else: print(sp, 'spectrum is not available!')

    def save(self, dir0='.'):

        """
        Function that saves the run in a pickle variable.

        Arguments:
            dir0 -- directory where to save the variable
                    (default is the current directory)
        """

        import os
        import pickle

        # change to dir0 if it is given, otherwise stay current directory
        if dir0 != '.':
            cwd = os.getcwd()
            os.chdir(dir0 + self.dir_run)

        name_f = self.name_run + '.pckl'
        f = open(name_f, 'wb')
        print('Saving ' + self.name_run + '\n')
        print('The output file is ' + name_f + '\n saved in the directory',
              os.getcwd() + '\n')
        pickle.dump(self, f)
        f.close()

        # return to initial directory
        if dir0 != '.': os.chdir(cwd)
