#   Projektarbeit "Recherche und Tool zur Simulation von Quantenschaltungen im Bereich Quantencomputing"
#   Author: Lukas Lepper, 24.11.2020
#   Betreuer: Dipl.-Ing. Martin Hardieck
#   Dateiname: G_PhaseShift.py
#   Version: 0.6


import numpy as np
import cmath
from QGate import QGate


class GatePhase(QGate):
    """
    Klasse für das PhaseShift Gatter. Speichert den Typ und erweitert die Matrix dieses Gatters auf Größe des
    Zustandsvektors.
    """

    def __init__(self, list_affected_qubits, list_of_parameters):
        """
        Konstruktor erstellt Matrix in der Größe der Quantenschaltung (Anzahl der Qubits), die das Gatter auf ein
        bestimmtes Qubit beschreibt.

        :param list_affected_qubits: Index des Qubits, auf welches das Gatter angewendet wird
        """

        #   list_affected_qubits wird in der Elternklasse in qsim_obj.list_affected_qubits gespeichert
        #   Gebe nur das erste Element für die Liste der zu verändernden Qubits zurück, da das Gatter nur auf ein Qubit
        #   angewendet wird. Das zweite Element stellt den Parameter Phi da, für dieses Gatter
        super().__init__(list_affected_qubits)

        #   Bezeichnung des Gatters
        self.type = 'p'

        #   Spezifische Matrix des Gatters
        self.general_matrix = np.array([[1, 0], [0, cmath.exp(list_of_parameters[0] * 1j)]], dtype=complex)

        #   Die Matrix wird auf die Größe der Quantenschaltung erweitert
        self.general_matrix = self.expandmatrix(self.getnqubits(), max(list_affected_qubits))
