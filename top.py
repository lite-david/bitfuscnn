import utils
from bitfuscnn import CoordinateComputation, MultiplierArray, BufferBankArray, Crossbar
from scipy.ndimage import convolve
import numpy as np

import ppu


def do_cycle(
    bufferbank, weights, weight_indices, activations, activation_indices, parallel=4
):
    coordinatecompute = CoordinateComputation(
        weight_indices, activation_indices, 3, 3, parallel, parallel
    )
    multiplierarray = MultiplierArray(weights, activations, parallel, parallel)
    xbar = Crossbar(32, bufferbank)

    cycle = 0
    stall = 0
    outputcoordinates = coordinatecompute.getCoordinates()
    while len(outputcoordinates) > 0 or stall > 0:
        if stall == 0:
            products = multiplierarray.multiply()
            stall = xbar.route(products, outputcoordinates, 3)
        else:
            stall = xbar.route(products, outputcoordinates, 3)
        if stall == 0:
            outputcoordinates = coordinatecompute.getCoordinates()
        cycle += 1

    # print('Cycles: ' + str(cycle))
    # print(bufferbank.buffer)
    return cycle


def do_output_channel(weights, activations, parallel=4):
    bufferbank = BufferBankArray(32, 32)
    cycles = 0
    for weight, activation in zip(weights, activations):
        cweights, weightindices = utils.compress(weight)
        cactivations, activationindices = utils.compress(activation)

        cycles += do_cycle(
            bufferbank,
            cweights,
            weightindices[1:],
            cactivations,
            activationindices[1:],
            parallel=parallel,
        )

    return bufferbank, cycles


def do_ppu_cycle(buffers, buffer_info):
    state = ppu.PPUState(buffer_info)
    RAM_SIZE = 1024
    neighbor_cts = [True] * 8
    neighbor_exchange_done = [False] * 8
    neighbor_input = [(0, -1, -1, -1)] * 8
    oaram = [0] * RAM_SIZE
    oaram_indices = [0] * RAM_SIZE
    cycles = 1
    buffers = buffers.buffer
    ppu_output = ppu.ppu(
        state,
        True,
        oaram,
        oaram_indices,
        buffers,
        neighbor_input,
        neighbor_exchange_done,
        neighbor_cts,
        buffer_address_info=buffer_info,
    )
    while not ppu_output.cycle_done:
        cycles += 1
        ppu_output = ppu.ppu(
            state,
            False,
            oaram,
            oaram_indices,
            buffers,
            neighbor_input,
            neighbor_exchange_done,
            neighbor_cts,
            buffer_address_info=buffer_info,
        )
        neighbor_exchange_done = [ppu_output.exchange_done] * 8

    return cycles


def generate_data(width, height, count, p_zero=0.5, relu=False):
    values = []
    for i in range(count):
        value = np.random.rand(width, height) * 256 - 128
        zeros = np.random.rand(width, height) > p_zero
        value = value * zeros
        value = value.astype(int)
        values.append(value)
    return values


# weights = []
# activations = []
# weights.append([
#     [1, 0, 1],
#     [0, 0, 0],
#     [1, 0, 1],
# ])

# activations.append([
#     [1, 2, 3],
#     [4, 5, 6],
#     [7, 8, 9],
# ])


# weights.append([
#     [0, 1, 0],
#     [1, 0, 1],
#     [0, 1, 0],
# ])

# activations.append([
#     [9, 8, 7],
#     [4, 5, 6],
#     [3, 2, 1],
# ])

density = 0.1
SIZE = 13
parallel = 4
buffer_info = ppu.BufferAddressInfo(32, tile_size=32)

CHANNELS = 192

bufferbank, cycles_c = do_output_channel(
    generate_data(SIZE, SIZE, CHANNELS, p_zero=density),
    generate_data(SIZE, SIZE, CHANNELS, p_zero=density),
    parallel=parallel
)
# next cycle

CHANNELS = 128
cycles_p = do_ppu_cycle(bufferbank, buffer_info)

bufferbank, cycles_c2 = do_output_channel(
    generate_data(SIZE, SIZE, CHANNELS, p_zero=density),
    generate_data(SIZE, SIZE, CHANNELS, p_zero=density),
    parallel=parallel
)
# next cycle

cycles_p2 = do_ppu_cycle(bufferbank, buffer_info)

max_stage_1 = max(cycles_p, cycles_c2)
total = cycles_c + max_stage_1 + cycles_p2
print(
    "p_zero = {}, stage [{},{},{}] = {}, c1={}, c2={}, p1={}, p2={}".format(
        density,
        cycles_c,
        max_stage_1,
        cycles_p2,
        total,
        cycles_c,
        cycles_c2,
        cycles_p,
        cycles_p2,
    )
)


# cweights, weightindices = utils.compress(weights)
# cactivations, activationindices = utils.compress(activations)

# do_cycle(bufferbank, cweights, weightindices[1:], cactivations, activationindices[1:])
# next_conv = utils.convolveMultiple(activations, [weights])
# for i in range(3):
#     for k in range(3):
#         conv_so_far[i][k] += next_conv[i][k]

print(bufferbank.buffer)
# print(cycles)
# print(conv_so_far)
