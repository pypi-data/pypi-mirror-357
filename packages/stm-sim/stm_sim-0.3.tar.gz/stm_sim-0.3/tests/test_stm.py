import pytest
from stm_sim.stm import STM

class TestSTM:
    def setup_method(self):
        pass

    def test_constant_current(self):
        parchg_file = "parchg_files/Fe28C12_101_17_PARCHG"
        stm = STM(bias=(-0.1, 0.1))
        stm.read_parchg(parchg_file)
        x, y, z = stm.scan(scan_mode='constant_current',
                           repeat=(2, 2),
                           plot=True,
                           )
        dh = stm.delta_h(repeat=(2, 2),plot=True)
        print("Done")
