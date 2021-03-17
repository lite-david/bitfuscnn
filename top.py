import utils
from bitfuscnn import CoordinateComputation, MultiplierArray, BufferBankArray, Crossbar
from scipy.ndimage import convolve
import numpy as np

import ppu


def do_cycle(
    bufferbank,
    weights,
    weight_indices,
    activations,
    activation_indices,
    banks=32,
    parallel=4,
    w_dim=3,
    a_dim=13,
    tile_size=32,
    bitwidth=0,
):
    coordinatecompute = CoordinateComputation(
        weight_indices, activation_indices, w_dim, a_dim, parallel, parallel
    )
    multiplierarray = MultiplierArray(weights, activations, parallel, parallel)
    xbar = Crossbar(banks, bufferbank)

    cycle = 0
    stall = 0
    outputcoordinates = coordinatecompute.getCoordinates()
    while len(outputcoordinates) > 0 or stall > 0:
        if stall == 0:
            products = multiplierarray.multiply()
            stall = xbar.route(products, outputcoordinates, tile_size)
        else:
            stall = xbar.route(products, outputcoordinates, tile_size)
        if stall == 0:
            outputcoordinates = coordinatecompute.getCoordinates()
        cycle += 1

    # print('Cycles: ' + str(cycle))
    # print(bufferbank.buffer)
    return cycle


def do_output_channel(weights, activations, parallel=4, banks=32, bitwidth=0):
    bufferbank = BufferBankArray(banks, banks)
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
            banks=banks,
            bitwidth=bitwidth,
        )

    return bufferbank, cycles


def do_ppu_cycle(buffers, buffer_info, bitwidth=0):
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
        bitwidth=bitwidth,
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
            bitwidth=bitwidth,
        )
        neighbor_exchange_done = [ppu_output.exchange_done] * 8

    return oaram, oaram_indices, cycles


def generate_data(width, height, count, p_zero=0.5, relu=False):
    values = []
    for i in range(count):
        value = np.random.rand(width, height) * 256 - 128
        zeros = np.random.rand(width, height) > p_zero
        value = value * zeros
        value = value.astype(int)
        values.append(value)
    return values


def extract_activations_from_oaram(oaram, oaram_indices, size):
    length = oaram[0]
    mat = np.zeros((size, size))
    index = 0
    for value, zeros in zip(oaram[1 : length + 1], oaram_indices[:length]):
        index += zeros
        r = index // size
        c = index % size
        mat[r][c] = value
        index += 1
    return mat


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


def expected_convolve(weights, activations):
    weight = weights[0]
    activation = activations[0]
    conv_so_far = utils.convolve(activation, weight)
    for weight, activation in zip(weights[1:], activations[1:]):
        conv_so_far += utils.convolve(activation, weight)
    return conv_so_far


def do_test(parallel, bitwidth, density):
    BANKS = 256
    KERNEL_SIZE = 3
    # scale = 8
    # density = 0.1
    SIZE = 13
    # parallel = 4
    buffer_info = ppu.BufferAddressInfo(BANKS, tile_size=SIZE + 2)

    # CHANNELS = 192 * 2
    CHANNELS = 1

    bufferbank, cycles_c = do_output_channel(
        generate_data(KERNEL_SIZE, KERNEL_SIZE, CHANNELS, p_zero=density),
        generate_data(SIZE, SIZE, CHANNELS, p_zero=density),
        banks=BANKS,
        parallel=parallel,
        bitwidth=bitwidth,
    )
    # next cycle

    # CHANNELS = 128 * 2
    CHANNELS = 1
    oaram, oaram_indices, cycles_p = do_ppu_cycle(bufferbank, buffer_info)

    weights = generate_data(KERNEL_SIZE, KERNEL_SIZE, CHANNELS, p_zero=density)
    activations = generate_data(SIZE, SIZE, CHANNELS, p_zero=density)

    bufferbank, cycles_c2 = do_output_channel(
        weights, activations, parallel=parallel, bitwidth=bitwidth, banks=BANKS
    )
    # next cycle

    oaram, oaram_indices, cycles_p2 = do_ppu_cycle(
        bufferbank, buffer_info, bitwidth=bitwidth
    )

    max_stage_1 = max(cycles_p, cycles_c2)
    total = cycles_c + max_stage_1 + cycles_p2
    # print(
    #     "p_zero = {}, stage [{},{},{}] = {}, c1={}, c2={}, p1={}, p2={}".format(
    #         density,
    #         cycles_c,
    #         max_stage_1,
    #         cycles_p2,
    #         total,
    #         cycles_c,
    #         cycles_c2,
    #         cycles_p,
    #         cycles_p2,
    #     )
    # )

    mat = extract_activations_from_oaram(oaram, oaram_indices, SIZE)
    ACTIVE_SIZE = 13
    active = mat[:ACTIVE_SIZE, :ACTIVE_SIZE]
    # print(active)

    conv_so_far = expected_convolve(weights, activations)
    conv_so_far = np.maximum(0, conv_so_far)
    # print(conv_so_far)
    delta = active - conv_so_far

    def print_mat(mat):
        for i in range(ACTIVE_SIZE):
            string = ""
            for k in range(ACTIVE_SIZE):
                string += "{}\t".format(mat[i][k])
            print(string)

    max_delta = np.max(np.abs(delta))
    if not max_delta == 0:
        print(weights[0])
        print(activations[0])
        print("active:")
        print_mat(active)
        print("conv_so_far:")
        print_mat(conv_so_far)

        print("delta:")
        print_mat(delta)
        print(max_delta)
        return False, total
    return True, total, cycles_c + cycles_c2, cycles_p + cycles_p2


BITWIDTH = 0
PARALLEL = 16
SPARSITY = 0.3
cycle_counts = []
cycle_conv = []
cycle_ppu = []
for i in range(100):
    passed, cycles, conv, ppu_cycles = do_test(PARALLEL, BITWIDTH, SPARSITY)
    cycle_counts.append(cycles)
    cycle_conv.append(conv)
    cycle_ppu.append(ppu_cycles)
    if not passed:
        break

cycle_counts = np.array(cycle_counts)
std_dev = np.std(cycle_counts)
mean = np.mean(cycle_counts)

mean_conv = np.mean(cycle_conv)
mean_ppu = np.mean(cycle_ppu)

print(
    "For bitwidth {} running {} || multiplies at sparsity {} give {} cycles with stdev {}".format(
        BITWIDTH, PARALLEL, SPARSITY, mean, std_dev
    )
)
print("{} cycles in conv, {} cycles in ppu".format(mean_conv, mean_ppu))


# cweights, weightindices = utils.compress(weights)
# cactivations, activationindices = utils.compress(activations)

# do_cycle(bufferbank, cweights, weightindices[1:], cactivations, activationindices[1:])
# next_conv = utils.convolveMultiple(activations, [weights])
# for i in range(3):
#     for k in range(3):
#         conv_so_far[i][k] += next_conv[i][k]

# print(generate_data(SIZE, SIZE, 1, p_zero=density))
# print(oaram)
# print(oaram_indices)
# mat = extract_activations_from_oaram(oaram, oaram_indices, 30)
# active = mat[:13, :13]
# print(active)
# for i in range(13):
#     string = ""
#     for k in range(13):
#         string += "{}\t".format(active[i][k]//10)
#     print(string)
# print(cycles)
# print(conv_so_far)
