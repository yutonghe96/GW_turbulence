"""
reading.py is a Python routine that contains functions that are used to read
the output files of a specific run.
The runs correspond to Pencil Code simulations of gravitational waves
generated by MHD turbulence in the early universe.
"""

def read_spectra_runs(dir0, dir_run, opt=0):

    """
    Function that reads all the spectra files stored in the run directory.
    It reads all files that start with 'power_' and 'powerhel_'
    (with the exeption of power_krms).

    Arguments:
        dir0 -- directory that contains the runs to be read
        dir_run -- directory of the specific run to be read

    Returns:
        spectra -- dictionary that contains the different spectra of the run

    To restore the spectra values from the dictionary one should use:
        spectra.get('#sp')
    where #sp corresponds to a specific spectrum, which can be one of the
    following:
        GWs -- time derivatives of the GW strains
        GWh -- GW strains
        mag -- magnetic field
        kin -- velocity field
        Tpq -- unprojected turbulent stress tensor
        SCL -- scalar mode of the stress tensor
        VCT -- vector mode of the stress tensor
        Str -- projected TT stress tensor

    Note that this list may vary depending on the run and could not include all
    of them or it could add some other spectra computed.

    To print the resulting spectra one can use:
        print([s for s in spectra.keys()])

    The helical spectra can be restored using:
        spectra.get('hel#sp')

    The wave numbers should be the same for all spectra, and can be obtained by
        spectra.get('k')

    The times at which the different spectra are computed might differ (although
    they should be the same in general), and one can obtain the time array as:
        spectra.get('t_#sp')
    """

    import os
    import numpy as np

    dir_data = dir0 + dir_run + '/data'
    os.chdir(dir_data)

    # define the list of power spectra to be read in matching and matchinghel
    # (for helical spectra)
    onlyfiles = [f for f in os.listdir() if os.path.isfile(os.path.join(f))]
    matching = [s for s in onlyfiles if "power" in s]
    matching = [s for s in matching if not "krms" in s]
    matchinghel = [s for s in matching if "hel" in s]
    matchinghel = [s for s in matchinghel if not "swp" in s]
    matching = [s for s in matching if not "hel" in s]
    matching = [s for s in matching if not "swp" in s]

    # read the wave number from power_krms.dat and normalize it using the
    # size of the box length L (assuming a cubic domain)
    k = read_k()
    Nk = len(k)
    if np.isnan(k[0]): k = np.linspace(0, Nk-1, num=Nk)
    L = read_L()
    k0 = 2*np.pi/L
    k = k*k0

    # read and add to the dictionary spectra all the spectra to be read
    # from the list 'matching'
    spectra = {}                # initialize the dictionary spectra
    spectra.update({'k':k})     # add the wave number array to the dictionary
    spectra.update({'k0':k0})   # add smallest wave number
    for i in matching:
        # print(i)
        aux = i.replace('power_', '')
        aux = aux.replace('.dat', '')
        times, sps = read_spectrum(aux, hel=False, opt=opt)
        sps = np.asarray(sps/k0, dtype=object)
        spectra.update({aux:sps})
        spectra.update({'t_' + aux:times})

    # read and add to the dictionary spectra all the helical spectra to be
    # read from the list 'matchinghel'
    for i in matchinghel:
        aux = i.replace('powerhel_', '')
        aux = aux.replace('.dat', '')
        times, sps = read_spectrum(aux, hel=True, opt=opt)
        sps = np.asarray(sps/k0, dtype=object)
        spectra.update({'hel' + aux:sps})
        spectra.update({'t_hel' + aux:times})

    os.chdir(dir0)

    return spectra

