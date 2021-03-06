#!/usr/bin/env python3
#   Projektarbeit "Recherche und Tool zur Simulation von Quantenschaltungen im Bereich Quantencomputing"
#   Author: Lukas Lepper, 24.11.2020
#   Betreuer: Dipl.-Ing. Martin Hardieck
#   Dateiname: main.py
#   Version: 0.6

#   Klassen importieren, mit deren Memberfunktionen gearbeitet werden muss.
#   Die Klasse QuantumSimulation bietet die Hauptfunktionen für die Simulation an, die in der main gesteuert wird.
#   Sie benötigt daher Zugriff auf alle anderen Unterklassen der untersten Ebene. In den Funktionen dieser Hauptklasse
#   werden daher Objekte der untersten Ebene erzeugt. Die Klassen dieser Ebene erben von den darüber liegenden Klassen,
#   sodass alle Funktionen/Variablen in der Hauptklasse erreichbar sind.
from QuantumSimulation import QuantumSimulation
from Base import Base

import sys
import argparse
import math

"""
Die Klassen ValidateInitialization, ValidateGate, ValidatePrint und CheckFilePath definieren benutzerdefinierte Aktionen 
für den Parser.
Dieser ist nachfolgend in der Funktion cmd_line_parser() implementiert. Je nach subcommand werden die 
Funktionen process_cli() oder process_file() aufgerufen, welche danach implementiert sind. 
Danach folgt der Programmstart mit if __name__ == '__main__': (siehe ganz unten).
"""


