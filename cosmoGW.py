"""
cosmoGW.py is a Python routine that contains functions relevant for
cosmological sources of the stochastic gravitational wave background (SGWB).

Author: Alberto Roper Pol
Date: 01/12/2021
"""

import astropy.constants as const
import astropy.units as u
import numpy as np
import cosmology as co

########################## SGWB at present time ##########################

def fac_hc_OmGW(d=1, h0=1.):

    """
    Function that returns the factor to transform the strain function
    hc(f) to the GW energy density OmGW (f) away from the source.

    Arguments:
        d -- option to give the factor to convert from energy density to
             strain if set to -1 (default 1)
        h0 -- parameterizes the uncertainties (Hubble tension) in the value
              of the Hubble rate (default 1); see values_0 function

    Returns:
        fac -- factor to convert from the strain function hc(f) to the GW
               energy density OmGW (f) in frequency units (Hz)
               
    Reference: M. Maggiore, "Gravitational wave experiments and early universe cosmology,"
    https://arxiv.org/pdf/gr-qc/9909001.pdf (2000); eq. 17.
    """

    g0, g0s, T0, H0 = co.values_0(h0=h0)
    fac = H0*np.sqrt(3/2)/np.pi
    if d == -1: fac = 1/fac**2

    return fac

def hc_OmGW(f, OmGW, d=1, h0=1.):

    """
    Function that transforms the  GW energy density OmGW (f) to the
    characteristc strain spectrum function hc(f) away from the source.

    Arguments:
        f -- frequency array (in units of frequency, e.g. Hz)
        OmGW -- GW energy density spectrum OmGW (f)
        d -- option to convert from energy density to strain if set
             to -1 (default 1)
        h0 -- parameterizes the uncertainties (Hubble tension) in the value
              of the Hubble rate (default 1); see values_0 function

    Returns:
        hc -- strain spectrum
        
    Reference: M. Maggiore, "Gravitational wave experiments and early universe cosmology,"
    https://arxiv.org/pdf/gr-qc/9909001.pdf (2000); eq. 17.
    """

    f = f.to(u.Hz)
    fac = fac_hc_OmGW(d=d, h0=h0)
    hc = fac/f*np.sqrt(OmGW)
    if d==-1: hc = fac*f**2*OmGW**2

    return hc

def hc_Sf(f, Sf, d=1):

    """
    Function that transforms the power spectral density Sf (f) to the
    characteristic strain spectrum function hc(f).

    Arguments:
        f -- frequency array (in units of frequency, e.g. Hz)
        Sf -- power spectral density Sf (f) (in units of 1/Hz^3)
        d -- option to convert from strain to power spectral density if set
             to -1 (default 1)

    Returns:
        hc -- strain spectrum
        
    Reference: A. Roper Pol, C. Caprini, A. Neronov, D. Semikoz, "The gravitational wave
    signal from primordial magnetic fields in the Pulsar Timing Array frequency band,"
    https://arxiv.org/pdf/2201.05630.pdf (2022); eq. 42.
    """

    f = f.to(u.Hz)
    Sf = Sf.to(1/u.Hz**3)
    hc = np.sqrt(12*np.pi**2)*np.sqrt(Sf*f**3)
    if d==-1: hc = Sf**2/12/np.pi**2/f**(3/2)

    return hc

def Omega_A(A=1, fref=0, beta=0, h0=1.):

    """
    Function that returns the amplitude of the SGWB energy density
    spectrum, expressed as a power law (PL), given the amplitude A of the
    characteristic strain, also expressed as a PL.
    
    Note that A is always given for the reference frequency of 1/(1 year)
    and it is used in the common process reported by PTA collaborations.

    The GW energy density and characteristic amplitude can be expressed as:

    OmGW = Omref (f/fref)^beta
    hc = A (f/fyr)^alpha

    Arguments:
        A -- amplitude of the characteristic strain PL using 1yr as the reference
             frequency
        fref -- reference frequency used for the PL expression of the
                GW background given in units of frequency (default
                1 yr^(-1))
        h0 -- parameterizes the uncertainties (Hubble tension) in the value
              of the Hubble rate (default 1); see values_0 function

    Returns:
        Omref -- amplitude of the GW energy density PL
        
    Reference: A. Roper Pol, C. Caprini, A. Neronov, D. Semikoz, "The gravitational wave
    signal from primordial magnetic fields in the Pulsar Timing Array frequency band,"
    https://arxiv.org/pdf/2201.05630.pdf (2022); eq. 44.
    """

    fac = fac_hc_OmGW(d=-1, h0=h0)
    fyr = 1/u.yr
    fyr = fyr.to(u.Hz)
    Omref = fac*fyr**2*A**2
    if fref != 0:
        fref = fref.to(u.Hz)
        Omref *= (fref.value/fyr.value)**beta

    return Omref