def read_ts(dir_data='.', opt=0):

    """
    Read the time series data, which contains the averaged values of the
    fields as a function of time.
    It reads the variables stored in the 'time_series.dat' file and listed in
    'legend.dat'.

    To change the variables in the time series one should change the 'print.in'
    file before executing the run, to decide which fields should be stored in
    the time series.

    Arguments:
        dir_data -- data directory where the time_series.dat file is stored
                    (default current directory)

    Returns:
        ts -- dictionary that contains the variables of the time series data
    """

    import os
    import numpy as np

    # change to dir_data if it is given, otherwise stay current directory
    if dir_data != '.':
        cwd = os.getcwd()
        os.chdir(dir_data)

    # read the file from time_series.dat
    file = 'time_series.dat'
    if opt==0: af = np.loadtxt(file)
    # in this case things become a bit more complicated, since
    # if there are terms of the type 1.23-114 then numpy loadtxt does not work
    # we have to read all data and modify 1.23-114 -> 1.23E-114 to construct
    # af from scratch (as done in read_spectrum)
    if opt==1:
        with open(file) as fp:
            line = fp.readline()
            content = line.split(' ')
            while '' in content: content.remove('')
            while '\n' in content: content.remove('\n')
            j = 0
            while line:
                line = fp.readline()
                content = line.split(' ')
                while '' in content: content.remove('')
                while '\n' in content: content.remove('\n')
                aff = [s.replace('\n', '') for s in content]
                neg = False
                aff2 = []
                for s in aff:
                    if s[0] == '-':
                        neg = True
                        s0 = s[1:]
                    else: s0 = s
                    if '-' in s0:
                        ind = s0.index('-') - 1
                        if s0[ind] != 'E': s2 = s0[:ind + 1] + 'E' + s0[ind + 1:]
                        else: s2 = s0
                    else: s2 = s0
                    if neg: s2 = '-' + s2
                    aff2.append(s2)
                if j == 0: af = [aff2]
                else:
                    if aff != []: af.append(aff2)
                j += 1
        # now we can convert to a numpy array of floats
        #for i in af:
            #print(i, len(i))
        af = np.array(af, dtype='float')

    with open('legend.dat') as fp:
        leg = fp.readline()
        leg = leg.split('-')
        while '' in leg: leg.remove('')
        while ' ' in leg: leg.remove(' ')
        while '\n' in leg: leg.remove('\n')
        #leg = [s for s in leg if s.isalpha()]

    # define the ts (time series) dictionary and update with the values read
    # from the time series file
    Nts = len(leg)
    ts = {}
    for i in range(0, Nts): ts.update({leg[i]:(af[:, i])})

    # return to initial directory
    if dir_data != '.': os.chdir(cwd)

    return ts

def read_spectrum(spectrum, dir_data='.', hel=False, opt=0):

    """
    Function to read the file containing the values of the spectrum

    Arguments:
        spectrum -- name of the spectrum to be read
        hel -- choose if helical spectrum should be read (default False)
        dir_data -- data directory where the time_series.dat file is stored
                    (default current directory)

    Returns:
        times -- array with the times at which the spectrum is computed
        sp -- array with the values of the spectrum for each wave number and at
              each time
    """

    import os
    import numpy as np

    # change to dir_data if it is given, otherwise stay current directory
    if dir_data != '.':
        cwd = os.getcwd()
        os.chdir(dir_data)
    power = 'power_'
    if hel: power = 'powerhel_'
    file = power + spectrum + '.dat'

    # read the file of the spectrum data and store the values of the
    # spectrum (specs) as a function of k, for every value of time
    # (stored in variable times)
    with open(file) as fp:
        line = fp.readline()
        times = []
        sp = [[]]
        content = line.strip()
        if opt == 1:
            content = line.split(' ')
            while '' in content: content.remove('')
            while '\n' in content: content.remove('\n')
        times.append(content)
        len_st = len(content)
        specs = []
        while line:
            line = fp.readline()
            content = line.strip()
            if opt == 1:
                content = line.split(' ')
                while '' in content: content.remove('')
                while '\n' in content: content.remove('\n')
            if len(content) == len_st:
                times.append(content)
                sp.append(specs)
                specs = []
            else:
                if opt == 0:
                    spec = content.split()
                if opt == 1:
                    spec = [s.replace('\n', '') for s in content]
                    # first, remove initial '-' of negative values,
                    # and then
                    # find a second '-' character that corresponds
                    # to the index notation and check if 'E' is before '-',
                    # which is not the case for very large exponents > 100
                    # for example, 1.23-103 -> 1.23E-103
                    spec0 = []
                    neg = False
                    for s in spec:
                        if s[0] == '-':
                            neg = True
                            s0 = s[1:]
                        else: s0 = s
                        if '-' in s0:
                            ind = s0.index('-') - 1
                            if s0[ind] != 'E': s2 = s0[:ind + 1] + \
                                                        'E' + s0[ind + 1:]
                            else: s2 = s0
                            if neg: s2 = '-' + s2
                            s0 = s2
                        spec0.append(s0)
                    spec = spec0
                specs.append(spec)
    sp.append(specs)

    # define the length of the times values read, and compare with the size of
    # the 2D array spec (check test)
    sp = np.array(sp, dtype=object)
    nt = np.shape(sp)[0] - 1
    nt2 = len(times)
    if nt != nt2:
        print('The number of points in time does not coincide with the ',
              'number of spectra values in time')

    # rewrite spec as a 2D array, function of time (first index) and
    # k (second index)
    # note that previously spec had the format of the data file (chunks of
    # values at every time)
    sps = []
    test = False
    for l in range(0, min(nt, nt2)):
        a = np.shape(np.array(sp[l + 1], dtype=object))
        if len(a) == 1:
            a = np.shape(np.array(sp[l + 1], dtype=object))[0] - 1
            b = np.shape(np.array(sp[l + 1][0], dtype=object))[0]
        else:
            a, b = a
        sp0 = np.zeros(a*b)
        cnt = 0
        for i in range(0, a):
            for j in range(0, b):
                sp0[cnt] = sp[l + 1][i][j]
                cnt += 1
        sps.append(np.array(sp0, dtype='double'))

    # redefine the times and sps arrays as numpy arrays to return them
    times = np.array(times, dtype='double')
    sps = np.array(sps, dtype=object)

    # return to initial directory
    if dir_data != '.': os.chdir(dir0)

    return times, sps

