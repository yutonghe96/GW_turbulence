"""
generate_plots_PRD_2020.py is a Python routine  that can be used to generate
the plots of A. Roper Pol, S. Mandal, A. Brandenburg, T. Kahniashvili,
and A. Kosowsky, "Numerical simulations of gravitational waves
from early-universe turbulence," Phys. Rev. D 102, 083512 (2020),
https://arxiv.org/abs/1903.08585
"""

import os

# get working directory, where the runs and routines should be stored
dir0 = os.getcwd() + '/'
HOME = dir0 + '/..'
os.chdir(HOME)

from dirs import read_dirs as rd
import plot_sets
import run as r

# import dictionary with the names identifying
# the runs and pointing to the corresponding directory
dirs = rd('PRD_2020_ini')
dirs = rd('PRD_2020_hel', dirs)
dirs = rd('PRD_2020_noh', dirs)
dirs = rd('PRD_2020_ac', dirs)
R = [s for s in dirs]

# read the runs stored in the pickle variables
runs = r.load_runs(R, dir0, dirs, quiet=False)
os.chdir(dir0)

def plot_EGW_EM_vs_k(rr='ini2', save=True, show=True):

    """
    Function that generates the plot of the magnetic spectrum
    EM (k) = Omega_M(k)/k at the initial time of turbulence generation
    and the GW spectrum EGW (k) = Omega_GW(k)/k, averaged over oscillations
    in time.

    It corresponds to figure 1 of A. Roper Pol, S. Mandal, A. Brandenburg,
    T. Kahniashvili, and A. Kosowsky, "Numerical simulations of gravitational
    waves from early-universe turbulence," Phys. Rev. D 102, 083512 (2020),
    https://arxiv.org/abs/1903.08585.

    Arguments:
        rr -- string that selects which run to plot (default 'ini2')
        save -- option to save the resulting figure (default True)
        show -- option to show the resulting figure (default True)
    """

    import matplotlib.pyplot as plt
    import numpy as np

    plt.figure(figsize=(10,6))
    plt.xscale('log')
    plt.yscale('log')
    plt.xlim(120, 6e4)
    plt.ylim(1e-19, 1e-4)
    plt.xlabel('$k$')
    plt.ylabel(r'$\Omega_{\rm GW}(k)/k$ and $\Omega_{\rm M}(k)/k$',
               fontsize=20)

    run = runs.get(rr)
    # plot the averaged over times GW spectrum
    GWs_stat_sp = run.spectra.get('GWs_stat_sp')
    k = run.spectra.get('k')[1:]
    plt.plot(k, GWs_stat_sp, color='black')
    # plot magnetic spectrum at the initial time
    mag = run.spectra.get('mag')[0, 1:]
    plt.plot(k, mag, color='black')

    # plot k^4 line
    k0 = np.logspace(np.log10(150), np.log10(500), 5)
    plt.plot(k0, 1e-9*(k0/100)**4, color='black', ls='-.', lw=.7)
    plt.text(300, 8e-9, r'$\sim\!k^4$', fontsize=20)

    # plot k^(-5/3) line
    k0 = np.logspace(np.log10(2000), np.log10(8000), 5)
    plt.plot(k0, 1e-5*(k0/1000)**(-5/3), color='black', ls='-.', lw=.7)
    plt.text(5e3, 1.6e-6, r'$\sim\!k^{-5/3}$', fontsize=20)

    # plot k^(-11/3) line
    k0 = np.logspace(np.log10(3000), np.log10(30000), 5)
    plt.plot(k0, 5e-12*(k0/1000)**(-11/3), color='black', ls='-.', lw=.7)
    plt.text(1e4, 2e-15, r'$\sim\!k^{-11/3}$', fontsize=20)

    plt.text(1500, 1e-16, r'$\Omega_{\rm GW} (k)/k$', fontsize=20)
    plt.text(800, 5e-8, r'$\Omega_{\rm M} (k)/k$', fontsize=20)

    ax = plt.gca()
    ax.set_xticks([100, 1000, 10000])
    ytics = 10**np.array(np.linspace(-19, -5, 7))
    ytics2 = 10**np.array(np.linspace(-19, -5, 15))
    yticss = ['$10^{-19}$', '', '$10^{-17}$', '', '$10^{-15}$', '',
              '$10^{-13}$', '', '$10^{-11}$', '', '$10^{-9}$', '',
              '$10^{-7}$', '', '$10^{-5}$']
    ax.set_yticks(ytics2)
    ax.set_yticklabels(yticss)
    plot_sets.axes_lines()
    ax.tick_params(pad=10)

    if save: plt.savefig('plots/EGW_EM_vs_k_' + run.name_run + '.pdf',
                         bbox_inches='tight')
    if not show: plt.close()

