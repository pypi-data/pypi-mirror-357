import pytest
import numpy as np
from buildupp.hydration import Compound, Hydration

# compare to values in chemistry_database.ini
def test_formation_enthalpy_Jpmol():
    cmpnd = Compound()
    assert cmpnd.formation_enthalpy_Jpmol('C3S') == -2931000
    assert cmpnd.molar_mass_gpmol('C3S') == 228
    assert cmpnd.density_gpcm3('C3S') == 3.12

    assert cmpnd.formation_enthalpy_Jpmol('H') == -286000


# define C3S hydration
C3S_hydration = {'reactants':{'solids':{'C3S':1},
                                    'liquids':{'H':3.43}},
                        'products':{'solids':{'C1.67SH2.1':1, 'CH':1.33},
                                    'liquids':{}}}
c3s_hyd = Hydration(C3S_hydration)

# compare to values computed in master thesis report
def test_compute_DH0reaction_Jpmol():
    assert c3s_hyd.compute_DH0reaction_Jpmol() == pytest.approx(-121100, abs=50)

def test_compute_mschange_gpmol():
    assert c3s_hyd.compute_mschange_gpmol() == pytest.approx(61.7, abs=0.5)

def test_compute_mu_s_gpJ():
    assert c3s_hyd.compute_mu_s_gpJ() == pytest.approx(0.00051, abs=0.00005)

def test_compute_Vs_change_cm3pmol():
    assert c3s_hyd.compute_Vs_change_cm3pmol() == pytest.approx(48.9, abs=0.5)

def test_compute_nu_s_cm3pJ():
    assert c3s_hyd.compute_nu_s_cm3pJ() == pytest.approx(0.00041, abs=0.00005)