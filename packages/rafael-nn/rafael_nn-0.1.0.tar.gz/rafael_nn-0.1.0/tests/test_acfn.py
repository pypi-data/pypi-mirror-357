import unittest
import numpy as np
from rafael_nn.acfn import ReLU

class TestReLU(unittest.TestCase):

    def test_forward_positive(self):
        relu = ReLU()
        x = np.array([1, -1, 0, 5])
        output = relu.forward(x)
        expected = np.array([1, 0, 0, 5])
        np.testing.assert_array_equal(output, expected)

    def test_backward(self):
        relu = ReLU()
        x = np.array([1.0, -2.0, 0.0])
        grad = relu.backward(x)
        expected = np.array([1.0, 0.0, 0.0])
        np.testing.assert_array_equal(grad, expected)

if __name__ == '__main__':
    unittest.main()

