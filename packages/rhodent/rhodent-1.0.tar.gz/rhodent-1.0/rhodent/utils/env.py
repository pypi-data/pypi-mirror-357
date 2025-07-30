from __future__ import annotations


from os import getenv


def rhodent_getenv(variable) -> str:
    """ Get value of environment variable, or default.

    Possible environment variables are:

    - `RHODENT_RESPONSE_MAX_MEM` - Value in units of MiB. When constructing
      response, try to limit memory usage below this value.
    - `RHODENT_RESPONSE_MAX_MEM_PER_RANK` - Value in units of MiB.
      Ignored if `RHODENT_RESPONSE_MAX_MEM` is set.
    - `RHODENT_REDISTRIBUTE_MAXSIZE` - Maximal number of elements in single redistribute call.
      Larger arrays are split.

    Parameters
    ----------
    variable
        Name of variable, without the ``'RHODENT_'`` prefix.

    Returns
    -------
    Value of variable as string.
    """

    defaults = {'REDISTRIBUTE_MAXSIZE': '1e7',
                'RESPONSE_MAX_MEM': '',
                'RESPONSE_MAX_MEM_PER_RANK': '1000',
                }

    if variable not in defaults.keys():
        allowed = '\n'.join([f'  RHODENT_{var}' for var in defaults.keys()])
        raise ValueError(f'Environment variable RHODENT_{variable} is unknown. '
                         f'Allowed variables are:\n{allowed}')

    return getenv(f'RHODENT_{variable}', defaults[variable])


def get_float(variable) -> float:
    strvalue = rhodent_getenv(variable)
    try:
        value = float(strvalue)
    except ValueError:
        raise ValueError(f'Expected environment variable RHODENT_{variable} to '
                         f'be castable to float. Value is {strvalue!r}.')

    return value


def get_response_max_mem(comm_size: int):
    if rhodent_getenv('RESPONSE_MAX_MEM') == '':
        return get_float('RESPONSE_MAX_MEM_PER_RANK') * comm_size

    return get_float('RESPONSE_MAX_MEM')
