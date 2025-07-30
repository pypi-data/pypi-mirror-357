import logging
import typing

from .. import interface
from .._global import BaseObject, Parameter
from ..common import NEW_LINE, OPERATION_FAILED, OPERATION_SUCCESS, quoted

_logger = logging.getLogger(__name__)


class SolverHF(BaseObject):
    """This is the object that controls the high frequency solvers. A
    corresponding `FDSolver` Object allows to manipulate the settings for the
    Frequency Domain and Integral Equation solvers. The `EigenmodeSolver` Object
    is the specialized object for the calculation of Eigenmodes. Please note
    that the AKS Eigenmode solver method is still configured by the Solver
    Object.

    Settings concerning a simulation run may be defined with this object. Use
    one of the 'start' commands to run the Time Domain Solver.

    This object controls the Wakefield solver.
    """

    def __init__(self, *, attributes=None, vba=None, **kwargs):
        super().__init__(attributes=attributes, vba=vba, **kwargs)
        self._history_title = "define HF Solver:"
        return

    def create_from_attributes(self, modeler):
        """从属性列表定义求解器。

        Args:
            modeler (interface.Model3D): 建模环境。

        Returns:
            self (BaseObject): self
        """
        if not self._attributes:
            _logger.error("No valid properties.")
        else:
            scmd1 = [
                "With Solver ",
            ]
            cmd1 = NEW_LINE.join(scmd1)
            scmd2 = []
            for k, v in self._attributes.items():
                scmd2.append(f".{k} {v}")
            cmd2 = NEW_LINE.join(scmd2)
            scmd3 = [
                "End With",
            ]
            cmd3 = NEW_LINE.join(scmd3)
            cmd = NEW_LINE.join((cmd1, cmd2, cmd3))
            modeler.add_to_history(self._history_title, cmd)
        return self


def define_frequency_range(
    modeler: "interface.Model3D", fmin: Parameter, fmax: Parameter
) -> None:
    """定义频率范围。
    频率单位在define_units中设置。

    Args:
        modeler (cst.interface.Model3D): 建模环境。
        fmin (float): 最小频率。
        fmax (float): 最大频率。
    Returns:
        None:
    """

    modeler.add_to_history(
        "define frequency range",
        f'Solver.FrequencyRange "{fmin.name}","{fmax.name}"',
    )
    return


class FDSolver(BaseObject):
    """This is the object that controls the time-harmonic high frequency solver
    and its methods, as well as the integral equation solver (see also
    `IESolver` Object). Every setting concerning a frequency domain or integral
    equation solver simulation run may be defined with this object. Mesh and
    solver method can be chosen by calling `SetMethod`. Use the `Start` command
    to run the solver.
    """

    def __init__(self, *, attributes=None, vba=None, **kwargs):
        super().__init__(attributes=attributes, vba=vba, **kwargs)
        self._history_title = "define FD Solver:"
        return

    def create_from_attributes(self, modeler):
        """从属性列表定义求解器。

        Args:
            modeler (interface.Model3D): 建模环境。

        Returns:
            self (BaseObject): self
        """
        if not self._attributes:
            _logger.error("No valid properties.")
        else:
            scmd1 = [
                "With FDSolver ",
            ]
            cmd1 = NEW_LINE.join(scmd1)
            scmd2 = []
            for k, v in self._attributes.items():
                scmd2.append(f".{k} {v}")
            cmd2 = NEW_LINE.join(scmd2)
            scmd3 = [
                "End With",
            ]
            cmd3 = NEW_LINE.join(scmd3)
            cmd = NEW_LINE.join((cmd1, cmd2, cmd3))
            modeler.add_to_history(self._history_title, cmd)
        return self
