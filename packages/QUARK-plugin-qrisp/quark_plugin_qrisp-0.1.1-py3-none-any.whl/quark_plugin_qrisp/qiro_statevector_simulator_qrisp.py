import logging
from dataclasses import dataclass
from typing import override

from qrisp import QuantumVariable
from qrisp.algorithms.qiro import QIROProblem
from quark.core import Core, Data, Result
from quark.interface_types import Other


@dataclass
class QiroStatevectorSimulatorQrisp(Core):
    qiro_reps: int = 3
    depth: int = 5
    shots: int = 1000
    iterations: int = 20

    @override
    def preprocess(self, data: Other) -> Result:
        qiro_instance: QIROProblem = data.data[0]
        qarg = QuantumVariable(data.data[1])

        try:
            res_qiro = qiro_instance.run_qiro(
                qarg=qarg,
                depth=self.depth,
                n_recursions=self.qiro_reps,
                mes_kwargs={"shots": self.shots},
                max_iter=self.iterations,
            )
        except ValueError as e:
            logging.error(f"The following ValueError occurred in module QrispQIRO: {e}")
            logging.error("The benchmarking run terminates with exception.")
            raise Exception("Please refer to the logged error message.") from e

        self._result = res_qiro
        return Data(None)

    @override
    def postprocess(self, data: None) -> Result:
        return Data(Other(self._result))
