# OmegaID

[![PyPI version](https://badge.fury.io/py/omegaid.svg)](https://badge.fury.io/py/omegaid)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

ΩID is a Python package for calculating the integrated information decomposition (ΦID) of time series data. It is designed for high-performance computing, with optional GPU acceleration via CuPy.

## Installation

Currently, OmegaID is not available on PyPI. You can install it from source by following these steps:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-repo/omegaid.git
   cd omegaid
   ```

2. **Create and activate a virtual environment (recommended with `uv`)**:

   ```bash
   uv venv
   uv shell
   ```

3. **Install dependencies and the package**:

   ### With GPU support

   To install OmegaID with GPU support, you need to have a CUDA-enabled GPU and the CUDA toolkit installed. Then, install the package with the `gpu` extra:

   ```bash
   uv pip install ".[gpu]"
   ```

   ### CPU-only

   If you don't have a GPU or don't want to use it, you can install the CPU-only version:

   ```bash
   uv pip install .
   ```

## Usage

OmegaID provides multiple functions for ΦID calculation, tailored for different use cases.

### Bivariate Systems (2x2)

For standard 2x2 systems (e.g., two sources influencing two targets), the legacy implementation offers the highest performance.

```python
import numpy as np
from omegaid.core.phiid import calc_phiid_ccs, calc_phiid_mmi

# Generate some random data for a 2x2 system
src = np.random.randn(1000)
trg = np.random.randn(1000)

# Calculate PhiID using the high-performance CCS method (GPU-accelerated)
atoms_res_ccs, _ = calc_phiid_ccs(src, trg, tau=1)
print("CCS Results (Bivariate):", atoms_res_ccs)

# For theoretical comparison, use the MMI method (CPU-only)
atoms_res_mmi, _ = calc_phiid_mmi(src, trg, tau=1)
print("MMI Results (Bivariate):", atoms_res_mmi)
```

### Multivariate Systems (NxM)

For generalized systems with N sources and M targets, use the `multivariate` functions.

```python
import numpy as np
from omegaid.core.phiid import calc_phiid_multivariate_ccs, calc_phiid_multivariate_mmi

# Generate data for a 3-source, 3-target system
n_samples = 1000
sources = np.random.randn(n_samples, 3)
targets = np.random.randn(n_samples, 3)

# Calculate PhiID using the generalized CCS method
# Note: The core logic is JIT-compiled with Numba for CPU performance.
# The `xp` backend is used for entropy calculations, allowing GPU use there.
atoms_res_multi_ccs, _ = calc_phiid_multivariate_ccs(sources, targets, tau=1)
print("CCS Results (Multivariate):", atoms_res_multi_ccs)

# The MMI version is also available (CPU-only)
atoms_res_multi_mmi, _ = calc_phiid_multivariate_mmi(sources, targets, tau=1)
print("MMI Results (Multivariate):", atoms_res_multi_mmi)
```

## Benchmarks

The performance of OmegaID has been benchmarked across different scenarios.

### Bivariate Implementation (`calc_phiid_*`)

This implementation is highly optimized for 2x2 systems. It shows excellent GPU speedup with `calc_phiid_ccs` for computations involving a large number of features (dimensions).

### Generalized Multivariate Implementation (`calc_phiid_multivariate_*`)

This implementation handles arbitrary N-source, M-target systems. The core logic for lattice building and Mobius inversion is JIT-compiled with Numba for high CPU performance. The MI calculation has been ported to a CUDA kernel to eliminate GPU-CPU data transfer overhead.

### Performance Summary

| Test Case                 | Samples | Backend | Total Time (s) | Entropy (s) | Lattice Gen (s) | Mobius Inv (s) | Perf Ratio |
| :------------------------ | :------ | :------ | :------------- | :---------- | :-------------- | :------------- | :--------- |
| **Bivariate (256 Dims)**  | 50,000  | numpy   | 0.133          | -           | -               | -              | -          |
|                           |         | cupy    | **0.030**      | -           | -               | -              | **4.48x**  |
| **Bivariate (1024 Dims)** | 50,000  | numpy   | 0.113          | -           | -               | -              | -          |
|                           |         | cupy    | **0.023**      | -           | -               | -              | **4.99x**  |
| **Multivariate (1x1)**    | 1,000   | numpy   | 3.418          | 0.357       | 2.797           | 0.263          | -          |
|                           |         | cupy    | **1.414**      | 0.221       | 0.632           | 0.306          | **2.42x**  |
| **Multivariate (2x2)**    | 1,000   | numpy   | **0.846**      | 0.070       | 0.629           | 0.146          | -          |
|                           |         | cupy    | 1.118          | 0.193       | 0.634           | 0.147          | 0.76x      |
| **Multivariate (3x3)**    | 1,000   | numpy   | **3.689**      | 1.283       | 2.203           | 0.187          | -          |
|                           |         | cupy    | 5.550          | 3.112       | 2.125           | 0.162          | 0.66x      |
| **Stress Test (3x3)**     | 10,000  | numpy   | **9.602**      | 7.143       | 2.181           | 0.187          | -          |

*Note: Detailed timings for the Bivariate case are not shown as its internal structure is different.*

### Conclusion

1.  **Bivariate Case**: For systems with many features (high dimensionality) but a simple 2x2 source-target structure, the `calc_phiid_ccs` function provides significant **multi-fold speedups** on the GPU.
2.  **Multivariate Case**: For systems with more variables (e.g., 3x3), the computational complexity grows exponentially.
    -   Our optimizations, including CUDA kernels for MI calculation, have successfully removed data transfer bottlenecks.
    -   The current performance limitation is the **algorithmic complexity** of the entropy calculation (`2^n` subsets) and the CPU-bound lattice generation.
    -   As a result, for N > 1, the highly-optimized NumPy backend currently outperforms the CuPy backend.
3.  **Future Work**: Further significant performance gains in the multivariate case will require **algorithmic innovations** to reduce the complexity of the core entropy calculation, rather than further code-level micro-optimizations.
