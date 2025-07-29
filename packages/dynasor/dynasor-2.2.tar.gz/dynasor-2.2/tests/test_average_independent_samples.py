import numpy as np
import pytest
from dynasor.sample import DynamicSample
from dynasor.post_processing import get_sample_averaged_over_independent_runs


dynamic_correlation_functions = ['Fqt', 'Fqt_coh', 'Fqt_coh_A_A', 'Fqt_coh_A_B', 'Fqt_coh_B_B',
                                 'Fqt_incoh', 'Fqt_incoh_A', 'Fqt_incoh_B',
                                 'Sqw', 'Sqw_coh', 'Sqw_coh_A_A', 'Sqw_coh_A_B', 'Sqw_coh_B_B',
                                 'Sqw_incoh', 'Sqw_incoh_A', 'Sqw_incoh_B']


def get_random_dynamic_data_dict(n_q, n_t):
    """ generate a random data_dict """
    data_dict = dict()
    data_dict['q_points'] = np.linspace([0, 0, 0], [1.0, 1.0, 1.5], n_q)
    data_dict['time'] = np.linspace(0, 10, n_t)
    data_dict['omega'] = np.linspace(0, 3, n_t)

    for name in dynamic_correlation_functions:
        data_dict[name] = np.random.normal(0, 10, (n_q, n_t))
    return data_dict


def get_random_dynamic_sample():
    n_q = 50
    n_t = 200
    data_dict = get_random_dynamic_data_dict(n_q, n_t)
    sample = DynamicSample(data_dict, **get_meta_data())
    return sample


def get_meta_data():
    meta_data = dict()
    meta_data['cell'] = np.diag([11.5, 18.2, 10.1])
    meta_data['atom_types'] = ['A', 'B']
    meta_data['particle_counts'] = dict(A=100, B=250)
    meta_data['pairs'] = [('A', 'A'), ('A', 'B'), ('B', 'B')]
    return meta_data


def test_average_dynamic_samples():

    # setup samples to average over
    n_samples = 25
    meta_data_ref = get_meta_data()
    samples = [get_random_dynamic_sample() for _ in range(n_samples)]

    # average
    sample_ave = get_sample_averaged_over_independent_runs(samples)
    assert isinstance(sample_ave, DynamicSample)

    # check dimensions are correct
    assert sorted(sample_ave.dimensions) == ['omega', 'q_points', 'time']
    assert np.allclose(sample_ave.omega, samples[0].omega)
    assert np.allclose(sample_ave.q_points, samples[0].q_points)
    assert np.allclose(sample_ave.time, samples[0].time)

    # check meta data is correct
    assert len(sample_ave.meta_data) == 4
    assert np.allclose(sample_ave.meta_data['cell'], meta_data_ref['cell'])
    assert sample_ave.meta_data['particle_counts'] == meta_data_ref['particle_counts']
    assert sample_ave.meta_data['atom_types'], meta_data_ref['atom_types']
    assert sample_ave.meta_data['pairs'], meta_data_ref['pairs']

    # check value of correlation functions is correct
    for name in dynamic_correlation_functions:
        average = np.mean([sample[name] for sample in samples], axis=0)
        assert np.allclose(average, sample_ave[name])


def test_raises_error_with_inconsistent_samples():

    n_samples = 25

    # inconsistent meta_data
    samples = [get_random_dynamic_sample() for _ in range(n_samples)]
    samples[10].meta_data['cell'] = 4.19 * np.eye(3)
    with pytest.raises(AssertionError):
        get_sample_averaged_over_independent_runs(samples)

    # inconsistent dimensions
    samples = [get_random_dynamic_sample() for _ in range(n_samples)]
    samples[4].q_points[0, 0] = 0.212354
    with pytest.raises(AssertionError):
        get_sample_averaged_over_independent_runs(samples)
