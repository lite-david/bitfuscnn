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

class PPUStates(Enum):
    IDLE = 0
    BROADCAST = 1


class PPUState:
    def __init__(self, buffer_info):
        self.done = True
        self.neighbor_inputs = [(0, -1, -1)] * buffer_info.buffer_count


class BufferAddressInfo:
    def __init__(self, buffer_count):
        self.buffer_count = buffer_count


def bank_from_rcc(row, column, channel, buffer_address_info):
    shift = row * 3 + channel
    shift = shift % buffer_address_info.buffer_count
    index = (column+shift) % buffer_address_info.buffer_count
    return int(index)

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

def output_partials(state, channel_group_done, neighbor_cts, buffers, buffer_address_info, kernel_size=3):
    neighbor_outputs = [(0, -1, -1, -1)] * 8
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
