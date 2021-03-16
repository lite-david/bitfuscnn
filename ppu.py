#!/usr/bin/python3
# Apply activations
# Receive partial sums from neighbors
# Do weight compression / access IARAM and IARAM indices
# Sends partial sums to buffer bank for final accumulation
# Sends remote partial sums to remote for final accumulation
import math
import copy
from enum import Enum

class Neighbor(Enum):
    TOP_LEFT = 0
    TOP = 1
    TOP_RIGHT = 2
    LEFT = 3
    RIGHT = 4
    BOTTOM_LEFT = 5
    BOTTOM = 6
    BOTTOM_RIGHT = 7
    NONE = 8

class PPUStates(Enum):
    IDLE = 0
    BROADCAST = 1


class PPUState:
    def __init__(self, buffer_info):
        self.done = True
        self.neighbor_inputs = [(0, -1, -1)] * buffer_info.buffer_count
        self.process_outputs = False
        self.row_counter = 0
        self.column_counter = 0


class BufferAddressInfo:
    def __init__(self, buffer_count, tile_size=4):
        self.buffer_count = buffer_count
        self.tile_size = tile_size


def bank_from_rcc(row, column, channel, buffer_address_info, bitwidth=0):
    row_upper = row >> bitwidth
    row_section = row % (1 << bitwidth)
    small_buffcount = buffer_address_info.buffer_count >> bitwidth
    shift = row_upper * 3
    shift = shift % buffer_address_info.buffer_count
    index = (column + shift + row_section * small_buffcount) % buffer_address_info.buffer_count
    return int(index)


def entry_from_rcc(row, column, channel, buffer_address_info, bitwidth=0):
    return row >> bitwidth


def bank_entry_to_rcc(bank, entry, buffer_address_info, bitwidth=0):
    small_buffcount = buffer_address_info.buffer_count >> bitwidth
    row = entry
    row_msb = row << bitwidth
    shift = row * 3
    shift = shift % buffer_address_info.buffer_count
    column = bank-shift
    if bank < shift:
        column = bank + buffer_address_info.buffer_count - shift
    col_div = int(math.log2(buffer_address_info.buffer_count))
    row_lsb = column >> (col_div - bitwidth)
    column = column % small_buffcount
    row = row_msb | row_lsb
    
    return (row, column, 0)  # zero channel for now


def has_leftover_inputs(state):
    for partial in state.neighbor_inputs:
        if partial[2] >= 0:
            return True
    return False

def process_neighbor_inputs(state, neighbor_inputs, buffer_address_info):
    if not has_leftover_inputs(state):
        state.neighbor_inputs = copy.copy(neighbor_inputs)
    buffer_outputs = [(0, -1, -1, -1)] * buffer_address_info.buffer_count
    used_banks = [False] * buffer_address_info.buffer_count
    for i in range(len(state.neighbor_inputs)):
        partial = state.neighbor_inputs[i]
        if(partial[1] < 0):
            continue
        bank = bank_from_rcc(
            partial[1],
            partial[2],
            partial[3],
            buffer_address_info
        )
        if used_banks[bank]:
            continue
        used_banks[bank] = True
        buffer_outputs[bank] = partial
        state.neighbor_inputs[i] = (0, -1, -1, -1)

    return buffer_outputs

def neighbor_from_rcc(rcc, buffer_address_info, kernel_size=3):
    tile_size = buffer_address_info.tile_size
    halo_size = (kernel_size - 1) / 2
    row = rcc[0]
    column = rcc[1]

    max_center = tile_size - halo_size

    if row < halo_size and column < halo_size:
        return Neighbor.TOP_LEFT
    if row >= max_center and column >= max_center:
        return Neighbor.BOTTOM_RIGHT
    if row < halo_size and column >= max_center:
        return Neighbor.TOP_RIGHT
    if row >= max_center and column < halo_size:
        return Neighbor.BOTTOM_LEFT

    if row < halo_size:
        return Neighbor.TOP
    if column < halo_size:
        return Neighbor.LEFT

    if row >= max_center:
        return Neighbor.BOTTOM
    if column >= max_center:
        return Neighbor.RIGHT

    return Neighbor.NONE

def get_neighbor_rcc(rcc, neighbor, buffer_address_info, kernel_size=3):
    halo_size = (kernel_size-1)/2
    row_top = buffer_address_info.tile_size - rcc[0] - 2 * halo_size
    row_bottom = rcc[0] - buffer_address_info.tile_size + 2 * halo_size
    column_left = buffer_address_info.tile_size - rcc[1] - 2 * halo_size
    column_right = rcc[1] - buffer_address_info.tile_size + 2 * halo_size

    if neighbor == Neighbor.TOP_LEFT:
        row = row_top
        column = column_left
        return (row, column, rcc[2])

    if neighbor == Neighbor.TOP:
        row = row_top
        column = rcc[1]
        return (row, column, rcc[2])

    if neighbor == Neighbor.TOP_RIGHT:
        row = row_top
        column = column_right
        return (row, column, rcc[2])

    if neighbor == Neighbor.LEFT:
        row = rcc[0]
        column = column_left
        return (row, column, rcc[2])

    if neighbor == Neighbor.RIGHT:
        row = rcc[0]
        column = column_right
        return (row, column, rcc[2])

    if neighbor == Neighbor.BOTTOM_LEFT:
        row = row_bottom
        column = column_left
        return (row, column, rcc[2])

    if neighbor == Neighbor.BOTTOM:
        row = row_bottom
        column = rcc[1]
        return (row, column, rcc[2])

    if neighbor == Neighbor.BOTTOM_RIGHT:
        row = row_bottom
        column = column_right
        return (row, column, rcc[2])

    return rcc

