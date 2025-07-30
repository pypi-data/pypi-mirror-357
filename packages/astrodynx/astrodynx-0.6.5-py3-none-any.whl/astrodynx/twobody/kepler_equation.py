import jax.numpy as jnp
from jax.typing import DTypeLike
from jax import Array


def mean_anomaly_ecliptic(
    eccentricity: DTypeLike, eccentric_anomaly: DTypeLike
) -> Array:
    r"""
    Returns the mean anomaly in the ecliptic frame.

    Parameters
    ----------
    eccentricity : DTypeLike
        Eccentricity of the orbit.
    eccentric_anomaly : DTypeLike
        Eccentric anomaly of the orbit.

    Returns
    -------
    out : Array
        Mean anomaly in the ecliptic frame.

    Notes
    -----
    The mean anomaly is calculated using the formula:
    $$
    M = E - e \sin(E)
    $$
    where $M$ is the mean anomaly, $E$ is the eccentric anomaly, and $e<1$ is the eccentricity.

    References
    ----------
    Battin, 1999, pp.160.

    Examples
    --------
    >>> import jax.numpy as jnp
    >>> from astrodynx.twobody.kepler_equation import mean_anomaly_ecliptic
    >>> mean_anomaly_ecliptic(0.1, jnp.pi/4)
    Array(0.78539816)
    """
    return eccentric_anomaly - eccentricity * jnp.sin(eccentric_anomaly)


def mean_anomaly_hyperbolic(
    eccentricity: DTypeLike, hyperbolic_anomaly: DTypeLike
) -> Array:
    r"""
    Returns the mean anomaly in the hyperbolic frame.

    Parameters
    ----------
    eccentricity : DTypeLike
        Eccentricity of the orbit.
    hyperbolic_anomaly : DTypeLike
        Hyperbolic anomaly of the orbit.

    Returns
    -------
    out : Array
        Mean anomaly in the hyperbolic frame.

    Notes
    -----
    The mean anomaly is calculated using the formula:
    $$
    M_h = e \sinh(H) - H
    $$
    where $M_h$ is the mean anomaly, $H$ is the hyperbolic anomaly, and $e>1$ is the eccentricity.

    References
    ----------
    Battin, 1999, pp.168.

    Examples
    --------
    >>> import jax.numpy as jnp
    >>> from astrodynx.twobody.kepler_equation import mean_anomaly_hyperbolic
    >>> mean_anomaly_hyperbolic(1.1, jnp.pi/4)
    Array(0.78539816)
    """
    return eccentricity * jnp.sinh(hyperbolic_anomaly) - hyperbolic_anomaly
