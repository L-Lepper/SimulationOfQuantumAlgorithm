#   Projektarbeit Literaturrecherche zu Simulationsalgorithmen für Quantencomputing
#   Author: Lukas Lepper, 21.10.2020
#   Betreuer: Martin Hardieck
#   Dateiname: QuantumSimulation.py
#   Version: 0.5


#   Importiere wie in der main oben beschrieben, alle Klassen auf der untersten Ebene. Durch Objekte in diesen Klassen
#   kann auf alle Funktionen zugegriffen werden, die benötigt werden.
from Base import Base
from Operation import Operation
from QState import QState
from PauliX import PauliX
from PauliZ import PauliZ
from HadarmardH import HadamardH
from Measurement import Measurement
from PauliY import PauliY
from GateRphi import GateRphi
from pathlib import Path
import cmath

#   wird nur für den custm Zustandsvektor benötigt
import numpy as np


class QuantumSimulation(Base):
    """
    In dieser Klasse sind die Hauptfunktionen des Programms definiert. Die hier definierten Funktionen erstellen
    Objekte der anderen Klassen. Diese Klassen erben von übergeordneeten Klassen, sodass Objekte nur aus den
    Kind-Klassen benötigt werden.

    Funktionen sind das Einlesen der Eingabe, das Initialisieren des Zustandsvektors und das Durchführen der Berechnung.
    Die Operationen werden in einer Liste gespeichert (Gatter, Messungen, Print Ausgaben) und nacheinander ausgeführt.
    """

    def __init__(self):
        super().__init__()

        #   Erstellen von Objekten, die in dieser Klasse benötigt werden
        self.qstate_obj = QState()
        self.operation_obj = Operation()
        self.qgate_obj = None

        #   alte Initialisierung
        #self.phi_in = []

        #   Initialzustand = Basiszustand ist standardmäßig 000.. --> Index 0 im Vektor
        self.index_of_basis_state = 0

        self.clear_memory = False
        self.interactive_input = False

    def calculate(self):
        """
        Funktion führt Operationen aus der Operation_List aus. Elemente dieser Liste werden abgearbeitet:
        Erstellt Objekt für Operation, und führt Multiplikation aus, wenn es ein Gatter ist. Wenn Messung oder der
        Befehl printdurchgeführt werden soll, wird die Multipligation Gate*State nicht ausgeführt, sondern der
        jeweilige Code.
        :return qstate_obj: Mit Ergebnis als Zustandsvektor.
        """

        #   Index in der operation_list
        i = 0

        #   Führe nacheinander die Operationen aus operation_obj.list_of_operations
        for operation in self.operation_obj.list_of_operations:

            #   Falls ein Element der Liste Indizes in der Liste operation[1] gespeichert hat, handelt es sich um ein
            #   Gatter, ansonsten um einen Befehl, wie print state (in der Form 'state')
            if operation[1]:
                #   In der mehr-Dimensionalen Liste list_of_operations wird aus dem Element mit dem aktuellen Index
                #   i, die Liste mit den Indizes der Qubits, auf welche das Gatter angewendet wird, ausgelesen.
                #   [ ['h', [1], []], ['cx', [0, 3, 6], [], [print_gates, [], []] ]
                list_affected_qubits = operation[1]
                list_of_parameters = operation[2]

                #   Erzeugen des benötigten Objekt für das Gatter (Gatter werden durch Konstruktor automatisch auf richtige
                #   Größe erweitert.
                if operation[0] == 'x':
                    self.qgate_obj = PauliX(list_affected_qubits)
                elif operation[0] == 'z':
                    self.qgate_obj = PauliZ(list_affected_qubits)
                elif operation[0] == 'h':
                    self.qgate_obj = HadamardH(list_affected_qubits)
                elif operation[0] == 'y':
                    self.qgate_obj = PauliY(list_affected_qubits)
                elif operation[0] == 'r_phi':
                    self.qgate_obj = GateRphi(list_affected_qubits, list_of_parameters)
                elif operation[0] == 's':
                    self.qgate_obj = GateRphi(list_affected_qubits, [cmath.pi/2])
                elif operation[0] == 's*':
                    self.qgate_obj = GateRphi(list_affected_qubits, [-cmath.pi/2])
                elif operation[0] == 't':
                    self.qgate_obj = GateRphi(list_affected_qubits, [cmath.pi/4])
                elif operation[0] == 't*':
                    self.qgate_obj = GateRphi(list_affected_qubits, [cmath.pi/4])
                elif operation[0] == 'm':

                    #   Erstelle Objekt für die Messung, dabei wird auch ein Objekt für das Entscheidungsdiagramm
                    #   erstellt --> Im Debug Modus: Ausgabe der einzelnen Schritte zum erstellen eines
                    #   Entscheidungsdiagramms
                    measure_obj = Measurement(self.qstate_obj.general_matrix, list_affected_qubits)

                    #   gebe Zustände des Zustandsvektors vor der Messung aus
                    if Base.get_verbose() >= 0:
                        print('\n---------------\t Measurement \t---------------\n')
                    if Base.get_verbose() >= 1:
                        print('States of the state vector before the measurement:')
                        print(self.qstate_obj, '\n')

                    #   Bei der Messung wird anstatt der Multiplikation unten, die Funktion measure() aufgerufen.
                    self.qstate_obj.general_matrix = measure_obj.measure()

                    #   gebe Zustände des Zustandsvektors nach der Messung aus
                    if Base.get_verbose() >= 1:
                        print('\nStates of the state vector after the measurement:')
                        print(self.qstate_obj, '\n')

                    # Index welches Tupel abgearbeitet wird, wird hochgezählt
                    i += 1

                    continue

                #   Das 'Gatter' custm überschreibt den bisherigen Zustand mit einem beliebigen Zustandsvektor, der hier
                #   gespeichert wurde, oder mit einem Initialzustand 000..000 für die richtige Anzahl an Qubits
                elif operation[0] == 'custm':

                    #   Falls die Anzahl an Qubits, der Anzahl aus dem gespeicherten Vektor entspricht, wird dieser
                    #   verwendet
                    if Base.getnqubits() == 5:
                        #qsim_obj.qstate_obj.general_matrix = np.array([0.080396894, 0.037517934, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0.143565882, 0.066997412, 0j, 0j, 0j, 0j, 0j, 0j, 0.777808047, 0j, 0.601700565, 0j, 0j, 0j, 0j, 0j])
                        #qsim_obj.qstate_obj.general_matrix = np.array([1, 1, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 1, 1, 0j, 0j, 0j, 0j, 0j, 0j, 1, 0j, 1, 0j, 0j, 0j, 0j, 0j])
                        self.qstate_obj.general_matrix = np.array([0, 0, 0.00752268163518088, 0, 0, 0, 0, 0, 0, 0, 0.306489370178815, 0.353641580975556, 0, 0, 0, 0, 0, 0, 0.286171213985822, 0.330197554599025, 0, 0, 0, 0, 0, 0.523233828563029, 0, 0.391028839851374, 0.283219972790003, 0.288323035362795, 0, 0])
                    else:
                        self.qstate_obj.general_matrix = np.zeros(Base.getnqubits())
                        self.qstate_obj.general_matrix[0] = 1


                    # Index welches Tupel abgearbeitet wird, wird hochgezählt
                    i += 1

                    continue

                #   Fehler: Operation wird als gültige Eingabe erkannt, ist oben aber nicht aufgeführt
                else:
                    raise Exception('Error: The following operation was not recognized as Error in '
                                    'QuantumSimulation.py: cmd_input_for_qsim(),\n'
                                    'but is not implemented in QuantumSimulation.py: calculate():', operation)

                #   Multiplikation führt Simulation aus: Neuer Zustandsvektor nachdem Gatter angewendet wurde
                #   (Messung wird ebenfalls durch den Operator __mul__() aufgerufen)
                self.qstate_obj = self.qgate_obj * self.qstate_obj

                # Index welches Tupel abgearbeitet wird, wird hochgezählt
                i += 1

            else:
                #   Gebe die aktuellen Zustände mit Wahrscheinlichkeit aus
                if operation[0] == 'print_states':
                    self.print_actual_states(False)

                #   Gebe den aktuellen Zustandsvektor als Vektor aus
                elif operation[0] == 'print_state_vec':
                    self.print_actual_states(True)

                #   Gebe die Liste der Operationen aus
                elif operation[0] == 'print_gates':
                    self.print_list_of_operations()

                #   Gebe den aktuell gespeicherten Initialzustand aus
                elif operation[0] == 'print_init_state':
                    self.print_init_state()

                # Index welches Tupel abgearbeitet wird, wird hochgezählt
                i += 1

        return self.qstate_obj

    #   Bitmuster kann als binäre Zahl in int umgewandelt werden, und wieder zurück. Vorgehen ist effizienter als
    #   String. Integer Zahl entspricht dann dem Index im Zustandsvektor, beginnend bei 0. Dadurch erfolgt leichtere
    #   Vektorzuordnung.
    #   Funktion erzeugt aus initialem Bitmuster im qstate_obj den zugehörigen Zustandsvektor
    #def init_qbit_sequence_to_statevec(self, bit_seq_as_str):
    #    """
    #    Funktion erzeugt aus dem eingelesenen Initalzustand den zugehörigen Zustandsvektor im QState-Objekt, welches
    #    in dieser Klasse enthalten ist. Der Initalzustand wird als String aus 0en und 1en übergeben.

    #    :param bit_seq_as_str: Der String des Initialzustandes kann als binäre Zahl in eine Dezimalzahl umgewandelt
    #    werden. Diese entspricht genau dem Index des Zustandes im Zustandsvektor. Dieses Vorgehen ist effizienter als
    #    die Verwendung des Strings.
    #    :return: void.
    #    """

    #    bit_seq_as_int = int(bit_seq_as_str, 2)
    #    self.qstate_obj = self.qstate_obj.init_vec_from_index(bit_seq_as_int)

    #   1
    def process_n_qubits(self, n_qubits):
        """
        Setzt die Anzahl der QUbits und initialisiert sie mit 0, sofern vorher der default Wert 0 war. In der
        interactiven Eingabe wird die Anzahl an Qubits durch den ersten Befhel festgelegt.
        :param n_qubits:
        :return:
        """

        #   Falls die bisherige Anzahl an Qubits noch 0 ist, wird die neue Anzahl gespeichert. Wird der Befehl
        #   interaktiv hintereinander aufgerufen, kann die Anzahl des ersten Befehls für alle nachfolgenden Befehle
        #   verwendet.
        if Base.getnqubits() == 0:

            #   Anzahl an Qubits wird gespeichert
            self.set_n_qubits(n_qubits)

            #   Wird für alte Initialisierung benötigt:
            #   In der Liste phi_in wird für jedes neue Qubit eine 0 hinzugefügt.
            #self.phi_in += (Base.getnqubits() - len(self.phi_in)) * [0]

        elif n_qubits != Base.getnqubits():
            print('Due to the previous setting the number of qubits is', Base.getnqubits(),
                  '. The new input of', n_qubits, 'qubits is ignored. Use --clear to delete memory.')

        #   Falls es bereits mehr Qubits gibt, wird eine Warnung ausgegeben und alle darüberliegenden Qubits gelöscht

        #    raise ValueError('Number of qubits have to be greater than 0:', Base.getnqubits())
        #    print('\nWarning!\n\tThe number of qubits was', Base.getnqubits(),
        #          'but should be set to', n_qubits, '\n\tThe number of qubits was set to', n_qubits,
        #          'and all qubits above were deleted! Output vector is now the initial state,\n\t'
        #          'because the previous state vector does not match the number of qubits anymore.')

            #   Speichere die Anzahl der Qubits
        #    self.set_n_qubits(n_qubits)

            #   Der aktuelle Zustandsvektor wird gelöscht, da sich die Anzahl der Qubits verändert hat
        #    self.qstate_obj.general_matrix = np.array([])

            #   Prüfen, dass Index wirklich weiter geht, als die neue Anzahl der Qubits
        #    if len(self.phi_in) > n_qubits:
        #        del self.phi_in[n_qubits:]

    #   2
    #def initialize_qubits(self, index, value):
    #    """
    #    Initialisiert ein Qubit mit dem Zustand 0 oder 1.
    #    :param index: Index des Qubits
    #    :param value: Zustand 0 oder 1
    #    :return:
    #    """

        #   Falls der Index des zu initialisierenden Qubits aus dem Bereich der Anzahl an Qubits hinaus geht,
        #   wird eine Warnung ausgegeben und die Anzahl angepasst.
        #        if index >= Base.getnqubits():
        #           print('\nWarnung!\n\tAnzahl der Qubits war', Base.getnqubits(), ', aber das Qubit mit Index',
        #                index, 'liegt darüber.\n\tDie Anzahl an Qubits wurde auf', index + 1,
        #               'geändert!\n')
        #        Base.set_n_qubits(index + 1)

        #   Der Liste der initialen Zustände der Qubits wird mit 0en für die neuen Qubits erweitert
        #   (Da die Anzahl jetzt beim ersten Mal festgelegt wird, ist len(phi_in) immer 0)
    #    self.phi_in += (Base.getnqubits() - len(self.phi_in)) * [0]

        #   Die Anzahl der Qubits soll nicht automatisch festgelegt werden
    #    if index >= Base.getnqubits():
    #        raise IndexError('The Index of a Qubit is aut of range. It does\'t fit to the number of Qubits.')

        #   Der Zustand wird in der Liste phi_in gespeichert
    #    self.phi_in[index] = value

    #   3
    def process_operation(self, operation_in):
        """
        Fügt die Gatter der Liste an Operationen hinzu.
        :param operation_in: Liste mit 0: Bezeichnung des Gatters/Befehl, 1: Liste der Indizes der Qubits, die das
         Gatter beeinflussen, 2: Liste der Parameter, die für das Gatter notwendig sind. Liste, die der Liste aller
         Operationen hinzugefügt wird
        :return:
        """

        #   Falls Operation ein Gatter ist, gibt es in der Liste mindestens 1 Index.
        if operation_in[1]:

            #   Wird ein Gatter auf ein Index über der Anzahl an Qubits angewendet, soll es einen Fehler geben
            if max(operation_in[1]) >= Base.getnqubits():
                raise IndexError('The Index of a gate is aut of range. It does\'t fit to the number of Qubits.')

        #   Der Operationen-Liste wird über die Funktion aus dem Operation-Objekt ein Tupel aus Gatter, Liste der
        #   betreffendem Qubits und Liste der Parameter hinzugefügt.
        self.operation_obj.add_operation_to_list([operation_in])

    def start_simulation(self):
        """
        Funktion prüft ob die Anzahl der Qubits größer 0 ist und ob in der Liste der Operationen Elemente vorhanden sind,
        und startet anschließend die Simulation.
        :return:
        """
        if Base.getnqubits() > 0 and self.operation_obj.list_of_operations:

            #   Falls im QState Objekt noch kein Vektor qsim_obj.general_matrix existiert, wird der neue Initialzustand
            #   verwendet
            if not any(self.qstate_obj.general_matrix):

                self.qstate_obj.init_vec_from_index(self.index_of_basis_state)

                #   Das Bitmuster für den initialen Zustand, wird aus der Liste in einem String gespeichert
                #phi_str = ""
                #for value in self.phi_in:
                #    phi_str += str(value)

                #   Diese Funktion wandelt das Bitmuster 0011 in eine 3 um, und ruft dann die Funktion
                #   init_vec_from_index(qsim_obj, int_in) in QState auf, die den zugehörigen Vektor im
                #   jeweiligen Objekt erzeugt
                #self.init_qbit_sequence_to_statevec(phi_str)

            #   Falls im QState Objekt bereits ein Vektor qsim_obj.general_matrix existiert, wird dieser als aktueller
            #   Zustandsvektor verwendet, auf den alle Operationen angewendet werden
            else:
                if Base.get_verbose() >= 0:
                    print('Using previous state vector instead of a new base state / initial state...\n'
                          '(use -c to start a completely new simulation)')

            #   Führe Berechnung der eingelesenen Eingabe durch
            self.qstate_obj = self.calculate()

            #   Ausgabe der Zustände nach der Simulation, falls vebose level 0 (nicht quiet)
            if Base.get_verbose() >= 0:
                print('\n---------------\t Simulation completed: \t---------------\n')
            print(self.qstate_obj, '\n\n\n')

        else:
            if Base.get_verbose() >= 0:
                print('\nSimulation was not started, the number of qubits is 0 or the list of operations is empty. '
                      'Type clii -h for help.\n')

    #   7
    def print_list_of_operations(self):
        """
        Funktion gibt die Liste der Operationen aus.
        :return:
        """

        if Base.get_verbose() >= 0:
            print('\n---------------\t List of operations: \t---------------\n')

            #   Falls in der Liste der Operationen Elemente vorhanden sind:
            if self.operation_obj.list_of_operations:
                print('\tGate/Command\t| Indices\t| Parameters')

                for operation in self.operation_obj.list_of_operations:
                    str_out = ''
                    if operation[1]:
                        str_out += '\t  ' + operation[0] + '\t\t|  ' + str(operation[1]) + '\t\t|  ' + str(operation[2]) + '\n'
                    else:
                        str_out += '\t ' + operation[0] + '\n'

                    print(str_out.rstrip())
                print('')
            else:
                print('The list is empty.\n')

        else:
            print(self.operation_obj.list_of_operations)

    #   7 ToDo: Möglichkeit als Vektor auszugeben
    def print_actual_states(self, as_vector):
        if Base.get_verbose() >= 0:
            print('\n---------------\t Output actual state: \t---------------\n')

        if as_vector:
            print(self.qstate_obj.general_matrix)
        else:
            print(self.qstate_obj)

    #   7
    def print_init_state(self):
        """
        Die Funktion gibt den Initialzustand aus.
        :return:
        """

        #   Ausgabestring erstellen
        #   For-Schleife notwendig, da Liste in String gespeichert werden soll. Mit Strings konnte vorher
        #   nicht gearbeitet werden, da z.B. bsp_str[2]='g' nicht funktioniert.
        phi_str = "|"
        phi_str += str(bin(self.index_of_basis_state)[2:])
        phi_str += ")"

        print('\n---------------\t Output initial state: \t---------------\n'
              'The initial state in dirac notation is', phi_str, '.')

    #   8
    def clear_mem(self):
        """
        Diese Funktion löscht die Liste der Operationen, die Anzahl der Qubits und den Initialzustand.
        Sie löscht aber keine Objekte. Das ist bisher nicht nötig wegen der GarbageCollection.
        """

        #   Entferne alle Gatter in der Liste aller Operationen, die ausgeführt werden sollen
        self.operation_obj.list_of_operations = []

        #   Setze die Anzahl der Qubits auf 0
        self.set_n_qubits(0)

        #   Lösche die Initialisierung aller Qubits (Default-Basiszustand 0000..0)
        self.index_of_basis_state = 0

        #   Lösche den aktuellen Zustandsvektor
        self.qstate_obj.general_matrix = np.array([])
