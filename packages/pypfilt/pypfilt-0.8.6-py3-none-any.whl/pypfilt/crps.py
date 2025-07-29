"""Calculate CRPS scores for simulated observations."""

import numpy as np


def crps_sample(true_values, samples_table):
    """
    Calculate the CRPS score for a table of samples drom from predictive
    distributions for multiple values, using the empirical distribution
    function defined by the provided samples.

    :param true_values: A 1-D array of observed values.
    :param samples_table: A 2-D array of samples, where each row contains the
        samples for the corresponding value in ``true_values``.
    """
    if np.ndim(true_values) != 1:
        raise ValueError('true_values must be a 1-D array')
    if np.ndim(samples_table) != 2:
        raise ValueError('samples_table must be a 2-D array')
    if len(true_values) != samples_table.shape[0]:
        raise ValueError('incompatible dimensions')
    return np.fromiter(
        (
            crps_edf_scalar(truth, samples_table[ix])
            for (ix, truth) in enumerate(true_values)
        ),
        dtype=np.float64,
    )


def crps_edf_scalar(true_value, sample_values):
    r"""
    Calculate the CRPS for samples drawn from a predictive distribution for a
    single value, using the probability weighted moment CRPS estimator.

    :param true_value: The (scalar) value that was observed.
    :param sample_values: Samples from the predictive distribution (a 1-D
        array).

    See equation (ePWM) in
    `Zamo and Naveau, 2020 <https://doi.org/10.1007/s11004-017-9709-7>`__.

    Note that we use a different definition of the ensemble quantiles,
    :math:`\frac{i - 0.5}{m} : i \in {1, \dots, m}`, as presented in
    `Bröcker 2012 <https://doi.org/10.1002/qj.1891>`__ and noted in
    `Ferro 2013 <https://doi.org/10.1002/qj.2270>`__.
    """
    samples = np.array(sample_values)
    if len(samples.shape) != 1:
        raise ValueError('sample_values must be a 1-D array')
    samples.sort()
    num = len(samples)
    a = np.mean(np.abs(samples - true_value))
    b0 = np.mean(samples)
    qtls = (0.5 + np.arange(num)) / num
    b1 = np.mean(samples * qtls)
    return a + b0 - 2 * b1


def simulated_obs_crps(true_obs, sim_obs):
    """
    Calculate CRPS scores for simulated observations, such as those recorded
    by the :class:`~pypfilt.summary.SimulatedObs` table, against observed
    values.

    The returned array has fields: ``'time'``, ``'fs_time'``, and ``'score'``.

    :param true_obs: The table of recorded observations; this must contain the
        fields ``'time'`` and ``'value``'.
    :param sim_obs: The table of simulated observations; this must contain the
        fields ``'fs_time'``, ``'time'``, and ``'value'``.

    :raises ValueError: if ``true_obs`` or ``sim_obs`` do not contain all of
        the required fields.
    """
    # Check that required columns are present.
    for column in ['time', 'value']:
        if column not in true_obs.dtype.names:
            msg_fmt = 'Column "{}" not found in true_obs'
            raise ValueError(msg_fmt.format(column))
    for column in ['fs_time', 'time', 'value']:
        if column not in sim_obs.dtype.names:
            msg_fmt = 'Column "{}" not found in sim_obs'
            raise ValueError(msg_fmt.format(column))

    # Only retain simulated observations for times with true observations.
    sim_mask = np.isin(sim_obs['time'], true_obs['time'])
    sim_obs = sim_obs[sim_mask]
    # Only retain true observations for times with simulated observations.
    true_mask = np.isin(true_obs['time'], sim_obs['time'])
    true_obs = true_obs[true_mask]

    # Identify the output rows.
    time_combs = np.unique(sim_obs[['fs_time', 'time']])
    score_rows = len(time_combs)
    time_dtype = true_obs.dtype.fields['time'][0]
    scores = np.zeros(
        (score_rows,),
        dtype=[
            ('time', time_dtype),
            ('fs_time', time_dtype),
            ('score', np.float64),
        ],
    )

    # Calculate each CRPS score in turn.
    for ix, (fs_time, time) in enumerate(time_combs):
        # Ensure there is only a single true value for this time.
        true_mask = true_obs['time'] == time
        true_value = true_obs['value'][true_mask]
        true_count = len(true_value)
        if true_count != 1:
            msg_fmt = 'Found {} true values for {}'
            raise ValueError(msg_fmt.format(true_count, time))
        true_value = true_value[0]

        # Calculate the CRPS for this time.
        sim_mask = np.logical_and(
            sim_obs['time'] == time, sim_obs['fs_time'] == fs_time
        )
        samples = sim_obs['value'][sim_mask]
        score = crps_edf_scalar(true_value, samples)

        # Update the current row of the scores table.
        scores['time'][ix] = time
        scores['fs_time'][ix] = fs_time
        scores['score'][ix] = score

    return scores
