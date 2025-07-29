import pytest
import numpy as np
from buildupp.blend import Blend


def test_compute_surface():
    assert Blend.compute_surface(1) == np.pi

def test_compute_volume():
    assert Blend.compute_volume(1) == np.pi / 6

def test_get_pairs():
    blend_1 = Blend('85pc15ls')
    assert blend_1.get_pairs() == [('85', 'pc'), ('15', 'ls')]

    blend_2 = Blend('85opc15ls')
    assert blend_2.get_pairs() == [('85', 'opc'), ('15', 'ls')]

    blend_3 = Blend('55opc_45lsfine')
    assert blend_3.get_pairs() == [('55', 'opc'), ('45', 'lsfine')]

# this one is important, make dummy psd files with like perfect bidisperse
# the d50 and d90 likely fail
def test_get_psd_dict():
    pass

def test_get_density():
    opc = Blend('100opc')
    assert opc.get_density(units='g/cm3') == 3.15
    assert opc.get_density(units='g/m3') == 3.15 * 1e6

    ls = Blend('100ls')
    assert ls.get_density(units='g/cm3') == 2.7
    assert ls.get_density(units='g/m3') == 2.7 * 1e6

    opc_ls_5545 = Blend('55opc45ls')
    assert opc_ls_5545.get_density(units='g/cm3') == 0.55 * 3.15 + 0.45 * 2.7
    assert opc_ls_5545.get_density(units='g/m3') == (0.55 * 3.15 + 0.45 * 2.7) * 1e6

def test_get_ssa_bet():
    opc = Blend('100opc')
    assert opc.get_ssa_bet(units='m2/g') == 1.09
    assert opc.get_ssa_bet(units='cm2/g') == 1.09 * 1e4

    ls = Blend('100ls')
    assert ls.get_ssa_bet(units='m2/g') == 0.56
    assert ls.get_ssa_bet(units='cm2/g') == 0.56 * 1e4

    opc_ls_5545 = Blend('55opc45ls')
    assert opc_ls_5545.get_ssa_bet(units='m2/g') == 0.55 * 1.09 + 0.45 * 0.56
    assert opc_ls_5545.get_ssa_bet(units='cm2/g') == (0.55 * 1.09 + 0.45 * 0.56) * 1e4

def test_compute_ds():
    pass

def test_compute_ssa_from_psd():
    pass

def test_compute_rou_over_F():
    pass
