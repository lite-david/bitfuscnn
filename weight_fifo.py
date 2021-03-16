#!/usr/bin/python3
# Loops through all nonzero weights
# Advances by four
# Zero fill weights once done

#     If we have 9 weights the last 3 need to be zero filled to 12 total weights (Div by four)


class WeightFIFO:
    def __init__(self):
        self.current_weight = 0
        self.on_last_cycle = False


"""
This method applies one clock cycle for the weight FIFO

:param state: the current state of the weight FIFO
:param advance: true if we should advance this clock cycle
:param weight_memory: array of the possible weights to choose, (values, indices)
:param output_width: width of the output list, zero padded
:returns: tuple of indices and values of the weights of length output_width
"""


def weight_fifo(state, advance, weight_memory, output_width=4):
    weights_left = len(weight_memory[0]) - state.current_weight
    weights_to_take = min(output_width, weights_left)
    weights_not_taken = output_width - weights_to_take
    end_index = state.current_weight + weights_to_take

    fill_weights = [0] * weights_not_taken
    fill_indices = [-1] * weights_not_taken
    weight_indices = weight_memory[1][state.current_weight : end_index] + fill_indices
    weight_values = weight_memory[0][state.current_weight : end_index] + fill_weights

    if weights_left <= output_width:
        state.on_last_cycle = True
    if advance:
        state.current_weight += output_width
    return (weight_indices, weight_values)
