import unittest
from weight_fifo import weight_fifo, WeightFIFO

class WeightFIFOTest(unittest.TestCase):
    def test_no_weights_outputs_zero(self):
        state = WeightFIFO()
        indices, weights = weight_fifo(state, False, [[], []], 4)
        expected_indices = [-1] * 4
        expected_weights = [0] * 4
        self.assertEqual(
            indices, expected_indices, "Four indices with negative one index"
        )
        self.assertEqual(weights, expected_weights, "Four weights with value zero")
        self.assertTrue(state.on_last_cycle)

    def test_one_weights_outputs_only_that_one(self):
        state = WeightFIFO()
        indices, weights = weight_fifo(state, False, [[1], [0]], 4)
        expected_indices = [0] + [-1] * 3
        expected_weights = [1] + [0] * 3
        self.assertEqual(indices, expected_indices)
        self.assertEqual(weights, expected_weights)
        self.assertTrue(state.on_last_cycle)

    def test_fives_weights_output_four(self):
        state = WeightFIFO()
        indices, weights = weight_fifo(
            state, False, [[1, 2, 3, 4, 5], [0, 1, 2, 0, 1]], 4
        )
        expected_indices = [0, 1, 2, 0]
        expected_weights = [1, 2, 3, 4]
        self.assertEqual(indices, expected_indices)
        self.assertEqual(weights, expected_weights)
        self.assertFalse(state.on_last_cycle)

    def test_four_weights_output_weights_and_set_last_cycle(self):
        state = WeightFIFO()
        indices, weights = weight_fifo(
            state, False, [[1, 2, 3, 4], [0, 1, 2, 0]], 4
        )
        expected_indices = [0, 1, 2, 0]
        expected_weights = [1, 2, 3, 4]
        self.assertEqual(indices, expected_indices)
        self.assertEqual(weights, expected_weights)
        self.assertTrue(state.on_last_cycle)

    def test_fives_second_cycle_same_if_not_advance(self):
        state = WeightFIFO()
        indices, weights = weight_fifo(
            state, False, [[1, 2, 3, 4, 5], [0, 1, 2, 0, 1]], 4
        )
        indices, weights = weight_fifo(
            state, False, [[1, 2, 3, 4, 5], [0, 1, 2, 0, 1]], 4
        )
        expected_indices = [0, 1, 2, 0]
        expected_weights = [1, 2, 3, 4]
        self.assertEqual(indices, expected_indices)
        self.assertEqual(weights, expected_weights)
        self.assertFalse(state.on_last_cycle)

    def test_fives_second_cycle_next_if_advance(self):
        state = WeightFIFO()
        indices, weights = weight_fifo(
            state, True, [[1, 2, 3, 4, 5], [0, 1, 2, 0, 5]], 4
        )
        indices, weights = weight_fifo(
            state, False, [[1, 2, 3, 4, 5], [0, 1, 2, 0, 5]], 4
        )
        expected_indices = [5] + [-1] * 3
        expected_weights = [5] + [0] * 3
        self.assertEqual(indices, expected_indices)
        self.assertEqual(weights, expected_weights)
        self.assertTrue(state.on_last_cycle)


if __name__ == "__main__":
    unittest.main()