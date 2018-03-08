#import re
import math

import numpy as np

from ..exceptions import *
#from ..datastructures import *
#from . import pe
#from . import driver_util
#from . import driver_helpers
#from .. import moptions
##from . import pe
##from .driver import options
#from .. import util
#from .. import qcvars


#_zeta_values = ['d', 't', 'q', '5', '6', '7', '8']
#_zeta_val2sym = {k + 2: v for k, v in zip(range(7), _zeta_values)}
#_zeta_sym2val = {v: k for k, v in _zeta_val2sym.items()}
_zeta_values = 'dtq5678'
_zeta_val2sym = {k + 2: v for k, v in enumerate(_zeta_values)}
_zeta_sym2val = {v: k for k, v in _zeta_val2sym.items()}


def xtpl_highest_1(functionname, zHI, valueHI, verbose=True):
    r"""Scheme for total or correlation energies with a single basis or the highest
    zeta-level among an array of bases. Used by :py:func:`~psi4.cbs`.

    .. math:: E_{total}^X = E_{total}^X

    """
    if isinstance(valueHI, float):

        if verbose:
            # Output string with extrapolation parameters
            cbsscheme = ''
            cbsscheme += """\n   ==> {} <==\n\n""".format(functionname.upper())
            cbsscheme += """   HI-zeta ({}) Energy:               {:16.12f}\n""".format(zHI, valueHI)

            print(cbsscheme)

        return valueHI

    elif isinstance(valueHI, np.ndarray): #(core.Matrix, core.Vector)):

        if verbose > 2:
            core.print_out("""   HI-zeta (%s) Total Energy:\n""" % (str(zHI)))
            valueHI.print_out()

        return valueHI


def scf_xtpl_helgaker_2(functionname, zLO, valueLO, zHI, valueHI, verbose=True, alpha=1.63):
    r"""Extrapolation scheme for reference energies with two adjacent zeta-level bases.
    Used by :py:func:`~psi4.cbs`.
    Halkier, Helgaker, Jorgensen, Klopper, & Olsen, Chem. Phys. Lett. 302 (1999) 437-446.

    .. math:: E_{total}^X = E_{total}^{\infty} + \beta e^{-\alpha X}, \alpha = 1.63

    """

    if type(valueLO) != type(valueHI):
        raise ValidationError("scf_xtpl_helgaker_2: Inputs must be of the same datatype! (%s, %s)"
                              % (type(valueLO), type(valueHI)))

    beta_division = 1 / (math.exp(-1 * alpha * zLO) * (math.exp(-1 * alpha) - 1))
    beta_mult = math.exp(-1 * alpha * zHI)

    if isinstance(valueLO, float):
        beta = (valueHI - valueLO) / (math.exp(-1 * alpha * zLO) * (math.exp(-1 * alpha) - 1))
        value = valueHI - beta * math.exp(-1 * alpha * zHI)

        if verbose:
            # Output string with extrapolation parameters
            cbsscheme = ''
            cbsscheme += """\n   ==> Helgaker 2-point SCF extrapolation for method: %s <==\n\n""" % (functionname.upper())
            cbsscheme += """   LO-zeta (%s) Energy:               % 16.12f\n""" % (str(zLO), valueLO)
            cbsscheme += """   HI-zeta (%s) Energy:               % 16.12f\n""" % (str(zHI), valueHI)
            cbsscheme += """   Alpha (exponent) Value:           % 16.12f\n""" % (alpha)
            cbsscheme += """   Beta (coefficient) Value:         % 16.12f\n\n""" % (beta)

            name_str = "%s/(%s,%s)" % (functionname.upper(), _zeta_val2sym[zLO].upper(), _zeta_val2sym[zHI].upper())
            cbsscheme += """   @Extrapolated """
            cbsscheme += name_str + ':'
            cbsscheme += " " * (18 - len(name_str))
            cbsscheme += """% 16.12f\n\n""" % value
            print(cbsscheme)

        return value

    #elif isinstance(valueLO, (core.Matrix, core.Vector)):
    elif isinstance(valueLO, np.ndarray):
        beta = valueHI.clone()
        beta.name = 'Helgaker SCF (%s, %s) beta' % (zLO, zHI)
        beta.subtract(valueLO)
        beta.scale(beta_division)
        beta.scale(beta_mult)

        value = valueHI.clone()
        value.subtract(beta)
        value.name = 'Helgaker SCF (%s, %s) data' % (zLO, zHI)

        if verbose > 2:
            core.print_out("""\n   ==> Helgaker 2-point SCF extrapolation for method: %s <==\n\n""" % (functionname.upper()))
            core.print_out("""   LO-zeta (%s)""" % str(zLO))
            core.print_out("""   LO-zeta Data""")
            valueLO.print_out()
            core.print_out("""   HI-zeta (%s)""" % str(zHI))
            core.print_out("""   HI-zeta Data""")
            valueHI.print_out()
            core.print_out("""   Extrapolated Data:\n""")
            value.print_out()
            core.print_out("""   Alpha (exponent) Value:          %16.8f\n""" % (alpha))
            core.print_out("""   Beta Data:\n""")
            beta.print_out()

        return value

    else:
        raise ValidationError("scf_xtpl_helgaker_2: datatype is not recognized '%s'." % type(valueLO))


