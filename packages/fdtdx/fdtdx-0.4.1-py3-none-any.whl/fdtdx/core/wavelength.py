from fdtdx import constants
from fdtdx.core.jax.pytrees import TreeClass, autoinit, frozen_field


@autoinit
class WaveCharacter(TreeClass):
    """Class describing a wavelength/period/frequency in free space. Importantly, the wave characteristic conversion is
    based on a free space wave when using the wavelength (For conversion, a refractive index of 1 is used).



    Attributes:
        _period: Optional period in seconds. Mutually exclusive with _wavelength and _frequency.
        _wavelength: Optional wavelength in meters. Mutually exclusive with _period and _frequency.
        _frequency: Optional frequency in Hz. Mutually exclusive with _period and _wavelength.
    """

    phase_shift: float = frozen_field(default=0.0)
    _period: float | None = frozen_field(default=None, alias="period")
    _wavelength: float | None = frozen_field(default=None, alias="wavelength")
    _frequency: float | None = frozen_field(default=None, alias="frequency")

    def __post_init__(
        self,
    ):
        self._check_input()

    def _check_input(self):
        if sum([self._period is not None, self._frequency is not None, self._wavelength is not None]) != 1:
            raise Exception("Need to set exactly one of Period, Frequency or Wavelength in WaveCharacter")

    @property
    def period(self) -> float:
        """Gets the period in seconds.

        Returns:
            float: The period in seconds.

        Raises:
            Exception: If neither period nor wavelength is set, or if both are set.
        """
        self._check_input()
        if self._period is not None:
            return self._period
        if self._wavelength is not None:
            return self._wavelength / constants.c
        if self._frequency is not None:
            return 1.0 / self._frequency
        raise Exception("This should never happen")

    @property
    def wavelength(self) -> float:
        """Gets the wavelength in meters.

        Returns:
            float: The wavelength in meters.

        Raises:
            Exception: If neither period nor wavelength is set, or if both are set.
        """
        self._check_input()
        if self._wavelength is not None:
            return self._wavelength
        if self._period is not None:
            return self._period * constants.c
        if self._frequency is not None:
            return constants.c / self._frequency
        raise Exception("This should never happen")

    @property
    def frequency(self) -> float:
        """Gets the frequency in Hz.

        Returns:
            float: The frequency in Hz.
        """
        self._check_input()
        if self._period is not None:
            return 1.0 / self._period
        if self._wavelength is not None:
            return constants.c / self._wavelength
        if self._frequency is not None:
            return self._frequency
        raise Exception("This should never happen")
