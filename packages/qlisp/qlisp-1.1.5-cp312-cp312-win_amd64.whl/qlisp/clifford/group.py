from functools import reduce
from itertools import islice, product
from typing import Sequence

import numpy as np
from cycles import CliffordGroup as _CliffordGroup
from cycles import (Cycles, OneQubitCliffordGateType, TwoQubitCliffordGateType,
                    find_permutation)

from ..matricies import sigmaI, sigmaX, sigmaY, sigmaZ
from ..simple import seq2mat
from .utils import (one_qubit_clifford_index, one_qubit_clifford_mul_table,
                    one_qubit_clifford_seq)


def find_permutation_for_Unitary(U: np.ndarray,
                                 N: int | None = None) -> Cycles:
    init = []
    final = []

    if N is None:
        N = round(np.log2(U.shape[0]))

    assert U.ndim == 2 and U.shape == (2**N, 2**N)

    for s in islice(
            product([sigmaI(), sigmaX(),
                     sigmaY(), sigmaZ()], repeat=N), 1, None):
        op = reduce(np.kron, s)
        init.append(op)
        final.append(U @ op @ U.T.conj())
        init.append(-op)
        final.append(U @ (-op) @ U.T.conj())
    return find_permutation(init, final)


class CliffordGroup(_CliffordGroup):

    def __init__(self,
                 N: int,
                 one_qubit_gates: Sequence[OneQubitCliffordGateType] = ('H',
                                                                        'S'),
                 two_qubit_gate: TwoQubitCliffordGateType = 'CZ',
                 graph: tuple[int, int] | None = None,
                 generators: dict[tuple, Cycles] | None = None):
        super().__init__(N, one_qubit_gates, two_qubit_gate, graph, generators)
        for i in range(self.N):
            for g in one_qubit_clifford_seq:
                self.circuit_to_permutation([(g, i)])

    def matrix_to_circuit(self, mat):
        perm = self.matrix_to_permutation(mat)
        return [self.reversed_map[c] for c in perm.expand()]

    def matrix_to_permutation(self, mat) -> Cycles:
        assert mat.shape == (
            2**self.N, 2**self.N
        ), f"mat.shape = {mat.shape} != (2**{self.N}, 2**{self.N})"
        perm = find_permutation_for_Unitary(mat, self.N)
        perm = self.express(perm)
        return perm

    def circuit_to_permutation(self, circuit) -> Cycles:
        perm = Cycles()
        for gate in circuit:
            if gate not in self.gate_map:
                try:
                    self.gate_map[gate] = super().circuit_to_permutation(
                        [gate])
                except:
                    _, *qubits = gate
                    circ = [('I', i) for i in range(self.N) if i not in qubits]
                    circ.append(gate)
                    mat = seq2mat(circ)
                    self.gate_map[gate] = self.matrix_to_permutation(mat)
                    self.gate_map_inv[self.gate_map[gate]] = gate
            perm = perm * self.gate_map[gate]
        return self.express(perm)

    def permutation_to_matrix(self, perm: Cycles):
        return seq2mat(self.permutation_to_circuit(perm))

    def circuit_simplify(self, circuit):
        ret = []
        stack = {}
        for gate, *qubits in circuit:
            if len(qubits) > 1:
                for qubit in qubits:
                    ret.append((stack.pop(qubit,
                                          one_qubit_clifford_seq[0]), qubit))
                ret.append((gate, *qubits))
            else:
                qubit, = qubits
                i = one_qubit_clifford_index(
                    stack.get(qubit, one_qubit_clifford_seq[0]))
                j = one_qubit_clifford_index(gate)
                stack[qubit] = one_qubit_clifford_seq[
                    one_qubit_clifford_mul_table[i, j]]
        for qubit, gate in stack.items():
            ret.append((gate, qubit))
        return ret

    def circuit_fullsimplify(self, circuit):
        perm = self.circuit_to_permutation(circuit)
        return self.circuit_simplify(self.permutation_to_circuit(perm))
