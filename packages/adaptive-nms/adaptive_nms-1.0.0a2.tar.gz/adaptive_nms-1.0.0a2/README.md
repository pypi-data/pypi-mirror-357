# Efficient Adaptive Non-Maximal Suppression (ANMS)

This project provides a Cython implementation of the Efficient Adaptive Non-Maximal Suppression (ANMS) algorithms, designed to achieve a homogeneous spatial distribution of keypoints. This implementation is based on the paper "Efficient adaptive non-maximal suppression algorithms for homogeneous spatial keypoint distribution" and offers improved packaging and installation via pip.

## Installation

You can install the `adaptivenms` package directly using pip:

```shell
pip install adaptivenms
```

If you have cloned the repository, you can also install it from the project directory:

```shell
pip install .
```

## Example

The following example demonstrates how to use the `square_covering_adaptive_nms` function to select a target number of keypoints with a homogeneous distribution.

```python
import numpy as np
from adaptivenms import square_covering_adaptive_nms

# Randomly generate sample keypoint data
n_kpts = 10000
width, height = 960, 720
kpts_x = np.random.randint(width, size=(n_kpts,))
kpts_y = np.random.randint(height, size=(n_kpts,))
kpts = np.stack([kpts_x, kpts_y], axis=-1)
responses = np.random.random(n_kpts)

# Apply square_covering_adaptive_nms
kpts_idxs = square_covering_adaptive_nms(
    kpts,  # 2-dimensional array of shape [N, 2] representing keypoint coordinates (x, y)
    responses,  # 1-dimensional array of shape [N,] representing keypoint responses (e.g., cornerness scores)
    width=width,  # Width of the image
    height=height,  # Height of the image
    target_num_kpts=2048,  # Desired number of keypoints to retain
    indices_only=True,  # If True, returns only the indices of selected keypoints; otherwise, returns the selected keypoints themselves
    up_tol=10,  # Tolerance for allowing slightly more selected keypoints than target_num_kpts
    max_num_iter=30,  # Maximum number of binary search iterations to find the optimal suppression radius
)

print(f"Original number of keypoints: {n_kpts}")
print(f"Number of selected keypoints: {len(kpts_idxs)}")
```

## References

* **Paper:** [Efficient adaptive non-maximal suppression algorithms for homogeneous spatial keypoint distribution](https://www.researchgate.net/publication/323388062_Efficient_adaptive_non-maximal_suppression_algorithms_for_homogeneous_spatial_keypoint_distribution)
* **Original C++ Implementation:** [GitHub - BAILOOL/ANMS-Codes](https://github.com/BAILOOL/ANMS-Codes)
* **Original Cython Implementation (Forked from):** [GitHub - viniavskyi-ostap/adaptive-nms](https://github.com/viniavskyi-ostap/adaptive-nms)