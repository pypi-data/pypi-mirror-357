import pytest
import numpy as np
from ase.build import bulk
from dynasor.qpoints.tools import get_index_offset


def test_index_offset():
    prim = bulk('Ti', 'hcp')
    prim.set_array('basis_index', np.array([0, 1]))
    supercell = prim.repeat((4, 3, 2))

    # check indices
    index, offset = get_index_offset(supercell, prim)
    assert np.allclose(index, supercell.get_array('basis_index'))

    # fail if positions dont match
    supercell.positions[0, 0] += 0.01
    with pytest.raises(ValueError):
        index, offset = get_index_offset(supercell, prim)

    # works again if using higher tolerenaces
    index, offset = get_index_offset(supercell, prim, atol=0.03)
    assert np.allclose(index, supercell.get_array('basis_index'))