def plot_OmMK_OmGW_vs_t(save=True, show=True):

    """
    Function that generates the plots of the total magnetic/kinetic energy
    density as a function of time ('OmM_vs_t.pdf') and the GW energy density
    as a function of time ('OmGW_vs_t.pdf').

    It corresponds to figure 5 of A. Roper Pol, S. Mandal, A. Brandenburg,
    T. Kahniashvili, and A. Kosowsky, "Numerical simulations of gravitational
    waves from early-universe turbulence," Phys. Rev. D 102, 083512 (2020),
    https://arxiv.org/abs/1903.08585.

    Arguments:
        save -- option to save the resulting figure (default True)
        show -- option to show the resulting figure (default True)
    """

    import matplotlib.pyplot as plt
    import numpy as np

    # chose the runs to be shown
    rrs = ['ini1', 'ini2', 'ini3', 'hel1', 'hel2', 'ac1']
    # chose the colors of each run
    col = ['black', 'red', 'blue', 'red', 'blue', 'black']
    # chose the line style for the plots
    ls = ['solid']*6
    ls[3] = 'dashed'
    ls[4] = 'dashed'
    ls[5] = 'dashed'

    plt.figure(1, figsize=(10,6))
    plt.figure(2, figsize=(10,6))

    j = 0
    for i in rrs:
        run = runs.get(i)
        k = run.spectra.get('k')[1:]
        GWs_stat_sp = run.spectra.get('GWs_stat_sp')
        t = run.ts.get('t')[1:]
        indst = np.argsort(t)
        t = t[indst]
        EEGW = run.ts.get('EEGW')[1:][indst]
        if run.turb == 'm': EEM = run.ts.get('EEM')[1:][indst]
        if run.turb == 'k': EEM = run.ts.get('EEK')[1:][indst]

        plt.figure(1)
        plt.plot(t, EEGW, color=col[j], lw=.8, ls=ls[j])
        # text with run name
        if i=='ini1': plt.text(1.02, 5e-8, i, color=col[j])
        if i=='ini2': plt.text(1.07, 5e-11, i, color=col[j])
        if i=='ini3': plt.text(1.2, 6e-9, i, color=col[j])
        if i=='hel1': plt.text(1.15, 2e-9, i, color=col[j])
        if i=='hel2': plt.text(1.12, 7e-10, i, color=col[j])
        if i=='ac1': plt.text(1.2, 1e-7, i, color=col[j])

        plt.figure(2)
        plt.plot(t, EEM, color=col[j], lw=.8, ls=ls[j])
        # text with run name
        if i=='ini1': plt.text(1.01, 8e-2, i, color=col[j])
        if i=='ini2': plt.text(1.12, 3e-3, i, color=col[j])
        if i=='ini3': plt.text(1.01, 9e-3, i, color=col[j])
        if i=='hel1': plt.text(1.15, 1.3e-2, i, color=col[j])
        if i=='hel2': plt.text(1.02, 1e-3, i, color=col[j])
        if i=='ac1': plt.text(1.17, 1.5e-3, i, color=col[j])

        j += 1

    plt.figure(1)
    plt.yscale('log')
    plt.xlabel('$t$')
    plt.xlim(1, 1.25)
    plt.ylim(2e-11, 2e-7)
    plt.ylabel(r'$\Omega_{\rm GW}$')
    plot_sets.axes_lines()
    plt.savefig('plots/OmGW_vs_t.pdf', bbox_inches='tight')

    plt.figure(2)
    plt.yscale('log')
    plt.xlim(1, 1.25)
    plt.ylim(5e-4, 2e-1)
    plt.xlabel('$t$')
    plt.ylabel(r'$\Omega_{\rm M, K}$')
    plot_sets.axes_lines()

    if save: plt.savefig('plots/OmM_vs_t.pdf', bbox_inches='tight')
    if not show: plt.close()