def shift_onlyOmGW_today(OmGW, g=10, d=1, h0=1.):

    """
    Function that shifts the GW energy density spectrum from the time of
    generation to the present time.

    Arguments:
        OmGW -- GW energy density spectrum per logarithmic interval
                (normalized by the radiation energy density)
        g -- number of relativistic degrees of freedom (dof) at the time of generation
             (default 10, i.e., ~QCD scale)
        d -- option to reverse the transformation if set to -1, i.e.,
             to return OmGW(k) from the shifted to present time OmGW(f)
             (default 1)
        h0 -- parameterizes the uncertainties (Hubble tension) in the value
              of the Hubble rate (default 1); see values_0 function

    Returns:
        OmGW0 -- shifted spectrum OmGW to present time
        
    Reference: A. Roper Pol, C. Caprini, A. Neronov, D. Semikoz, "The gravitational wave
    signal from primordial magnetic fields in the Pulsar Timing Array frequency band,"
    https://arxiv.org/pdf/2201.05630.pdf (2022); eq. 27.
    """

    Hs_f = Hs_fact()*u.MeV**2
    as_f = as_fact()/u.MeV
    g0, g0s, T0, H0 = values_0(h0=h0)
    OmGW_f = Hs_f**2/H0**2*as_f**4
    OmGW0 = OmGW*OmGW_f*g**(-1/3)
    if d==-1: OmGW0 = OmGW/OmGW_f/g**(-1/3)

    return OmGW0

def shift_frequency_today(k, g=10, T=100*u.MeV, d=1):

    """
    Function that transforms the normalized wave number at the time of
    generation by the Hubble rate H_* to the present time frequency.

    Arguments:
        k -- array of wave numbers (normalized by the Hubble scale)
        g -- number of relativistic degrees of freedom (dof) at the time of generation
             (default 10, i.e., ~QCD scale)
        T -- temperature scale at the time of generation in energy units
             (convertible to MeV) (default 100 MeV, i.e., ~QCD scale)
        d -- option to reverse the transformation if set to -1, i.e.,
             to return the normalized k from the frequency shifted to present
             time f (default 1)

    Returns:
        f -- shifted wave number to frequency as a present time observable
             (in Hz)
             
    Reference: A. Roper Pol, A. Brandenburg, T. Kahniashvili, A. Kosowsky, S. Mandal,
    "The timestep constraint in solving the gravitational wave equations sourced by
    hydromagnetic turbulence," https://arxiv.org/pdf/1807.05479.pdf (2020); eq. B.13.
    """

    Hs_f = Hs_fact()
    as_f = as_fact()
    f_f = Hs_f*as_f/2/np.pi
    T = T.to(u.MeV)
    f = k*f_f*g**(1/6)*T
    if d==-1:
        k = k.to(u.Hz)
        f = k/f_f/g**(1/6)/T
        
    return f

def shift_OmGW_today(k, OmGW, g=10, T=100*u.MeV, d=1, h0=1.):

    """
    Function that shifts the GW energy density spectrum from the time of
    generation to the present time.
    It assumes that the time of generation is within the radiation dominated
    era.

    Arguments:
        k -- array of wave numbers (normalized by the Hubble scale)
        OmGW -- GW energy density spectrum per logarithmic interval
                (normalized by the radiation energy density)
        g -- number of relativistic degrees of freedom (dof) at the time of generation
             (default 10, i.e., ~QCD scale)
        T -- temperature scale at the time of generation in energy units
             (convertible to MeV) (default 100 MeV, i.e., ~QCD scale)
        d -- option to reverse the transformation if set to -1, i.e.,
             to return the normalized k from the frequency shifted to present
             time f (default 1)
        h0 -- parameterizes the uncertainties (Hubble tension) in the value
              of the Hubble rate (default 1); see values_0 function

    Returns:
        f -- shifted wave number to frequency as a present time observable
             (in Hz)
        OmGW0 -- shifted spectrum OmGW to present time
        
    Reference: see functions shift_onlyOmGW_today and shift_frequency_today
    """

    # shift Omega_GW
    OmGW0 = shift_onlyOmGW_today(OmGW, g=g, d=d, h0=h0)
    # shift frequency
    f = shift_frequency_today(k, g=g, T=T, d=d)
    
    return f, OmGW0

def shift_hc_today(k, hc, g=10, T=100*u.MeV, d=1):

    """
    Function that shifts the characteristic amplitude spectrum from the time
    of generation to the present time.

    It assumes that the time of generation is within the radiation dominated
    era.

    Arguments:
        k -- array of wave numbers (normalized by the Hubble scale)
        hc -- spectrum of GW characteristic amplitude per logarithmic interval
        g -- number of relativistic degrees of freedom (dof) at the time of generation
             (default 10, i.e., ~QCD scale)
        T -- temperature scale at the time of generation in energy units
             (convertible to MeV) (default 100 MeV, i.e., ~QCD scale)
        d -- option to reverse the transformation if set to -1, i.e.,
             to return the normalized k from the frequency shifted to present
             time f, and hc(k) from the shifted to present time hc0(f) (default 1)

    Returns:
        f -- shifted wave number to frequency as a present time observable
             (in Hz)
        hc0 -- shifted hc spectrum to present time
        
    Reference: A. Roper Pol, A. Brandenburg, T. Kahniashvili, A. Kosowsky, S. Mandal,
    "The timestep constraint in solving the gravitational wave equations sourced by
    hydromagnetic turbulence," https://arxiv.org/pdf/1807.05479.pdf (2020); eq. B.12.
    """

    as_f = as_fact()
    T = T.to(u.MeV)
    hc0 = hc*as_f*g**(-1/3)/T
    if d == -1: hc0 = hc/as_f/g**(-1/3)*T
    f = shift_frequency_today(k, g=g, T=T, d=d)

    return f, hc0
