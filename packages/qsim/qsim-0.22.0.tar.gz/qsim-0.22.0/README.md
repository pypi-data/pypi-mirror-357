# &nbsp; qsim and qsimh <img height="40em" align="left" alt="qsim logo" src="https://quantumai.google/static/site-assets/images/icons/icon_qsim_2880.png">

The libraries qsim and qsimh are high-performance [quantum
circuit](https://en.wikipedia.org/wiki/Quantum_circuit) simulators written in
C++ and offering a Python API wrapper. _qsim_ is a Schrödinger full
state-vector simulator, and _qsimh_ is a hybrid Schrödinger-Feynman simulator.
They use gate fusion, AVX/FMA vectorized instructions, and multi-threading
using OpenMP to achieve state of the art simulations of quantum circuits. Both
can be easily used from [Cirq](https://github.com/quantumlib/cirq), a framework
for writing, manipulating, and running Noisy Intermediate-Scale Quantum (NISQ)
circuits.

qsim and qsimh together are available as the Python package
[qsimcirq](https://pypi.org/project/qsimcirq). The project whose page on PyPI
you are reading now (i.e., [qsim](https://pypi.org/project/qsim)) only acts to
reference [qsimcirq](https://pypi.org/project/qsimcirq) and point people to the
that project.
