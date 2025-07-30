import logging

import numpy as np

from exerpy.components.component import Component
from exerpy.components.component import component_registry


@component_registry
class SimpleHeatExchanger(Component):
    r"""
    Class for exergy analysis of simple heat exchangers.

    This class performs exergy analysis calculations for simple heat exchangers with
    one primary flow stream and heat transfer. The exergy product and fuel definitions
    vary based on the direction of heat transfer and temperature levels relative to
    ambient temperature.

    Parameters
    ----------
    **kwargs : dict
        Arbitrary keyword arguments passed to parent class.
        Optional parameter 'dissipative' (bool) to indicate if the component
        is considered fully dissipative.

    Attributes
    ----------
    E_F : float
        Exergy fuel of the component :math:`\dot{E}_\mathrm{F}` in :math:`\mathrm{W}`.
    E_P : float
        Exergy product of the component :math:`\dot{E}_\mathrm{P}` in :math:`\mathrm{W}`.
    E_D : float
        Exergy destruction of the component :math:`\dot{E}_\mathrm{D}` in :math:`\mathrm{W}`.
    epsilon : float
        Exergetic efficiency of the component :math:`\varepsilon` in :math:`-`.
    inl : dict
        Dictionary containing inlet stream data with temperature, mass flows,
        enthalpies, and specific exergies.
    outl : dict
        Dictionary containing outlet stream data with temperature, mass flows,
        enthalpies, and specific exergies.

    Notes
    -----
    The exergy analysis considers three main cases based on heat transfer direction
    and temperatures relative to ambient temperature :math:`T_0`:

    Case 1 - **Heat Release** (:math:`\dot{Q} < 0`):

    a) Both temperatures above ambient:

    .. math::
        \dot{E}_\mathrm{P} &= \dot{m} \cdot (e^\mathrm{T}_\mathrm{in} - 
        e^\mathrm{T}_\mathrm{out})\\
        \dot{E}_\mathrm{F} &= \dot{m} \cdot (e^\mathrm{PH}_\mathrm{in} - 
        e^\mathrm{PH}_\mathrm{out})

    b) Inlet above, outlet below ambient:

    .. math::
        \dot{E}_\mathrm{P} &= \dot{m}_\mathrm{out} \cdot e^\mathrm{T}_\mathrm{out}\\
        \dot{E}_\mathrm{F} &= \dot{m}_\mathrm{in} \cdot e^\mathrm{T}_\mathrm{in} + 
        \dot{m}_\mathrm{out} \cdot e^\mathrm{T}_\mathrm{out} + 
        (\dot{m}_\mathrm{in} \cdot e^\mathrm{M}_\mathrm{in} - 
        \dot{m}_\mathrm{out} \cdot e^\mathrm{M}_\mathrm{out})

    c) Both temperatures below ambient:

    .. math::
        \dot{E}_\mathrm{P} &= \dot{m}_\mathrm{out} \cdot 
        (e^\mathrm{T}_\mathrm{out} - e^\mathrm{T}_\mathrm{in})\\
        \dot{E}_\mathrm{F} &= \dot{E}_\mathrm{P} + \dot{m}_\mathrm{in} \cdot 
        (e^\mathrm{M}_\mathrm{in} - e^\mathrm{M}_\mathrm{out})

    Case 2 - **Heat Addition** (:math:`\dot{Q} > 0`):

    a) Both temperatures above ambient:

    .. math::
        \dot{E}_\mathrm{P} &= \dot{m}_\mathrm{out} \cdot 
        (e^\mathrm{PH}_\mathrm{out} - e^\mathrm{PH}_\mathrm{in})\\
        \dot{E}_\mathrm{F} &= \dot{m}_\mathrm{out} \cdot 
        (e^\mathrm{T}_\mathrm{out} - e^\mathrm{T}_\mathrm{in})

    b) Inlet below, outlet above ambient:

    .. math::
        \dot{E}_\mathrm{P} &= \dot{m}_\mathrm{out} \cdot 
        (e^\mathrm{T}_\mathrm{out} + e^\mathrm{T}_\mathrm{in})\\
        \dot{E}_\mathrm{F} &= \dot{m}_\mathrm{in} \cdot e^\mathrm{T}_\mathrm{in} + 
        (\dot{m}_\mathrm{in} \cdot e^\mathrm{M}_\mathrm{in} - 
        \dot{m}_\mathrm{out} \cdot e^\mathrm{M}_\mathrm{out})

    c) Both temperatures below ambient:

    .. math::
        \dot{E}_\mathrm{P} &= \dot{m}_\mathrm{in} \cdot 
        (e^\mathrm{T}_\mathrm{in} - e^\mathrm{T}_\mathrm{out}) + 
        (\dot{m}_\mathrm{out} \cdot e^\mathrm{M}_\mathrm{out} - 
        \dot{m}_\mathrm{in} \cdot e^\mathrm{M}_\mathrm{in})\\
        \dot{E}_\mathrm{F} &= \dot{m}_\mathrm{in} \cdot 
        (e^\mathrm{T}_\mathrm{in} - e^\mathrm{T}_\mathrm{out})

    Case 3 - **Dissipative** (it is not possible to specify the exergy product :math:`\dot{E}_\mathrm{P}` for this component):

    .. math::
        \dot{E}_\mathrm{P} &= \mathrm{NaN}\\
        \dot{E}_\mathrm{F} &= \dot{m}_\mathrm{in} \cdot 
        (e^\mathrm{PH}_\mathrm{in} - e^\mathrm{PH}_\mathrm{out})

    For all cases, the exergy destruction is calculated as:

    .. math::
        \dot{E}_\mathrm{D} = \dot{E}_\mathrm{F} - \dot{E}_\mathrm{P}

    Where:
        - :math:`e^\mathrm{T}`: Thermal exergy
        - :math:`e^\mathrm{PH}`: Physical exergy
        - :math:`e^\mathrm{M}`: Mechanical exergy
    """

    def __init__(self, **kwargs):
        r"""Initialize simple heat exchanger component with given parameters."""
        super().__init__(**kwargs)

    def calc_exergy_balance(self, T0: float, p0: float, split_physical_exergy) -> None:
        r"""
        Calculate the exergy balance of the simple heat exchanger.

        Performs exergy balance calculations considering both heat transfer direction
        and temperature levels relative to ambient temperature.

        Parameters
        ----------
        T0 : float
            Ambient temperature in :math:`\mathrm{K}`.
        p0 : float
            Ambient pressure in :math:`\mathrm{Pa}`.
        split_physical_exergy : bool
            Flag indicating whether physical exergy is split into thermal and mechanical components.

        Raises
        ------
        ValueError
            If the required inlet and outlet streams are not properly defined or
            exceed the maximum allowed number.
        """      
        # Validate the number of inlets and outlets
        if not hasattr(self, 'inl') or not hasattr(self, 'outl') or len(self.inl) < 1 or len(self.outl) < 1:
            msg = "SimpleHeatExchanger requires at least one inlet and one outlet as well as one heat flow."
            logging.error(msg)
            raise ValueError(msg)
        if len(self.inl) > 2 or len(self.outl) > 2:
            msg = "SimpleHeatExchanger requires a maximum of two inlets and two outlets."
            logging.error(msg)
            raise ValueError(msg)

        # Extract inlet and outlet streams
        inlet = self.inl[0]
        outlet = self.outl[0]

        # Calculate heat transfer Q
        Q = outlet['m'] * outlet['h'] - inlet['m'] * inlet['h']

        # Initialize E_P and E_F
        self.E_P = 0.0
        self.E_F = 0.0

        # Case 1: Heat is released (Q < 0)
        if Q < 0:
            if inlet['T'] >= T0 and outlet['T'] >= T0:
                if split_physical_exergy:
                    self.E_P = np.nan if getattr(self, 'dissipative', False) else inlet['m'] * (inlet['e_T'] - outlet['e_T'])
                else:
                    self.E_P = np.nan if getattr(self, 'dissipative', False) else inlet['m'] * (inlet['e_PH'] - outlet['e_PH'])
                self.E_F = inlet['m'] * (inlet['e_PH'] - outlet['e_PH'])

            elif inlet['T'] >= T0 and outlet['T'] < T0:
                if split_physical_exergy:
                    self.E_P = outlet['m'] * outlet['e_T']
                    self.E_F = (inlet['m'] * inlet['e_T'] + outlet['m'] * outlet['e_T'] +
                            (inlet['m'] * inlet['e_M'] - outlet['m'] * outlet['e_M']))
                else:
                    self.E_P = outlet['m'] * outlet['e_PH']
                    self.E_F = inlet['m'] * inlet['e_PH']

            elif inlet['T'] <= T0 and outlet['T'] <= T0:
                if split_physical_exergy:
                    self.E_P = outlet['m'] * (outlet['e_T'] - inlet['e_T'])
                    self.E_F = self.E_P + inlet['m'] * (inlet['e_M'] - outlet['m'] * outlet['e_M'])
                else:
                    self.E_P = np.nan if getattr(self, 'dissipative', False) else \
                        outlet['m'] * (outlet['e_PH'] - inlet['e_PH'])
                    self.E_F = outlet['m'] * (outlet['e_PH'] - inlet['e_PH'])

            else:
                # Unimplemented corner case
                logging.warning(
                    "SimpleHeatExchanger: unimplemented case (Q < 0, T_in < T0 < T_out?)."
                )
                self.E_P = np.nan
                self.E_F = np.nan

        # Case 2: Heat is added (Q > 0)
        elif Q > 0:
            if inlet['T'] >= T0 and outlet['T'] >= T0:
                if split_physical_exergy:
                    self.E_P = outlet['m'] * (outlet['e_PH'] - inlet['e_PH'])
                    self.E_F = outlet['m'] * (outlet['e_T'] - inlet['e_T'])
                else:
                    self.E_P = outlet['m'] * (outlet['e_PH'] - inlet['e_PH'])
                    self.E_F = outlet['m'] * (outlet['e_PH'] - inlet['e_PH'])
            elif inlet['T'] < T0 and outlet['T'] > T0:
                if split_physical_exergy:
                    self.E_P = outlet['m'] * (outlet['e_T'] + inlet['e_T'])
                    self.E_F = (inlet['m'] * inlet['e_T'] +
                            (inlet['m'] * inlet['e_M'] - outlet['m'] * outlet['e_M']))
                else:
                    self.E_P = outlet['m'] * (outlet['e_PH'] - inlet['e_PH'])
                    self.E_F = outlet['m'] * (outlet['e_PH'] - inlet['e_PH'])

            elif inlet['T'] < T0 and outlet['T'] < T0:
                if split_physical_exergy:
                    self.E_P = np.nan if getattr(self, 'dissipative', False) else \
                        inlet['m'] * (inlet['e_T'] - outlet['e_T']) + \
                        (outlet['m'] * outlet['e_M'] - inlet['m'] * inlet['e_M'])
                    self.E_F = inlet['m'] * (inlet['e_T'] - outlet['e_T'])
                else:
                    self.E_P = np.nan if getattr(self, 'dissipative', False) else \
                        inlet['m'] * (inlet['e_PH'] - outlet['e_PH'])
                    self.E_F = inlet['m'] * (inlet['e_PH'] - outlet['e_PH'])
            else:
                logging.warning(
                    "SimpleHeatExchanger: unimplemented case (Q > 0, T_in > T0 > T_out?)."
                )
                self.E_P = np.nan
                self.E_F = np.nan

        # Case 3: Fully dissipative or Q == 0
        else:
            self.E_P = np.nan
            self.E_F = inlet['m'] * (inlet['e_PH'] - outlet['e_PH'])

        # Calculate exergy destruction
        if np.isnan(self.E_P):
            self.E_D = self.E_F
        else:
            self.E_D = self.E_F - self.E_P

        # Calculate exergy efficiency
        self.epsilon = self.calc_epsilon()

        # Log the results
        logging.info(
            f"SimpleHeatExchanger exergy balance calculated: "
            f"E_P={self.E_P:.2f}, E_F={self.E_F:.2f}, E_D={self.E_D:.2f}, "
            f"Efficiency={self.epsilon:.2%}"
        )


    def aux_eqs(self, A, b, counter, T0, equations, chemical_exergy_enabled):
        """
        Auxiliary equations for the simple heat exchanger.
        
        This function adds rows to the cost matrix A and the right-hand-side vector b to enforce
        the following auxiliary cost relations:
        
        (1) Thermal exergy cost equation:
            - For heat release (T_in > T_out > T0): F-principle is applied
              1/E_T_in * C_T_in - 1/E_T_out * C_T_out = 0
            - For heat addition (T_in < T_out > T0): P-principle is applied
              1/ΔE_T * (C_T_out - C_T_in) = 1/ΔE_M * (C_M_out - C_M_in)
        
        (2) Mechanical exergy cost equation:
            1/E_M_in * C_M_in - 1/E_M_out * C_M_out = 0
            - F-principle: specific mechanical exergy costs equalized between inlet/outlet
            
        (3) Chemical exergy cost equation (if enabled):
            1/E_CH_in * C_CH_in - 1/E_CH_out * C_CH_out = 0
            - F-principle: specific chemical exergy costs equalized between inlet/outlet
        
        Parameters
        ----------
        A : numpy.ndarray
            The current cost matrix.
        b : numpy.ndarray
            The current right-hand-side vector.
        counter : int
            The current row index in the matrix.
        T0 : float
            Ambient temperature.
        equations : dict
            Dictionary for storing equation labels.
        chemical_exergy_enabled : bool
            Flag indicating whether chemical exergy auxiliary equations should be added.
        
        Returns
        -------
        A : numpy.ndarray
            The updated cost matrix.
        b : numpy.ndarray
            The updated right-hand-side vector.
        counter : int
            The updated row index.
        equations : dict
            Updated dictionary with equation labels.
        """
        # --- Thermal cost equation (row counter) ---
        if self.inl[0]["T"] > T0 and self.outl[0]["T"] > T0:
            if self.inl[0]["T"] > self.outl[0]["T"]:
                # Heat is released (turbine-like behavior, f‑rule).
                A[counter, self.inl[0]["CostVar_index"]["T"]] = (1 / self.inl[0]["e_T"] 
                                                                if self.inl[0]["e_T"] != 0 else 1)
                A[counter, self.outl[0]["CostVar_index"]["T"]] = (-1 / self.outl[0]["e_T"]
                                                                if self.outl[0]["e_T"] != 0 else -1)
                equations[counter] = f"aux_f_rule_{self.name}"
            elif self.inl[0]["T"] < self.outl[0]["T"]:
                # Heat is injected (compressor-like behavior, p‑rule):
                dET = self.outl[0]["e_T"] - self.inl[0]["e_T"]
                dEM = self.outl[0]["e_M"] - self.inl[0]["e_M"]
                if dET != 0 and dEM != 0:
                    A[counter, self.inl[0]["CostVar_index"]["T"]] = -1 / dET
                    A[counter, self.outl[0]["CostVar_index"]["T"]] = 1 / dET
                    A[counter, self.inl[0]["CostVar_index"]["M"]] = 1 / dEM
                    A[counter, self.outl[0]["CostVar_index"]["M"]] = -1 / dEM
                    equations[counter] = f"aux_p_rule_{self.name}"
                else:
                    logging.warning("SimpleHeatExchanger: dET or dEM is zero; case not implemented.")
                    equations[counter] = "aux_unimpl_HEX"
            else:
                logging.warning("SimpleHeatExchanger: Inlet and outlet temperatures are equal; case not implemented.")
                equations[counter] = "aux_unimpl_HEX"
        else:
            logging.warning("SimpleHeatExchanger: Cases with T_in or T_out below T0 are not implemented.")
            equations[counter] = "aux_unimpl_HEX"
        b[counter] = 0

        # --- Mechanical cost equality (row counter+1) ---
        A[counter+1, self.inl[0]["CostVar_index"]["M"]] = (1 / self.inl[0]["e_M"]
                                                            if self.inl[0]["e_M"] != 0 else 1)
        A[counter+1, self.outl[0]["CostVar_index"]["M"]] = (-1 / self.outl[0]["e_M"]
                                                            if self.outl[0]["e_M"] != 0 else 1)
        equations[counter+1] = f"aux_equality_mech_{self.outl[0]['name']}"
        b[counter+1] = 0

        # --- Chemical cost equality (conditionally added) ---
        if chemical_exergy_enabled:
            A[counter+2, self.inl[0]["CostVar_index"]["CH"]] = (1 / self.inl[0]["e_CH"]
                                                                if self.inl[0]["e_CH"] != 0 else 1)
            A[counter+2, self.outl[0]["CostVar_index"]["CH"]] = (-1 / self.outl[0]["e_CH"]
                                                                if self.outl[0]["e_CH"] != 0 else 1)
            equations[counter+2] = f"aux_equality_chem_{self.outl[0]['name']}"
            b[counter+2] = 0
            counter += 3
        else:
            counter += 2

        return A, b, counter, equations