class ValidateInitialization(argparse.Action, Base):
    """
    Klasse mit einer benutzerdefinierten Argparse Akion, um zu Prüfen, ob die Eingabe für die Initialisierung der
    Qubits -i 0011010 gültig ist. Die eingegebenen Initialisierung wird als int umgewandelt im namespace gespeichert.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        #   Tupel mit den gültigen Werten, die für die Zustände der Qubits erlaubt sind
        valid_states = (0, 1)

        #   Speichere die länge des Bitmusters, um die Anzahl der mindestens verwendeten Qubits festzustellen
        j = len(values)

        #   Wandle Bitmuster in int um 0*2^3 + 1*2^2 + 1*2^1 + 0*2^0
        index_in_vec = 0
        for i, x in enumerate(values):
            try:
                #   Ist x 0 oder 1 wird Index im Zustandsvektor wie oben berechnet (j - 1, da von 0-2 statt 1-3
                if int(x) in valid_states:
                    index_in_vec += int(x) * pow(2, j - i - 1)

                #   Falls x eine andere Zahl ist --> Fehler
                else:
                    raise argparse.ArgumentError(message='Only 0 and 1 are allowed for the states in the bit pattern.'
                                                         ' Got {}.'.format(values),
                                                 argument=self)
            #   Falls x nicht in int konvertiert werden kann --> Fehler
            except ValueError:
                raise argparse.ArgumentError(message='Only 0 and 1 are allowed for the states in the bit pattern.'
                                                     ' Got {}.'.format(values),
                                             argument=self)

        #   In namespace von dem aktuellen Parsor wird die neue Liste Items an der Stelle der alten Liste gespeichert
        setattr(namespace, self.dest, index_in_vec)


class ValidateGate(argparse.Action):
    """
    Klasse mit einer benutzerdefinierten Argparse Akion, um zu Prüfen, ob die Eingabe für das Gatter gültig ist.
    -g GATE INDEX [INDEX ... PARAMETER ...] Die beiden Parameter werden in der Liste der eingegebenen Gatter
    qsim_obj.dest gespeichert.
    """

    def __call__(self, parser, namespace, values, option_string=None):

        #   Wurde nur ein Parameter -g m eingegeben, wird eine Fehlermeldung ausgegeben, da mindestens ein Index
        #   für alle Gatter erforderlich ist.
        if len(values) <= 1:
            raise argparse.ArgumentError(self, 'Missing values for --gate GATE INDEX ...INDEX')

        #   Speicher den ersten Parameter, der eingegeben wurde. Er bezeichnet das Gatter
        gate = values[0]

        #   Speichere die eingegebenen Argumente in einer Liste
        list_of_arguments = values[1:]

        list_of_indizes = []
        list_of_parameters = []

        #   Tupel mit allen möglichen Parametern, die für Gatter stehen, welche auf ein einzelnes Qubit angewendet
        #   werden und daher nur einen Index-Parameter benötigen
        valid_gates = ('x', 'h', 'z', 'm', 'custm', 'p', 'y', 's', 'sdg', 't', 'tdg', 'i', 'u3', 'cnot', 'cx',
                       'toffoli', 'to', 'fredkin', 'f', 'cswap', 'csw', 'deutsch', 'd', 'swap', 'sw', 'sqrt_swap', 'srs'
                       , 'rx', 'sqrt_not', 'ry', 'u2', 'u1', 'cp', 'cx', 'cy', 'cz', 'xx', 'yy',
                       'zz', 'rz', 'r', 'cr')

        #   Prüfe, ob das eingegebene Gatter in dem Tupel der möglichen Gatter vorkommt.
        #   Falls nein, wird eine Fehlermeldung ausgegeben und das Programm abgebrochen
        if gate not in valid_gates:
            raise argparse.ArgumentError(self, 'Invalid gate: {s!r}'.format(s=gate))

        #   Gates that change 1 qubit, need only one argument:
        #   Tupel mit allen möglichen Parametern, die für Gatter stehen, welche auf ein einzelnes Qubit angewendet
        #   werden und daher nur einen Index-Parameter benötigen
        gates_1_qb = ('x', 'h', 'z', 'm', 'custm', 'y', 's', 'sdg', 't', 'tdg', 'i', 'sqrt_not')

        #   Falls das aktuelle Gatter in dieser Liste vorkommt, sollte es nur einen Index haben:
        if gate in gates_1_qb:

            #   Gehe die Liste der Indizes nacheinander durch. i ist der Index des aktuellen Elements in der Liste,
            #   x das Element selber
            for i, x in enumerate(list_of_arguments):

                #   Fehlermeldung, wenn mehr Indizes eingegeben wurden
                if len(list_of_arguments) != 1:
                    raise argparse.ArgumentError(self, 'The number of arguments ({r!r}) does not match the required '
                                                       'number of this gate ({s!r}: 1). Example: -g {s} INDEX'
                                                 .format(r=len(list_of_arguments), s=gate))

                #   Versuche das aktuelle Element x in Integer zu konvertieren, sonst gebe eine Fehlermeldung aus
                #   Als Eingabe werden ganze Zahlen erwartet.
                try:
                    list_of_arguments[i] = int(x)
                except ValueError:
                    raise argparse.ArgumentError(self, 'Value Error: {a!r} can\'t be converted to integer, for index'
                                                       ' of the qubit an integer was expected.'.format(a=x))

                #   Falls die Zahl negativ ist, wird ebenfalls ein Fehler ausgegeben
                if list_of_arguments[0] < 0:
                    raise argparse.ArgumentError(self, 'Value Error: the index for a qubit must be positive: {a!r}'
                                                 .format(a=list_of_arguments[i]))

            #   Nach der Prüfung wird der Liste der Indizes die Elemente der Liste der Argumente hinzugefügt. Jetzt ist
            #   dort lediglich 1 Index gespeichert.
            list_of_indizes = list_of_arguments

        #   Gates that needs one index and one parameter (gate change 1 Qubits and need 1 additional parameter):
        gates_1_1 = ('p', 'u1', 'rx', 'ry', 'rz')

        #   Falls das aktuelle Gatter in dieser Liste vorkommt, sollte es nur einen Index haben:
        if gate in gates_1_1:

            #   Fehlermelduung, wenn mehr Indizes/Argumente eingegeben wurden
            if len(list_of_arguments) != 2:
                if gate == 'p':
                    raise argparse.ArgumentError(self, 'The number of arguments ({r!r}) does not match the required '
                                                       'number of this gate ({s!r}: 2). Example: -g {s} INDEX PARAM_PHI'
                                                 .format(r=len(list_of_arguments), s=str(gate)))
                elif gate == 'u1':
                    raise argparse.ArgumentError(self, 'The number of arguments ({r!r}) does not match the required '
                                                       'number of this gate ({s!r}: 2). Example: -g {s} INDEX PARAM_LAMBDA'
                                                 .format(r=len(list_of_arguments), s=str(gate)))
                elif gate == 'rx' or gate == 'ry':
                    raise argparse.ArgumentError(self, 'The number of arguments ({r!r}) does not match the required '
                                                       'number of this gate ({s!r}: 2). Example: -g {s} INDEX PARAM_THETA'
                                                 .format(r=len(list_of_arguments), s=str(gate)))
                elif gate == 'rz':
                    raise argparse.ArgumentError(self, 'The number of arguments ({r!r}) does not match the required '
                                                       'number of this gate ({s!r}: 2). Example: -g {s} INDEX PARAM_PHI'
                                                 .format(r=len(list_of_arguments), s=str(gate)))
                else:
                    raise argparse.ArgumentError(self, 'The number of arguments ({r!r}) does not match the required '
                                                       'number of this gate ({s!r}: 2). Example: -g {s} INDEX PARAM'
                                                 .format(r=len(list_of_arguments), s=str(gate)))

            #   Versuche die Argumente in Float oder Integer zu konvertieren, sonst gebe eine Fehlermeldung aus.
            #   Als Eingabe werden ganze Zahlen für Indizes und Fließkommazahlen für Parameter von Gattern erwartet.
            try:
                list_of_arguments[0] = int(list_of_arguments[0])
            except ValueError:
                raise argparse.ArgumentError(self, 'Value Error: {a!r} can\'t be converted to integer, for index'
                                                   ' of the qubit an integer was expected.'
                                                   ''.format(a=list_of_arguments[0]))

            try:
                list_of_arguments[1] = float(list_of_arguments[1])
            except ValueError:
                raise argparse.ArgumentError(self, 'Value Error: {a!r} can\'t be converted to float, for index'
                                                   ' of the qubit an integer and for gate arguments float '
                                                   'was expected.'.format(a=list_of_arguments[1]))

            #   Falls der Index negativ ist, wird ebenfalls ein Fehler ausgegeben
            if list_of_arguments[0] < 0:
                raise argparse.ArgumentError(self, 'Value Error: the index for a qubit must be positive: {a!r}'
                                             .format(a=list_of_arguments[0]))

            #   Nach der Prüfung wird der eine Index und der eine Parameter jeweils der Liste hinzugefügt
            list_of_indizes = [list_of_arguments[0]]
            list_of_parameters = [list_of_arguments[1]]

        #   Gates that needs one index and three arguments (gate change 1 Qubits and need 3 additional parameters):
        gates_1_3 = ('u3', 'VVVVV')

        #   Falls das aktuelle Gatter in dieser Liste vorkommt, sollte es nur einen Index haben:
        if gate in gates_1_3:

            #   Fehlermeldung, wenn mehr Indizes/Argumente eingegeben wurden
            if len(list_of_arguments) != 4:
                raise argparse.ArgumentError(self, 'The number of arguments ({r!r}) does not match the required '
                                                   'number of this gate ({s!r}: 4). Example: -g {s} INDEX PARAM_THETA '
                                                   'PARAM_PHI PARAM_LAMBDA'
                                             .format(r=len(list_of_arguments), s=str(gate)))

            #   Versuche die Argumente in Float oder Integer zu konvertieren, sonst gebe eine Fehlermeldung aus.
            #   Als Eingabe werden ganze Zahlen für Indizes und Fließkommazahlen für Parameter von Gattern erwartet.
            try:
                list_of_arguments[0] = int(list_of_arguments[0])
            except ValueError:
                raise argparse.ArgumentError(self, 'Value Error: {a!r} can\'t be converted to integer, for index'
                                                   ' of the qubit an integer was expected.'
                                                   ''.format(a=list_of_arguments[0]))

            #   Versuche jedes Argument in der Liste, ab dem Index wo die Parameter vom Gatter gepseichert sind,
            #   in float zu konvertieren.
            for i, arg in enumerate(list_of_arguments):
                if i >= 1:
                    try:
                        list_of_arguments[i] = float(list_of_arguments[i])
                    except ValueError:
                        raise argparse.ArgumentError(self,
                                                     'Value Error: {a!r} can\'t be converted to float, for index'
                                                     ' of the qubit an integer and for gate arguments float '
                                                     'was expected.'.format(a=list_of_arguments[i]))

            #   Falls der Index negativ ist, wird ebenfalls ein Fehler ausgegeben
            if list_of_arguments[0] < 0:
                raise argparse.ArgumentError(self, 'Value Error: the index for a qubit must be positive: {a!r}'
                                             .format(a=list_of_arguments[0]))

            #   Nach der Prüfung wird der eine Index und der eine Parameter jeweils der Liste hinzugefügt
            list_of_indizes = [list_of_arguments[0]]
            list_of_parameters = list_of_arguments[1:]

        #   Gates that change 2 qubit, need 2 indizes:
        #   Tupel mit allen möglichen Parametern, die für Gatter stehen, welche auf ein einzelnes Qubit angewendet
        #   werden und daher nur einen Index-Parameter benötigen
        gates_2_0 = ('cnot', 'cx', 'swap', 'sw', 'sqrt_swap', 'srs', 'cx', 'cy', 'cz')

        #   Falls das aktuelle Gatter in dieser Liste vorkommt, sollte es nur einen Index haben:
        if gate in gates_2_0:

            #   Gehe die Liste der Indizes nacheinander durch. i ist der Index des aktuellen Elements in der Liste,
            #   x das Element selber
            for i, x in enumerate(list_of_arguments):

                #   Fehlermeldung, wenn mehr Indizes eingegeben wurden
                if len(list_of_arguments) != 2:
                    if gate[0] == 'c':
                        raise argparse.ArgumentError(self, 'The number of arguments ({r!r}) does not match the required'
                                                           ' number of this gate ({s!r}: 2). Example: -g {s} '
                                                           'INDEX_CONTROL INDEX_TARGET'
                                                     .format(r=len(list_of_arguments), s=gate))
                    if gate[0] == 's':
                        raise argparse.ArgumentError(self, 'The number of arguments ({r!r}) does not match the required'
                                                           ' number of this gate ({s!r}: 2). Example: -g {s} '
                                                           'INDEX_1 INDEX_2'
                                                     .format(r=len(list_of_arguments), s=gate))

                #   Versuche das aktuelle Element x in Integer zu konvertieren, sonst gebe eine Fehlermeldung aus
                #   Als Eingabe werden ganze Zahlen erwartet.
                try:
                    list_of_arguments[i] = int(x)
                except ValueError:
                    raise argparse.ArgumentError(self, 'Value Error: {a!r} can\'t be converted to integer, for index'
                                                       ' of the qubit an integer was expected.'.format(a=x))

                #   Falls die Zahl negativ ist, wird ebenfalls ein Fehler ausgegeben
                if list_of_arguments[i] < 0:
                    raise argparse.ArgumentError(self, 'Value Error: the index for a qubit must be positive: {a!r}'
                                                 .format(a=list_of_arguments[i]))

            #   Nach der Prüfung wird der Liste der Indizes die Elemente der Liste der Argumente hinzugefügt.
            list_of_indizes = list_of_arguments

        #   Gates that change 3 qubit, need 3 indizes:
        #   Tupel mit allen möglichen Parametern, die für Gatter stehen, welche auf ein einzelnes Qubit angewendet
        #   werden und daher nur einen Index-Parameter benötigen
        gates_3_0 = ('toffoli', 'to', 'fredkin', 'f', 'cswap', 'csw')

        #   Falls das aktuelle Gatter in dieser Liste vorkommt, sollte es nur einen Index haben:
        if gate in gates_3_0:

            #   Gehe die Liste der Indizes nacheinander durch. i ist der Index des aktuellen Elements in der Liste,
            #   x das Element selber
            for i, x in enumerate(list_of_arguments):

                #   Fehlermeldung, wenn mehr Indizes eingegeben wurden
                if len(list_of_arguments) != 3:
                    if gate == 'toffoli' or gate == 'to':
                        raise argparse.ArgumentError(self, 'The number of arguments ({r!r}) does not match the required'
                                                           ' number of this gate ({s!r}: 3). Example: -g {s} '
                                                           'INDEX_CONTROL_1 INDEX_CONTROL_2 INDEX_TARGET'
                                                     .format(r=len(list_of_arguments), s=gate))
                    if gate == 'fredkin' or gate == 'cswap' or gate == 'f':
                        raise argparse.ArgumentError(self, 'The number of arguments ({r!r}) does not match the required'
                                                           ' number of this gate ({s!r}: 3). Example: -g {s} '
                                                           'INDEX_CONTROL INDEX_TARGET_1 INDEX_TARGET_2'
                                                     .format(r=len(list_of_arguments), s=gate))
                    raise argparse.ArgumentError(self, 'The number of arguments ({r!r}) does not match the required'
                                                       ' number of this gate ({s!r}: 3). Example: forgotten to '
                                                       'implement'.format(r=len(list_of_arguments), s=gate))

                #   Versuche das aktuelle Element x in Integer zu konvertieren, sonst gebe eine Fehlermeldung aus
                #   Als Eingabe werden ganze Zahlen erwartet.
                try:
                    list_of_arguments[i] = int(x)
                except ValueError:
                    raise argparse.ArgumentError(self, 'Value Error: {a!r} can\'t be converted to integer, for index'
                                                       ' of the qubit an integer was expected.'.format(a=x))

                #   Falls die Zahl negativ ist, wird ebenfalls ein Fehler ausgegeben
                if list_of_arguments[i] < 0:
                    raise argparse.ArgumentError(self, 'Value Error: the index for a qubit must be positive: {a!r}'
                                                 .format(a=list_of_arguments[i]))

            #   Nach der Prüfung wird der Liste der Indizes die Elemente der Liste der Argumente hinzugefügt.
            list_of_indizes = list_of_arguments

        #   Gates that needs 3 indices and one parameter (gate change 3 Qubits and need 1 additional parameter):
        gates_3_1 = ('deutsch', 'd')

        #   Falls das aktuelle Gatter in dieser Liste vorkommt, sollte es nur einen Index haben:
        if gate in gates_3_1:

            #   Fehlermelduung, wenn mehr Indizes/Argumente eingegeben wurden
            if len(list_of_arguments) != 4:
                raise argparse.ArgumentError(self, 'The number of arguments ({r!r}) does not match the required '
                                                   'number of this gate ({s!r}: 4). Example: -g {s} INDEX_CONTROL_1'
                                                   ' INDEX_CONTROL_2 INDEX_TARGET PARAM_THETA'
                                             .format(r=len(list_of_arguments), s=str(gate)))

            #   Gehe die Liste der Indizes nacheinander durch. i ist der Index des aktuellen Elements in der Liste,
            #   x das Element selber
            for i, x in enumerate(list_of_arguments[0:3]):

                #   Versuche die Argumente in Float oder Integer zu konvertieren, sonst gebe eine Fehlermeldung aus.
                #   Als Eingabe werden ganze Zahlen für Indizes und Fließkommazahlen für Parameter von Gattern erwartet.
                try:
                    list_of_arguments[i] = int(list_of_arguments[i])
                except ValueError:
                    raise argparse.ArgumentError(self, 'Value Error: {a!r} can\'t be converted to integer, for index'
                                                       ' of the qubit an integer was expected.'
                                                       ''.format(a=list_of_arguments[i]))

                #   Falls der Index negativ ist, wird ebenfalls ein Fehler ausgegeben
                if list_of_arguments[i] < 0:
                    raise argparse.ArgumentError(self, 'Value Error: the index for a qubit must be positive: {a!r}'
                                                 .format(a=list_of_arguments[i]))

            try:
                list_of_arguments[3] = float(list_of_arguments[3])
            except ValueError:
                raise argparse.ArgumentError(self, 'Value Error: {a!r} can\'t be converted to float, for index'
                                                   ' of the qubit an integer and for gate arguments float '
                                                   'was expected.'.format(a=list_of_arguments[3]))

            #   Nach der Prüfung wird der eine Index und der eine Parameter jeweils der Liste hinzugefügt
            list_of_indizes = list_of_arguments[0:3]
            list_of_parameters = [list_of_arguments[3]]

        #   Gates that needs one index and 2 parameters (gate change 1 Qubits and need 2 additional parameter):
        gates_1_2 = ('u2', 'r')

        #   Falls das aktuelle Gatter in dieser Liste vorkommt, sollte es nur einen Index haben:
        if gate in gates_1_2:

            #   Fehlermelduung, wenn mehr Indizes/Argumente eingegeben wurden
            if len(list_of_arguments) != 3:
                if gate == 'u2':
                    raise argparse.ArgumentError(self, 'The number of arguments ({r!r}) does not match the required '
                                                       'number of this gate ({s!r}: 3). Example: -g {s} INDEX PARAM_PHI'
                                                       ' PARAM_LAMBDA'
                                                 .format(r=len(list_of_arguments), s=str(gate)))
                else:  # gate == 'r':
                    raise argparse.ArgumentError(self, 'The number of arguments ({r!r}) does not match the required '
                                                       'number of this gate ({s!r}: 3). Example: -g {s} INDEX THETA'
                                                       ' PHI'
                                                 .format(r=len(list_of_arguments), s=str(gate)))

            #   Versuche die Argumente in Float oder Integer zu konvertieren, sonst gebe eine Fehlermeldung aus.
            #   Als Eingabe werden ganze Zahlen für Indizes und Fließkommazahlen für Parameter von Gattern erwartet.
            try:
                list_of_arguments[0] = int(list_of_arguments[0])
            except ValueError:
                raise argparse.ArgumentError(self, 'Value Error: {a!r} can\'t be converted to integer, for index'
                                                   ' of the qubit an integer was expected.'
                                                   ''.format(a=list_of_arguments[0]))

            #   Versuche jedes Argument in der Liste, ab dem Index wo die Parameter vom Gatter gepspeichert sind,
            #   in float zu konvertieren.
            for i, arg in enumerate(list_of_arguments):
                if i >= 1:
                    try:
                        list_of_arguments[i] = float(list_of_arguments[i])
                    except ValueError:
                        raise argparse.ArgumentError(self,
                                                     'Value Error: {a!r} can\'t be converted to float, for index'
                                                     ' of the qubit an integer and for gate arguments float '
                                                     'was expected.'.format(a=list_of_arguments[i]))

            #   Falls der Index negativ ist, wird ebenfalls ein Fehler ausgegeben
            if list_of_arguments[0] < 0:
                raise argparse.ArgumentError(self, 'Value Error: the index for a qubit must be positive: {a!r}'
                                             .format(a=list_of_arguments[0]))

            #   Nach der Prüfung wird der eine Index und der eine Parameter jeweils der Liste hinzugefügt
            list_of_indizes = [list_of_arguments[0]]
            list_of_parameters = list_of_arguments[1:]

        #   Gates that needs 2 indices and one parameter (gate change 2 Qubits and need 1 additional parameter):
        gates_2_1 = ('cp', 'xx', 'yy', 'zz')

        #   Falls das aktuelle Gatter in dieser Liste vorkommt, sollte es zwei Indizes haben:
        if gate in gates_2_1:

            #   Fehlermelduung, wenn mehr Indizes/Argumente eingegeben wurden
            if len(list_of_arguments) != 3:
                if gate == 'cp':
                    raise argparse.ArgumentError(self, 'The number of arguments ({r!r}) does not match the required '
                                                       'number of this gate ({s!r}: 3). Example: -g {s} INDEX_CONTROL'
                                                       ' INDEX_TARGET PARAM_PHI'
                                                 .format(r=len(list_of_arguments), s=str(gate)))
                else:
                    raise argparse.ArgumentError(self, 'The number of arguments ({r!r}) does not match the required '
                                                       'number of this gate ({s!r}: 3). Example: -g {s} INDEX_1'
                                                       ' INDEX_2 PARAM_PHI'
                                                 .format(r=len(list_of_arguments), s=str(gate)))

            #   Gehe die Liste der Indizes nacheinander durch. i ist der Index des aktuellen Elements in der Liste,
            #   x das Element selber
            for i, x in enumerate(list_of_arguments[0:2]):

                #   Versuche die Argumente in Float oder Integer zu konvertieren, sonst gebe eine Fehlermeldung aus.
                #   Als Eingabe werden ganze Zahlen für Indizes und Fließkommazahlen für Parameter von Gattern erwartet.
                try:
                    list_of_arguments[i] = int(list_of_arguments[i])
                except ValueError:
                    raise argparse.ArgumentError(self, 'Value Error: {a!r} can\'t be converted to integer, for index'
                                                       ' of the qubit an integer was expected.'
                                                       ''.format(a=list_of_arguments[i]))

                #   Falls der Index negativ ist, wird ebenfalls ein Fehler ausgegeben
                if list_of_arguments[i] < 0:
                    raise argparse.ArgumentError(self, 'Value Error: the index for a qubit must be positive: {a!r}'
                                                 .format(a=list_of_arguments[i]))

            try:
                list_of_arguments[2] = float(list_of_arguments[2])
            except ValueError:
                raise argparse.ArgumentError(self, 'Value Error: {a!r} can\'t be converted to float, for index'
                                                   ' of the qubit an integer and for gate arguments float '
                                                   'was expected.'.format(a=list_of_arguments[2]))

            #   Nach der Prüfung wird der eine Index und der eine Parameter jeweils der Liste hinzugefügt
            list_of_indizes = list_of_arguments[0:2]
            list_of_parameters = [list_of_arguments[2]]

        #   Gates that needs 2 indices and 2 parameter (gate change 2 Qubits and need 2 additional parameters):
        gates_2_2 = ('cr', 'ccccccc')

        #   Falls das aktuelle Gatter in dieser Liste vorkommt, sollte es zwei Indizes haben:
        if gate in gates_2_2:

            #   Fehlermelduung, wenn mehr Indizes/Argumente eingegeben wurden
            if len(list_of_arguments) != 4:
                if gate == 'cr':
                    raise argparse.ArgumentError(self, 'The number of arguments ({r!r}) does not match the required '
                                                       'number of this gate ({s!r}: 4). Example: -g {s} INDEX_CONTROL'
                                                       ' INDEX_TARGET PARAM_THETA PARAM_PHI'
                                                 .format(r=len(list_of_arguments), s=str(gate)))
                else:
                    raise argparse.ArgumentError(self, 'The number of arguments ({r!r}) does not match the required '
                                                       'number of this gate ({s!r}: 4). Example: Not implemented'
                                                 .format(r=len(list_of_arguments), s=str(gate)))

            #   Gehe die Liste der Indizes nacheinander durch. i ist der Index des aktuellen Elements in der Liste,
            #   x das Element selber
            for i, x in enumerate(list_of_arguments[0:2]):

                #   Versuche die Argumente in Float oder Integer zu konvertieren, sonst gebe eine Fehlermeldung aus.
                #   Als Eingabe werden ganze Zahlen für Indizes und Fließkommazahlen für Parameter von Gattern erwartet.
                try:
                    list_of_arguments[i] = int(list_of_arguments[i])
                except ValueError:
                    raise argparse.ArgumentError(self, 'Value Error: {a!r} can\'t be converted to integer, for index'
                                                       ' of the qubit an integer was expected.'
                                                       ''.format(a=list_of_arguments[i]))

                #   Falls der Index negativ ist, wird ebenfalls ein Fehler ausgegeben
                if list_of_arguments[i] < 0:
                    raise argparse.ArgumentError(self, 'Value Error: the index for a qubit must be positive: {a!r}'
                                                 .format(a=list_of_arguments[i]))

            #   Gehe die Liste der Indizes nacheinander durch. i ist der Index des aktuellen Elements in der Liste,
            #   x das Element selber
            for i, x in enumerate(list_of_arguments[2:4]):
                try:
                    list_of_arguments[i+2] = float(list_of_arguments[i+2])
                except ValueError:
                    raise argparse.ArgumentError(self, 'Value Error: {a!r} can\'t be converted to float, for index'
                                                       ' of the qubit an integer and for gate arguments float '
                                                       'was expected.'.format(a=list_of_arguments[i]))


            #   Nach der Prüfung wird der eine Index und der eine Parameter jeweils der Liste hinzugefügt
            list_of_indizes = list_of_arguments[0:2]
            list_of_parameters = list_of_arguments[2:4]

        #   Ein neues Element wird aus dem geprüften Gatter und der Liste der Indizes erstellt. Das Element besteht aus
        #   der bezeichnung für das Gatter, einer Liste mit Indizes der Qubits, auf die das Gatter angewendet wird,
        #   und eine Liste mit Parametern, die für die Gatter benötigt werden
        new_item = [gate, list_of_indizes, list_of_parameters]

        #   Die alte Liste der bisherigen Gatter/Operationen wird gespeichert
        items = getattr(namespace, self.dest, None)

        #   Falls in dieser Liste bereits Gatter/Operationen enthalten sind, wird das neue Element ['m', 1]
        #   der Liste angehängt.
        if items:
            items.append(new_item)

        #   Ansonsten wird eine neue Liste mit dem aktuellen Element erstellt
        else:
            items = [new_item]

        #   Die bearbeitete Liste wird an der alten Position im Parsor gespeichert
        setattr(namespace, self.dest, items)


class CheckFilePath(argparse.Action):
    """
    Klasse mit einer benutzerdefinierten Argparse Akion, um zu Prüfen, ob die Eingabe für den Dateipfad gültig ist.
    Es wird geprüft, ob die Datei existiert. Dann werden die Befehle eingelesen und als Liste an der Stelle gespeichert,
    wo vorher der Dateipfad übergeben wurde.
    """

    def __call__(self, parser, namespace, values, option_string=None):

        list_of_cmds = []

        try:
            #   Öffne die Datei, wenn möglich, und Schließe sie wieder am Ende der Umgebung. Ansonsten wird automatisch
            #   eine Fehlermeldung ausgegeben.
            with open(values) as file:

                #   Lese die gesammte Datei, Zeile für Zeile ein, und Speichere sie in einer Liste
                list_of_cmds = file.readlines()
        except FileNotFoundError:
            raise argparse.ArgumentError(self, 'FileNotFoundError: The following file could not be opened: {a!r}'
                                         .format(a=values))
        except OSError:
            raise argparse.ArgumentError(self, 'OSError: The following file could not be opened: {a!r}'
                                         .format(a=values))

        #   Erstelle eine neue Liste, in der gleich die eingelesenen Parameter gespeichert werden. Sie beginnt mit
        #   'cli', da diese Liste nach dem ArgParse aufruf in einen neuen Parser eingegeben wird. (Aktuell erfolgt die
        #   Eingabe des Schaltungsaufbaus entweder in der Datei, oder in dim Command Line Interface)
        args_list_from_file = []

        #   Zeile für Zeile werden die Parameter eingelesen und in der Liste oben angehängt
        for cmd in list_of_cmds:
            #   rstrip() entfernt Leerzeichen und Zeilenumbrüche am Ende eines Strings
            #   split() trennt String nach den Leerzeichen --> Aus Parameter mit Argumenten pro Zeile / Element in
            #   der Liste wird Liste mit neuen Elementen für jedes Argument
            args_list_from_file += cmd.rstrip().split()

        #   Führe den Parser mit den eingelesenen Argumenten aus, und speichere sie im selben namespace im selben Objekt
        parser.parse_args(args_list_from_file, namespace)

        #   Speichere die neue Liste mit den eingelesenen Parametern am selben Ort, wo vorher der Dateipfad
        #   übergeben wurde
        setattr(namespace, self.dest, values)


class ValidatePrint(argparse.Action):
    """
    Klasse mit einer benutzerdefinierten Argparse Akion. Prüfen, ob die Eingabe für print gültig ist, erfolgt schon
    vorher mit choice={...}.
    Außerdem wird der Print Befehl der Liste aller Operationen hinzugefügt.
    -p {state_vec, states, gates}
    """

    def __call__(self, parser, namespace, values, option_string=None):

        #   Die alte Liste der bisherigen Operationen wird gespeichert
        items = getattr(namespace, self.dest, None)

        str_out = 'print_' + values
        #   new_item wird der Liste der Operationen hinzugefügt, jedes Element hat dann eine Bezeichnung für das Gatter
        #   oder den Befehl wie print, eine Liste mit Indizes und eine Liste mit Parametern
        new_item = [str_out, [], []]

        #   Falls in dieser Liste bereits Operationen enthalten sind, wird das neue Element ['print', 'STATE|GATE']
        #   der Liste angehängt.
        if items:
            items.append(new_item)

        #   Ansonsten wird eine neue Liste mit dem aktuellen Element erstellt
        else:
            items = [new_item]

        #   Die bearbeitete Liste wird an der alten Position im Parsor gespeichert
        setattr(namespace, self.dest, items)


def exit_interactiv_in(q_sim, args):
    """
    Funktion die ausgeführt wird, um den interaktiven Eingabemodus zu beenden. Sie ändert einfach die Variable in
    welcher der aktuelle Zustand gespeichert ist.

    :param q_sim: Objekt indem die Variable ist
    :param args: args wird hier nicht benötigt, allerdings muss der Parameter vohanden sein, da der Parser je nach
        Befehl verschiedene Funktionen, aber mit dem selben Aufbau aufruft (Siehe args.function)
    :return:
    """
    q_sim.interactive_input = False


def cmd_line_parser(q_sim, cmd_in):
    """
    Funktion für den Befehl-Parser. Sie wird direkt beim Programmstart mit den übergebenen Argumenten aufgerufen, oder
    iin der Schleife, wenn der interaktive Eingabemodus aktiviert ist.

    :param q_sim: Objekt, aus der Klasse QuantumSimulation um die Simulation zu steuern und in dem Memberfunktionen zur
        Speicherung und Verarbeitung der eingelesenen Argumente vorhanden sind.
    :param cmd_in: Eingegebene Argumente des Befehls.
    :return:
    """
    #   Parser-Objekt erstellen
    parser = argparse.ArgumentParser(prog='Quantum Simulation',
                                     description='Simulation of quantum algorithm. Input parameters for simulation by '
                                                 'using arguments from commandline and file. \nExample:\n'
                                                 '-v 3 --interactive_input -n 3 -i 011 -g h 0 -g z 0 -p state_vec '
                                                 '-g r_phi 0 1.570796327 -p gates -g m 0',
                                     epilog='by Lukas Lepper')

    #   Default-Wert für Parser, damit if args.function funktioniert
    parser.set_defaults(function=None)

    #   Subparser-Objekt erstellen
    subparsers = parser.add_subparsers(title='sub-commands',
                                       description='The exit subcommand is used to terminate the interactiv input mode '
                                                   'by just typing exit.',
                                       dest='subparser_name')

    #   Gruppe aus nicht kompatiblen Parametern: Verbose-Level einstellen oder quite, um Ausgabe auf Ergebnisse zu
    #   beschränken
    verbose_group = parser.add_mutually_exclusive_group()

    # Argumente für den parser
    #   1: positional Argument für die Anzahl der Qubits
    parser.add_argument('-n', '--n_qubits',
                        action='store',
                        type=int,
                        default=Base.getnqubits(),
                        help='Set number of qubits. Initialize new qubits with 0.'
                             'Index of the gates have to be in range of this number.')

    #   2: Argument um Qubits zu initialisieren (Bitmuster wird eingegeben, Benutzerdefinierte Aktion prüft Eingabe und
    #   Speichert Bitmuster als Index: Umwandlung von bool in int)
    parser.add_argument('-i', '--initial_state',
                        dest='index_in_vec',
                        default=0,
                        action=ValidateInitialization,
                        metavar='STATE',
                        help='Initialize qubits with bit pattern like 010011 '
                             '(from left: q_0 to the right: q_n).')

    #   3: Argument um Gatter einzulesen
    parser.add_argument('-g', '--gate',
                        dest='list_of_operations',
                        action=ValidateGate,
                        nargs='+',
                        metavar=('GATE', 'INDEX_1'),
                        help='Gate and indices of the affected qubits. Some Gates needs additional parameters,'
                             ' some gates have a short and a long term notation (fredkin = f = cswap).'
                             ' {x, z, y, h, s, s*, t, t*, r, to, f, u3, i, d}'
                             ' Example: -g r_phi INDEX PARAM')

    #   7: Argument um die Liste der Gatter oder den aktuellen Zustand auszugeben (Wird auch in der Liste der
    #   Operationen gespeichert)
    parser.add_argument('-p', '--print',
                        dest='list_of_operations',
                        choices=['states', 'state_vec', 'init_state', 'gates'],
                        action=ValidatePrint,
                        help='Print the state vector or the list of gates')

    #   4: Argument um Datei einzulesen
    parser.add_argument('-f', '--file',
                        default=[],
                        action=CheckFilePath,
                        metavar='FILEPATH',
                        help='Read simulation parameters from file. One argument per line. '
                             'Example: -v 1 -f '
                             r'C:\Users\Lukas\Documents\test.txt ; '
                             r'test.txt: -n 3\n -i 0011\n -g h 1\n -g m 1')

    # Argumente, die im Elternbefehl vorkommen (In der Syntax vor den Teilbefhelen: -v 2 -c file c:/user...
    #   5: Argument um das Verbose-Level festzulegen
    verbose_group.add_argument('-v', '--verbose_level',
                               dest='verbose_level',
                               type=int,
                               action='store',
                               default=0,
                               help='Increase output verbosity.'
                               )

    #   6: Argument um die Ausgabe auf die Ergebnisse einzuschränken
    verbose_group.add_argument('-q', '--quiet',
                               dest='quiet',
                               action='store_true',
                               help='Print only results.')

    #   8: Argument um nach der Simulation die alten Parameter zu löschen
    parser.add_argument('-c', '--clear',
                        dest='clear_mem',
                        action='store_true',
                        help='Delete the number of qubits, the list of gates, ... in memory. Useful in interactive '
                             'input mode.')

    #   9: Argument um meine erste Eingabe zu vewerwenden
    parser.add_argument('--interactive_input',
                        action='store_true',
                        help='Activates the input of different commands one after the other, which are applied to the '
                             'same state vector. Then -n and -i have no effect.')

    parser.add_argument('-a', '--accuracy',
                        dest='accuracy',
                        metavar='ACCURACY',
                        type=int,
                        default=4,
                        action='store',
                        help='Define the accuracy of the output. Accuracy of the parameters entered have to be some'
                             ' digits higher.')

    #   Teilbefehl, der die interaktive Eingabe deaktiviert
    parser_exit = subparsers.add_parser('exit',
                                        description='Exit from command input loop: --interactive_input.',
                                        help='Deaktivate interactive input from commandline interface')

    #   im Argumlent_Objekt des Parser wird an der Stelle function 'exit_interactiv_in' gespeichert. Damit wird
    #   später der Funktionsaufruf args.function(q_sim, args) zu exit_interactiv_in(q_sim, args), wenn der Teilbefehl
    #   exit aufgerufen wurde.
    parser_exit.set_defaults(function=exit_interactiv_in)

    #   Parsor wird mit dem Eingegebenen Befehl aufgerufen (cmd_input ist bereits über split() in Argumente pro
    #   Zeile aufgeteilt)
    args = parser.parse_args(cmd_in)

    #   Je nach Teilbefehl wird in args.function ein bestimter Text gespeichert, der sich für die Teilbefehle
    #   unterscheidet. Für cli ist funcion = qsim_obj.process_cli, für file, qsim_obj.process_file. Somit werden je nach
    #   verwendetem Teilbefehl, verschiedene Funktionen aufgerufen.
    #   https://docs.python.org/3/library/argparse.html#sub-commands
    if args.function:
        args.function(q_sim, args)

    #   Falls der Index des Initialzustandes im Bereich der Anzahl an Qubits ist, wird der Index als Basiszustand
    #   gespeichert
    if args.index_in_vec < pow(2, args.n_qubits):
        q_sim.index_of_basis_state = args.index_in_vec

    else:
        #   Berechne aus dem Index die Anzahl der Qubits (Ist der Index 0, wird 0 berechnet, die Anzahl der Qubits
        #   beträgt in diesem Fall aber 1)
        n = math.ceil(math.log(args.index_in_vec + 1, 2).real)
        if n == 0:
            n = 1

        #   Ist die Anzahl der Qubits 0, weil sie nicht mit -n festgelegt wurde oder weil im interaktiven Modus 0
        #   gespeichert war, wird die Anzahl an Qubits entsprechend dem Initialzustand angepasst.
        if args.n_qubits == 0:

            args.n_qubits = n
            q_sim.index_of_basis_state = args.index_in_vec

        #   Falls Bereits eine Anzahl an Qubits festgelegt ist, wird eine Fehlermeldung ausgegeben
        else:
            print('IndexError:\nThe number of qubits from the initial state {r!r} does not match to the entered '
                  'number of qubits: {s!r}.'.format(r=n, s=args.n_qubits))
            return

    #   1: Setzte die Anzahl der Qubits
    q_sim.process_n_qubits(args.n_qubits)

    #   Falls Operationen (Gatter oder Befehle wie der print state_vec Befehl) eingegeben wurden, werden diese über
    #   die Funktion process_operation() der Liste aller Operationen hinzugefügt
    if args.list_of_operations:
        for operation in args.list_of_operations:
            #   process_operation() fügt die Operation der Liste aller Operationen hinzu
            q_sim.process_operation(operation)

    #   5   Das Verboselevel, bzw quiet wird verarbeitet (die betreffenden Variablen gesetzt)
    if args.quiet:

        #   Quiet bedeutet Debug-Modus auf -1
        Base.set_verbose_level(-1)
    else:
        Base.set_verbose_level(args.verbose_level)

    #   Lege die Genauigkeit der Ausgegebenen Wahrscheinlichkeit fest
    Base.set_accuracy(args.accuracy)

    #   Die Simulation wird gestartet, falls nicht der exit Befehl aufgerufen wurde
    if not args.function:
        #   Starte die Simulation
        q_sim.start_simulation()

    #   Entferne alle Gatter in der Liste aller Operationen, die ausgeführt werden sollen
    #   (auch wenn mehrere Befehle hintereinander ausgeführt werden und der Arbeitsspeicher mit clear nicht
    #   gelöscht werden soll, ist es sinnvoll, die bereits angenwndeten Gatter zu entfernen, damit sie nicht
    #   doppelt aufgerufen werden. Außerdem kann bei einem neuen Befehl die Anzahl an Qubits verringert werden,
    #   wodurch es zu einem Fehler kommt, wenn alte Gatter mit höheren Index noch in der Liste vorhanden sind.
    q_sim.operation_obj.list_of_operations = []

    #   Die Liste aller Gatter und der Initialzustand wird gelöscht, die Anzahl der Qubits wird auf 0 gesetzt
    #   (Falls -c --clear im eingegebenen Befehl)
    if args.clear_mem:
        QuantumSimulation.clear_mem(q_sim)

    #   9   Sollen mehrere Befehle hintereinander ausgeführt werden, haben die Befehle das Argument --interactive_input.
    #       Wurde dieses Argument übergeben, gibt die Funktion cmd_line_parser() True zurück, ansonsten False
    #       Entsprechend wird diese Funktion in einer Schleife aufgerufen oder nicht.
    if args.interactive_input:
        q_sim.interactive_input = True

    return q_sim.interactive_input


def process_cli(qsim_obj, args):
    """
    Diese Funktion wird vom Parsor aufgerufen, wenn der Teilbefehl cli aufgerufen wurde.
    Sie verarbeitet die Argumente, die mit dem Parser ausgelesen wurden, indem sie kleinere Funktionen
    aufruft.
    :param qsim_obj:
    :param args: Argumente aus dem Parsor des Teilbefehls cli.
    :return:
    """




def process_file(q_sim, args):
    """
    Diese Funktion wird vom Parsor aufgerufen, wenn der Teilbefehl file aufgerufen wurde.
    Nachdem der erste Parsor aus der Datei die Argumente eingelesen hat, wird hier mit cmd_line_parser() der zweite
    Parsor aufgerufen, welcher die Argumente weiter verarbeitet.

    :param args: Argumente aus dem Parsor des Teilbefehls file.
    :return:
    """

    #   Der Parsor wird erneut aufgerufen, diesmal mit den Argumenten, die aus der Datei eingelesen wurden
    try:
        cmd_line_parser(q_sim, args.file)
    except argparse.ArgumentError:
        print('Argument error')
        a = input()


if __name__ == '__main__':

    #   QuantumSimulation Objekt erstellen
    q_sim = QuantumSimulation()

    #   Falls in den Parametern, die mit dem Programmaufruf übergeben wurden nur ein Element ist, ist das der
    #   Programmpfad, der nicht Teil des Befehls ist. Dann wird eine Hilfenachricht ausgegeben.
    #   Wenn mehr Argumente übergeben wurden, werden die Nachfolgenden Elemente für den Parser gespeichert.
    start_arguments = []
    if len(sys.argv) <= 1:
        print('No command entered, type -h to display help.')
    else:
        start_arguments = sys.argv[1:]

        #   Führe Simulation mit übergebenen Start-Parametern aus. Das Parsen, das Verabreiten der Eingabe, die Simulation
        #   und die bereinigung des Arbeitsspeichers erfolgt durch die Funktion q_sim.cmd_line_parser() der Klasse
        #   QuantumSimulation
        #
        #   Der Parser ist extra in der Funktion cmd_line_parser(), da er für eine Eingabe zweilmal aufgerufen
        #   werden soll, wenn Argumente aus einer Datei eingelesen werden sollen. Die Funktion gibt True oder False zurück,
        #   je nachdem, ob im Befehl mit --interactive_input das Ausführen von mehreren Befehlen hintereinander aktiviert
        #   wurde, oder nicht. (self.interactive_input in q_sim)
        loop_for_cli = cmd_line_parser(q_sim, start_arguments)

        #   Gibt der Parser q_sim.cmd_line_parser() True zurück, wird auf eine neue Konsoleneingabe gewartet.
        #   Die Schleife ist solange aktiv, bis ein erneuter aufruf des Parsers in der Schleife False zurück gibt.
        while loop_for_cli:

            #   Speichere die neue Eingabe
            cmd_input = input('QuantumSimulation: ').split()

            if any(cmd_input):
                #   Parse den eingegebenen Befehl, verarbeite die eingegebenen Parameter.
                #   Speichere den zurückgegebenen Wert. split() zerlegt den eingegebenen Befehl in die Einzelnen Argumente
                #   pro Zeile. Es wird nach Leerzeichen getrennt.
                loop_for_cli = cmd_line_parser(q_sim, cmd_input)