def scf_xtpl_helgaker_3(functionname, zLO, valueLO, zMD, valueMD, zHI, valueHI, verbose=True):
    r"""Extrapolation scheme for reference energies with three adjacent zeta-level bases.
    Used by :py:func:`~psi4.cbs`.
    Halkier, Helgaker, Jorgensen, Klopper, & Olsen, Chem. Phys. Lett. 302 (1999) 437-446.

    .. math:: E_{total}^X = E_{total}^{\infty} + \beta e^{-\alpha X}
    """

    if (type(valueLO) != type(valueMD)) or (type(valueMD) != type(valueHI)):
        raise ValidationError("scf_xtpl_helgaker_3: Inputs must be of the same datatype! (%s, %s, %s)"
                              % (type(valueLO), type(valueMD), type(valueHI)))

    if isinstance(valueLO, float):

        ratio = (valueHI - valueMD) / (valueMD - valueLO)
        alpha = -1 * math.log(ratio)
        beta = (valueHI - valueMD) / (math.exp(-1 * alpha * zMD) * (ratio - 1))
        value = valueHI - beta * math.exp(-1 * alpha * zHI)

        if verbose:
            # Output string with extrapolation parameters
            cbsscheme = ''
            cbsscheme += """\n   ==> Helgaker 3-point SCF extrapolation for method: %s <==\n\n""" % (functionname.upper())
            cbsscheme += """   LO-zeta (%s) Energy:               % 16.12f\n""" % (str(zLO), valueLO)
            cbsscheme += """   MD-zeta (%s) Energy:               % 16.12f\n""" % (str(zMD), valueMD)
            cbsscheme += """   HI-zeta (%s) Energy:               % 16.12f\n""" % (str(zHI), valueHI)
            cbsscheme += """   Alpha (exponent) Value:           % 16.12f\n""" % (alpha)
            cbsscheme += """   Beta (coefficient) Value:         % 16.12f\n\n""" % (beta)

            name_str = "%s/(%s,%s,%s)" % (functionname.upper(), _zeta_val2sym[zLO].upper(), _zeta_val2sym[zMD].upper(),
                                                             _zeta_val2sym[zHI].upper())
            cbsscheme += """   @Extrapolated """
            cbsscheme += name_str + ':'
            cbsscheme += " " * (18 - len(name_str))
            cbsscheme += """% 16.12f\n\n""" % value
            print(cbsscheme)

        return value

    elif isinstance(valueLO, np.ndarray): #(core.Matrix, core.Vector)):
        valueLO = np.array(valueLO)
        valueMD = np.array(valueMD)
        valueHI = np.array(valueHI)

        nonzero_mask = np.abs(valueHI) > 1.e-14
        top = (valueHI - valueMD)[nonzero_mask]
        bot = (valueMD - valueLO)[nonzero_mask]

        ratio = top / bot
        alpha = -1 * np.log(np.abs(ratio))
        beta = top / (np.exp(-1 * alpha * zMD) * (ratio - 1))
        np_value = valueHI.copy()
        np_value[nonzero_mask] -= beta * np.exp(-1 * alpha * zHI)
        np_value[~nonzero_mask] = 0.0

        # Build and set from numpy routines
        value = core.Matrix(*valueHI.shape)
        value_view = np.asarray(value)
        value_view[:] = np_value
        return value

    else:
        raise ValidationError("scf_xtpl_helgaker_3: datatype is not recognized '%s'." % type(valueLO))


