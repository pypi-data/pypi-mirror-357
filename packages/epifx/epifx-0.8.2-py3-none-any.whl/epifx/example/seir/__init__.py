import pkgutil


def __example_data(filename):
    return pkgutil.get_data('epifx.example.seir', filename).decode()


def __write_example_file(filename):
    content = __example_data(filename)
    with open(filename, 'w') as f:
        f.write(content)


def __example_scenarios():
    return {
        'seir': ['seir.toml', 'pr-obs.ssv', 'weekly-cases.ssv'],
        'seir_quick': ['seir_quick.toml', 'weekly-cases-quick.ssv'],
        'seeiir': ['seeiir.toml', 'pr-obs.ssv', 'weekly-cases.ssv'],
        'seeiir_scalar': [
            'seeiir_scalar.toml',
            'pr-obs-scalar.ssv',
            'weekly-cases-scalar.ssv',
        ],
        'stoch': ['stoch.toml', 'pr-obs.ssv', 'weekly-cases.ssv'],
    }


def write_example_files(scenario):
    """
    Save the example files for a scenario to the working directory.

    :param scenario: The scenario name.
    :raises ValueError: If the scenario name is invalid (see below).

    The valid scenarios are:

    * ``'seir'``: The deterministic :class:`~epifx.det.SEIR` model with date
      times.
    * ``'seir_quick'``: : The deterministic :class:`~epifx.det.SEIR` model
      with date times, using only 20 particles.
    * ``'seeiir'``: The deterministic :class:`~epifx.det.SEEIIR` model with
      date times.
    * ``'seeiir_scalar'``: The deterministic :class:`~epifx.det.SEEIIR` model
      with scalar time.
    * ``'stoch'``: The stochastic :class:`~epifx.stoch.SEEIIR` model with date
      times.
    """
    scenario_table = __example_scenarios()
    if scenario not in scenario_table:
        raise ValueError('Invalid scenario name "{}"'.format(scenario))

    for filename in scenario_table[scenario]:
        __write_example_file(filename)