def read_k(dir_data='.'):

    """
    Function that reads the values of wave numbers that correspond to
    the spectra files.
    Note that the return k array is normalized such that the smallest wave
    number is 1 (independently of the size of the box).

    Arguments:
        dir_data -- data directory where the time_series.dat file is stored
                    (default current directory)

    Returns:
        k -- array of the wave numbers of the spectral functions
    """

    import os
    import numpy as np

    # change to dir_data if it is given, otherwise stay current directory
    if dir_data != '.':
        cwd = os.getcwd()
        os.chdir(dir_data)

    # the values of the wave numbers are stored in power_krms.dat
    # read file and store in numpy array k
    ak = np.loadtxt('power_krms.dat')
    a, b = np.shape(ak)
    k = np.zeros(a*b)
    cnt = 0
    for i in range(0, a):
        for j in range(0, b):
            k[cnt] = ak[i][j]
            cnt += 1
    k = np.array(k, dtype='double')

    # return to initial directory
    if dir_data != '.': os.chdir(dir0)

    return k

def read_L(dir_data='.'):

    """
    Function that reads the size of the domain to compute the actual
    wave numbers from the normalized wave numbers read in the function 'read_k'.
    The length of the size domain is read from the file 'param.nml'.
    Note that this assumes cubic domain such that the volume is Lx^3

    Arguments:
        dir_data -- data directory where the time_series.dat file is stored
                    (default current directory)

    Returns:
        L -- size of the domain in one direction
    """

    import os

    # change to dir_data if it is given, otherwise stay current directory
    if dir_data != '.':
        cwd = os.getcwd()
        os.chdir(dir_data)

    # read length from the file 'param.nml'
    with open('param.nml') as fp:
        content = fp.readlines()
        content = [x.strip() for x in content]

    matching = [s for s in content if "LXYZ" in s]
    LXYZ = matching[0].split()[1]
    L = float(LXYZ.split('*')[1])

    # return to initial directory
    if dir_data != '.': os.chdir(dir0)

    return L

def sensitivity(file, dir='detector_sensitivity'):

    """
    Function that reads the sensitivity .csv files.

    Arguments:
        file -- name of the file to be read
        dir -- directory where the file is stored
               (default is 'detector_sensitivity')

    Returns:
        f -- array of frequencies
        OmGW -- spectrum of GW energy density
    """

    import os
    import numpy as np

    # move to directory where the detector files are stored
    cwd = os.getcwd()
    os.chdir(dir)

    f = []
    OmGW = []
    with open(file) as fp:
        line = fp.readline()
        x = line.split(';')
        f.append(x[0].replace(',', '.'))
        x1_aux = x[1].replace('\n', '')
        x1_aux = x1_aux.replace(',', '.')
        OmGW.append(x1_aux)
        while line:
            line = fp.readline()
            x = line.split(';')
            try:
                x1_aux = x[1].replace('\n', '')
                x1_aux = x1_aux.replace(',', '.')
                OmGW.append(x1_aux)
                f.append(x[0].replace(',', '.'))
            except: print('end')
    f = np.array(f, dtype='float')
    OmGW = np.array(OmGW, dtype='float')
    inds = np.argsort(f)
    f = f[inds]
    OmGW = OmGW[inds]
    os.chdir(cwd)

    return f, OmGW