def increment_row_column(state, buffer_address_info):
    state.row_counter += 1
    if state.row_counter >= buffer_address_info.tile_size:
        state.row_counter = 0
        state.column_counter += 1

def output_partials(state, channel_group_done, neighbor_cts, buffers, buffer_address_info, kernel_size=3):
    neighbor_outputs = [(0, -1, -1, -1)] * 8

    if not state.process_outputs and channel_group_done:
        state.row_counter = 0
        state.column_counter = 0
        state.process_outputs = True

    if not state.process_outputs:
        return neighbor_outputs

    rcc = (state.row_counter, state.column_counter, 0)
    bank = bank_from_rcc(rcc[0], rcc[1], 0, buffer_address_info)
    entry = entry_from_rcc(rcc[0], rcc[1], 0, buffer_address_info)
    selected_output = buffers[bank][entry]

    if selected_output == 0:
        increment_row_column(state, buffer_address_info)
        return neighbor_outputs
        
    neighbor = neighbor_from_rcc(rcc, buffer_address_info, kernel_size=kernel_size)
    if not neighbor_cts[neighbor.value]:
        return neighbor_outputs

    increment_row_column(state, buffer_address_info)
    if neighbor == Neighbor.NONE:
        return neighbor_outputs

    rcc = get_neighbor_rcc(rcc, neighbor, buffer_address_info, kernel_size=kernel_size)
    neighbor_outputs[neighbor.value] = (selected_output, rcc[0], rcc[1], rcc[2])

    return neighbor_outputs


def increment_column_row(state, buffer_address_info):
    if state.row_counter >= buffer_address_info.tile_size:
        return

    state.column_counter += 1
    if state.column_counter >= buffer_address_info.tile_size:
        state.column_counter = 0
        state.row_counter += 1


def relu(value):
    if value < 0:
        return 0
    return value


def save_value_sparse(state, oaram, oaram_indices, value, max_zero=16):
    if value == 0 and state.zero_counter < max_zero:
        state.zero_counter += 1
        return

    state.length += 1
    oaram[state.length] = value
    oaram_indices[state.length-1] = state.zero_counter
    state.zero_counter = 0


def output_accumulator(
    state,
    oaram,
    oaram_indices,
    buffers,
    neighbor_exchange_done,
    buffer_address_info,
    kernel_size=3,
    max_zero=15,
):
    all_done = True
    for value in neighbor_exchange_done:
        if not value:
            all_done = False

    if not all_done:
        return False

    if state.row_counter >= buffer_address_info.tile_size:
        oaram[0] = state.length
        return True

    rcc = (state.row_counter, state.column_counter, 0)
    neighbor = neighbor_from_rcc(rcc, buffer_address_info, kernel_size=kernel_size)

    bank = bank_from_rcc(
        state.row_counter, state.column_counter, 0, buffer_address_info
    )
    entry = entry_from_rcc(
        state.row_counter, state.column_counter, 0, buffer_address_info
    )
    value = buffers[bank][entry]

    value = relu(value)

    if neighbor == Neighbor.NONE:
        save_value_sparse(state, oaram, oaram_indices, value, max_zero=max_zero)

    increment_column_row(state, buffer_address_info)

    return False

    return neighbor_outputs

"""
This method applies one clock cycle for the PPU

:param state: the current state of the PPU
:param channel_group_done: true when the chanel group has been processed
:param oaram: array of the output activation values
:param oaram_indices: array of the output activation indices
:param buffers: back buffers of the accumulators 
:param neighbor_inputs: array of eight weight tuples (value, x, y) 
:param neighbor_cts: array of eight cts signals from neighbors
:param kernel_size: size of the kernel width and height, used to determin output halo
:param buffer_address_info: info about the accumulator buffers
:returns: (done, buffer_outputs, neighbor_outputs, clear_to_send) 
          buffer_outputs are a list of tuples with locations of where to
          place each iin the accumulator buffers
          clear to send is an array of cts's for each neighbor
"""


def ppu(
    state,
    channel_group_done,
    oaram,
    oaram_indices,
    buffers,
    neighbor_inputs,
    neighbor_cts,
    kernel_size=3,
    buffer_address_info=BufferAddressInfo(32)
):
    buffer_outputs = process_neighbor_inputs(state, neighbor_inputs, buffer_address_info)

    return (not has_leftover_inputs(state), buffer_outputs, False, not has_leftover_inputs(state))
