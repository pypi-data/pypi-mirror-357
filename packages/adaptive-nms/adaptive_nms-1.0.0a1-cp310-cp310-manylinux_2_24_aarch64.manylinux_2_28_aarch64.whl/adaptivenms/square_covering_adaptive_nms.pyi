import numpy as np
from typing import Tuple, Union

def square_covering_adaptive_nms(keypoints: np.ndarray, responses: np.ndarray,
                                   width: int, height: int, target_num_kpts: int, indices_only: bool = False,
                                   up_tol: int = 10, max_num_iter: int = 30) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]: ...