#def corl_xtpl_helgaker_2(functionname, valueSCF, zLO, valueLO, zHI, valueHI, verbose=True):
def corl_xtpl_helgaker_2(functionname, zLO, valueLO, zHI, valueHI, verbose=True):
    r"""Extrapolation scheme for correlation energies with two adjacent zeta-level bases.
    Used by :py:func:`~psi4.cbs`.
    Halkier, Helgaker, Jorgensen, Klopper, Koch, Olsen, & Wilson, Chem. Phys. Lett. 286 (1998) 243-252.

    .. math:: E_{corl}^X = E_{corl}^{\infty} + \beta X^{-3}

    """
    if type(valueLO) != type(valueHI):
        raise ValidationError("corl_xtpl_helgaker_2: Inputs must be of the same datatype! (%s, %s)"
                              % (type(valueLO), type(valueHI)))

    if isinstance(valueLO, float):
        value = (valueHI * zHI ** 3 - valueLO * zLO ** 3) / (zHI ** 3 - zLO ** 3)
        beta = (valueHI - valueLO) / (zHI ** (-3) - zLO ** (-3))

#        final = valueSCF + value
        final = value
        if verbose:
            # Output string with extrapolation parameters
            cbsscheme = """\n\n   ==> Helgaker 2-point correlated extrapolation for method: %s <==\n\n""" % (functionname.upper())
#            cbsscheme += """   HI-zeta (%1s) SCF Energy:           % 16.12f\n""" % (str(zHI), valueSCF)
            cbsscheme += """   LO-zeta (%s) Energy:               % 16.12f\n""" % (str(zLO), valueLO)
            cbsscheme += """   HI-zeta (%s) Energy:               % 16.12f\n""" % (str(zHI), valueHI)
#            cbsscheme += """   Beta (coefficient) Value:         % 16.12f\n""" % beta
            cbsscheme += """   Extrapolated Energy:              % 16.12f\n\n""" % value
            #cbsscheme += """   LO-zeta (%s) Correlation Energy:   % 16.12f\n""" % (str(zLO), valueLO)
            #cbsscheme += """   HI-zeta (%s) Correlation Energy:   % 16.12f\n""" % (str(zHI), valueHI)
            #cbsscheme += """   Beta (coefficient) Value:         % 16.12f\n""" % beta
            #cbsscheme += """   Extrapolated Correlation Energy:  % 16.12f\n\n""" % value

            name_str = "%s/(%s,%s)" % (functionname.upper(), _zeta_val2sym[zLO].upper(), _zeta_val2sym[zHI].upper())
            cbsscheme += """   @Extrapolated """
            cbsscheme += name_str + ':'
            cbsscheme += " " * (19 - len(name_str))
            cbsscheme += """% 16.12f\n\n""" % final
            print(cbsscheme)

        return final

    elif isinstance(valueLO, np.ndarray): #(core.Matrix, core.Vector)):

        beta = valueHI.clone()
        beta.subtract(valueLO)
        beta.scale(1 / (zHI ** (-3) - zLO ** (-3)))
        beta.name = 'Helgaker Corl (%s, %s) beta' % (zLO, zHI)

        value = valueHI.clone()
        value.scale(zHI ** 3)

        tmp = valueLO.clone()
        tmp.scale(zLO ** 3)
        value.subtract(tmp)

        value.scale(1 / (zHI ** 3 - zLO ** 3))
        value.name = 'Helgaker Corr (%s, %s) data' % (zLO, zHI)

        if verbose > 2:
            core.print_out("""\n   ==> Helgaker 2-point correlated extrapolation for """
                           """method: %s <==\n\n""" % (functionname.upper()))
            core.print_out("""   LO-zeta (%s) Data\n""" % (str(zLO)))
            valueLO.print_out()
            core.print_out("""   HI-zeta (%s) Data\n""" % (str(zHI)))
            valueHI.print_out()
            core.print_out("""   Extrapolated Data:\n""")
            value.print_out()
            core.print_out("""   Beta Data:\n""")
            beta.print_out()

#        value.add(valueSCF)
        return value

    else:
        raise ValidationError("corl_xtpl_helgaker_2: datatype is not recognized '%s'." % type(valueLO))

