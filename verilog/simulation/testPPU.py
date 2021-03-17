import cocotb
from cocotb.triggers import Timer
from cocotb.clock import Clock
import unittest
from enum import Enum

LONGTEST=False


class PPUOutput:
    def __init__(tc):
        pass


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


# @cocotb.test()
# def testPPU_1(dut):
#     clk = dut.ppu.clk
#     clk <= 0
#     yield Timer(100, units="ns")
#     clk <= 1
#     yield Timer(100, units="ns")


@cocotb.coroutine
def reset_dut(ppu):
    ppu.reset_n <= 0
    yield Timer(100, units="ns")
    ppu.reset_n <= 1
    yield Timer(100, units="ns")


@cocotb.coroutine
def set_bit(wire, i, val):
    old_val = wire.value
    not_mask = 1 << i
    mask = not_mask ^ 0xFFFFFF
    masked_val = mask & old_val
    new_val = (val << i) | masked_val
    wire <= new_val
    # print(i, val)
    # print("{},{},{},{},{}".format(bin(old_val), bin(new_val), bin(mask), bin(masked_val), bin(val << i)))
    yield Timer(1)


def get_bit(wire, i):
    not_mask = 1 << i
    mask = not_mask ^ 0xFFFFFF
    if wire.value & mask != 0:
        return 1
    return 0


@cocotb.coroutine
def set_neighbor_data(ppu, neighbor_input, neighbor_cts, neighbor_exchange_done):
    for i in range(len(neighbor_input)):
        ppu.neighbor_input_value[i] <= neighbor_input[i][0]
        ppu.neighbor_input_row[i] <= neighbor_input[i][1]
        ppu.neighbor_input_column[i] <= neighbor_input[i][2]

        ppu.neighbor_cts[i] <= neighbor_cts[i]
        # yield set_bit(ppu.neighbor_cts, i, neighbor_cts[i])
        ppu.neighbor_exchange_done[i] <= neighbor_exchange_done[i]
        # yield set_bit(ppu.neighbor_exchange_done, i, neighbor_exchange_done[i])
        we_value = 1
        if neighbor_input[i][1] == -1:
            we_value = 0
        ppu.neighbor_input_write_enable[i] <= we_value
        # yield set_bit(ppu.neighbor_input_write_enable, i, we_value)
    yield Timer(1)


# @cocotb.coroutine
def parley_oaram(ppu, oaram, oaram_indices):
    if ppu.oaram_write_enable.value:
        address = ppu.oaram_address.value.integer
        oaram[address] = ppu.oaram_value.value.integer
        if address > 0:
            oaram_indices[address - 1] = ppu.oaram_indices_value.value
    # yield Timer(1)


def get_ppu_output(ppu, bank_count):
    ppu_output = PPUOutput()
    ppu_output.cycle_done = ppu.cycle_done.value
    ppu_output.clear_to_send = False
    if ppu.clear_to_send.value == 1:
        ppu_output.clear_to_send = True
    ppu_output.exchange_done = ppu.exchange_done.value
    ppu_output.buffer_outputs = []

    for i in range(bank_count):
        if ppu.buffer_write_enable[i] == 0:
            new_value = (0, -1, -1, -1)
            ppu_output.buffer_outputs.append(new_value)
            continue
        value = ppu.buffer_data_write[i].value
        row = ppu.buffer_row_write[i].value
        column = ppu.buffer_column_write[i].value
        new_value = (value, row, column, 0)
        ppu_output.buffer_outputs.append(new_value)

    ppu_output.neighbor_outputs = []
    for i in range(8):
        val = ppu.neighbor_output_value[i].value.integer
        row = ppu.neighbor_output_row[i].value.integer
        column = ppu.neighbor_output_column[i].value.integer
        write_enable = ppu.neighbor_output_write_enable[i]
        if write_enable == 0:
            new_value = (0, -1, -1, -1)
            ppu_output.neighbor_outputs.append(new_value)
            continue
        new_value = (val, row, column, 0)
        ppu_output.neighbor_outputs.append(new_value)

    return ppu_output


def defined(value):
    string = value._str
    if "x" in string or "z" in string:
        return False
    return True


def bank_from_rcc(row, column, channel, buffer_address_info, bitwidth=0):
    row_upper = row >> bitwidth
    row_section = row % (1 << bitwidth)
    small_buffcount = buffer_address_info.buffer_count >> bitwidth
    shift = row_upper * 3
    shift = shift % buffer_address_info.buffer_count
    index = (
        column + shift + row_section * small_buffcount
    ) % buffer_address_info.buffer_count
    return int(index)


def entry_from_rcc(row, column, channel, buffer_address_info, bitwidth=0):
    return row >> bitwidth


@cocotb.coroutine
def parley_buffer_bank(ppu, buffer):
    # yield Timer(1)
    read_addr = ppu.buffer_bank_read.value
    assert defined(read_addr), "invalid bank {}".format(read_addr)
    entry = ppu.buffer_bank_entry.value
    assert defined(entry), "invalid entry {}".format(entry)
    if read_addr.integer < len(buffer) and entry.integer < len(buffer[0]):
        value = buffer[read_addr][entry]
        ppu.buffer_data_read <= value
        yield Timer(1)

    # if value != 0:
    #     print("nonzero value", value, read_addr.integer, entry.integer)
    # yield Timer(1)


@cocotb.coroutine
def do_ppu(
    ppu,
    channel_group_done,
    oaram,
    oaram_indices,
    buffers,
    neighbor_inputs,
    neighbor_exchange_done,
    neighbor_cts,
    bitwidth=2,
    kernel_size=3,
):
    ppu.clk <= 0
    ppu.channel_group_done <= channel_group_done
    ppu.bitwidth <= bitwidth
    ppu.kernel_size <= kernel_size
    yield Timer(1)
    yield parley_buffer_bank(ppu, buffers)
    yield Timer(1)
    yield set_neighbor_data(ppu, neighbor_inputs, neighbor_cts, neighbor_exchange_done)
    yield parley_buffer_bank(ppu, buffers)
    ppu.clk <= 1
    yield Timer(1)
    yield parley_buffer_bank(ppu, buffers)
    parley_oaram(ppu, oaram, oaram_indices)
    yield Timer(1)
    ppu_output = get_ppu_output(ppu, 256)
    ppu.clk <= 0
    yield Timer(1)
    return ppu_output


@cocotb.coroutine
def output_accumulator(
    ppu,
    oaram,
    oaram_indices,
    buffers,
    neighbor_exchange_done,
    bitwidth=2,
    kernel_size=3,
    max_zero=-1,
):
    channel_group_done = False
    neighbor_cts = [True] * 8

    ppu.clk <= 0
    ppu.channel_group_done <= channel_group_done
    ppu.bitwidth <= bitwidth
    ppu.kernel_size <= kernel_size
    # yield Timer(1)
    neighbor_inputs = [(0, -1, -1, -1)] * 8
    # yield set_neighbor_data(ppu, neighbor_inputs, neighbor_cts, neighbor_exchange_done)
    for i in range(len(neighbor_inputs)):
        ppu.neighbor_exchange_done[i] <= neighbor_exchange_done[i]
    # yield Timer(1)
    yield parley_buffer_bank(ppu, buffers)
    ppu.clk <= 1
    yield Timer(1)

    parley_oaram(ppu, oaram, oaram_indices)
    yield parley_buffer_bank(ppu, buffers)
    ppu_output = get_ppu_output(ppu, 32)
    ppu.clk <= 0
    yield Timer(1)
    return ppu_output.cycle_done


class BufferAddressInfo:
    def __init__(tc, buffer_count, tile_size=4):
        tc.buffer_count = buffer_count
        tc.tile_size = tile_size


@cocotb.test()
def test_ppu_done_on_first_cycle(dut):
    tc = unittest.TestCase()
    ppu = dut.ppu
    yield reset_dut(ppu)
    RAM_SIZE = 1024
    BUFFER_COUNT = 256
    BUFFER_WIDTH = 32

    oaram = [0] * RAM_SIZE
    oaram_indices = [0] * RAM_SIZE
    back_buffers = [[0] * BUFFER_WIDTH] * BUFFER_COUNT
    neighbor_input = [(0, -1, -1, -1)] * 8
    neighbor_cts = [False] * 8
    neighbor_exchange_done = [False] * 8
    parley_oaram(ppu, oaram, oaram_indices)
    ppu_output = yield do_ppu(
        ppu,
        False,
        oaram,
        oaram_indices,
        back_buffers,
        neighbor_input,
        neighbor_exchange_done,
        neighbor_cts,
    )

    tc.assertTrue(ppu_output.clear_to_send)


@cocotb.test()
def test_ppu_saves_incoming_partial_sum(dut):
    tc = unittest.TestCase()
    ppu = dut.ppu
    yield reset_dut(ppu)

    RAM_SIZE = 1024
    BUFFER_COUNT = 256
    BUFFER_WIDTH = 32
    buffer_info = BufferAddressInfo(BUFFER_COUNT)

    oaram = [0] * RAM_SIZE
    oaram_indices = [0] * RAM_SIZE
    back_buffers = [[0] * BUFFER_WIDTH] * BUFFER_COUNT
    neighbor_input = [(3, 1, 1, 0)] + [(0, -1, -1, -1)] * 7
    neighbor_cts = [False] * 8
    neighbor_exchange_done = [False] * 8
    ppu_outputs = yield do_ppu(
        ppu,
        False,
        oaram,
        oaram_indices,
        back_buffers,
        neighbor_input,
        neighbor_exchange_done,
        neighbor_cts,
    )

    expected_buffer_outputs = [(0, -1, -1, -1)] * BUFFER_COUNT
    expected_buffer_outputs[bank_from_rcc(1, 1, 0, buffer_info, bitwidth=2)] = (
        3,
        1,
        1,
        0,
    )
    tc.assertEqual(ppu_outputs.buffer_outputs, expected_buffer_outputs)


@cocotb.test()
def test_has_leftover_inputs(dut):
    tc = unittest.TestCase()
    ppu = dut.ppu
    neighbor_input_processor = ppu.neighbor_input_processor
    RAM_SIZE = 1024
    BUFFER_COUNT = 256
    BUFFER_WIDTH = 32
    neighbor_input_processor.clk <= 0

    yield reset_dut(neighbor_input_processor)

    yield set_bit(neighbor_input_processor.proc_neighbor_input_write_enable, 0, 1)
    neighbor_input_processor.proc_neighbor_input_value[0] <= 2
    neighbor_input_processor.proc_neighbor_input_row[0] <= 1
    neighbor_input_processor.proc_neighbor_input_column[0] <= 1

    yield Timer(1)
    tc.assertTrue(neighbor_input_processor.leftover_inputs.value)

    neighbor_input_processor.clk <= 1
    yield Timer(1)

    tc.assertFalse(neighbor_input_processor.leftover_inputs.value)


@cocotb.test()
def test_ppu_saves_sets_cts_false_when_conflicting_bank(dut):
    tc = unittest.TestCase()
    ppu = dut.ppu
    RAM_SIZE = 1024
    BUFFER_COUNT = 256
    BUFFER_WIDTH = 32
    buffer_info = BufferAddressInfo(BUFFER_COUNT)
    yield reset_dut(ppu)

    oaram = [0] * RAM_SIZE
    oaram_indices = [0] * RAM_SIZE
    back_buffers = [[0] * BUFFER_WIDTH] * BUFFER_COUNT
    neighbor_input = [(3, 1, 1, 0), (1, 1, 1, 0)] + [(0, -1, -1, -1)] * 6
    neighbor_cts = [False] * 8
    neighbor_exchange_done = [False] * 8
    ppu_output = yield do_ppu(
        ppu,
        False,
        oaram,
        oaram_indices,
        back_buffers,
        neighbor_input,
        neighbor_exchange_done,
        neighbor_cts,
    )
    tc.assertFalse(ppu_output.cycle_done)
    tc.assertFalse(ppu_output.clear_to_send)

    expected_buffer_outputs = [(0, -1, -1, -1)] * BUFFER_COUNT
    expected_buffer_outputs[bank_from_rcc(1, 1, 1, buffer_info, bitwidth=2)] = (
        3,
        1,
        1,
        0,
    )
    tc.assertEqual(ppu_output.buffer_outputs, expected_buffer_outputs)

    ppu_output = yield do_ppu(
        ppu,
        False,
        oaram,
        oaram_indices,
        back_buffers,
        neighbor_input,
        neighbor_exchange_done,
        neighbor_cts,
    )

    tc.assertTrue(ppu_output.clear_to_send)

    expected_buffer_outputs = [(0, -1, -1, -1)] * BUFFER_COUNT
    expected_buffer_outputs[bank_from_rcc(1, 1, 1, buffer_info, bitwidth=2)] = (
        1,
        1,
        1,
        0,
    )
    tc.assertEqual(ppu_output.buffer_outputs, expected_buffer_outputs)


@cocotb.coroutine
def output_partials(
    ppu, channel_group_done, neighbor_cts, buffers, ram_size, bitwidth=2, kernel_size=3
):
    ppu.clk <= 0
    ppu.channel_group_done <= channel_group_done
    ppu.bitwidth <= bitwidth
    ppu.kernel_size <= kernel_size
    yield Timer(1)
    neighbor_inputs = [(0, -1, -1, -1)] * 8
    neighbor_exchange_done = [False] * 8
    yield set_neighbor_data(ppu, neighbor_inputs, neighbor_cts, neighbor_exchange_done)
    yield parley_buffer_bank(ppu, buffers)
    ppu.clk <= 1
    yield Timer(1)

    oaram = [0] * ram_size
    oaram_indices = [0] * ram_size
    parley_oaram(ppu, oaram, oaram_indices)
    yield parley_buffer_bank(ppu, buffers)
    ppu_output = get_ppu_output(ppu, 32)
    ppu.clk <= 0
    yield Timer(1)
    return ppu_output.neighbor_outputs


@cocotb.test()
def test_no_partials_in_reset_state(dut):
    tc = unittest.TestCase()
    ppu = dut.ppu
    yield reset_dut(ppu)
    RAM_SIZE = 1024
    BUFFER_COUNT = 256
    BUFFER_WIDTH = 32
    buffer_info = BufferAddressInfo(BUFFER_COUNT)

    channel_group_done = False
    neighbor_cts = [True] * 8
    buffers = [[0] * BUFFER_WIDTH] * BUFFER_COUNT
    neighbor_outputs = yield output_partials(
        ppu, channel_group_done, neighbor_cts, buffers, RAM_SIZE
    )

    expected_neighbor_outputs = [(0, -1, -1, -1)] * 8
    tc.assertEqual(neighbor_outputs, expected_neighbor_outputs)


@cocotb.test()
def test_all_zero_partials_after_reset_yields_no_outputs(dut):
    tc = unittest.TestCase()
    ppu = dut.ppu
    yield reset_dut(ppu)
    RAM_SIZE = 1024
    BUFFER_COUNT = 256
    BUFFER_WIDTH = 32
    # buffer_info = BufferAddressInfo(BUFFER_COUNT)

    #
    channel_group_done = True
    neighbor_cts = [True] * 8
    buffers = [[0] * BUFFER_WIDTH] * BUFFER_COUNT

    neighbor_outputs = yield output_partials(
        ppu, channel_group_done, neighbor_cts, buffers, RAM_SIZE
    )

    expected_neighbor_outputs = [(0, -1, -1, -1)] * 8
    tc.assertEqual(neighbor_outputs, expected_neighbor_outputs)


@cocotb.test()
def test_non_zero_partial_after_reset_yields_one_output(dut):
    tc = unittest.TestCase()
    ppu = dut.ppu
    yield reset_dut(ppu)
    RAM_SIZE = 1024
    BUFFER_COUNT = 256
    BUFFER_WIDTH = 32
    # buffer_info = BufferAddressInfo(BUFFER_COUNT, tile_size=32)

    #
    channel_group_done = True
    neighbor_cts = [True] * 8
    buffers = [[0] * BUFFER_WIDTH] * BUFFER_COUNT
    buffers[0][0] = 5  # 0,0 is outside for kernel size > 1
    neighbor_outputs = yield output_partials(
        ppu, channel_group_done, neighbor_cts, buffers, RAM_SIZE
    )

    expected_neighbor_outputs = [(0, -1, -1, -1)] * 8
    expected_neighbor_outputs[Neighbor.TOP_LEFT.value] = (
        5,
        30,
        30,
        0,
    )  # remove padding bottom right corner
    tc.assertEqual(neighbor_outputs, expected_neighbor_outputs)


@cocotb.test()
def test_non_zero_partials_after_reset_output_in_order(dut):
    tc = unittest.TestCase()
    ppu = dut.ppu
    yield reset_dut(ppu)
    RAM_SIZE = 1024
    BUFFER_COUNT = 256
    BUFFER_WIDTH = 32
    buffer_info = BufferAddressInfo(BUFFER_COUNT, tile_size=32)

    #
    channel_group_done = True
    neighbor_cts = [True] * 8
    buffers = []
    for i in range(BUFFER_COUNT):
        buffers.append([0] * BUFFER_WIDTH)
    buffers[0][0] = 5  # 0,0 is outside for kernel size > 1

    bank = bank_from_rcc(0, 1, 0, buffer_info)
    entry = entry_from_rcc(0, 1, 0, buffer_info)

    buffers[bank][entry] = 10
    neighbor_outputs = yield output_partials(
        ppu, channel_group_done, neighbor_cts, buffers, RAM_SIZE
    )

    expected_neighbor_outputs = [(0, -1, -1, -1)] * 8
    expected_neighbor_outputs[Neighbor.TOP_LEFT.value] = (
        5,
        30,
        30,
        0,
    )  # remove padding bottom right corner
    tc.assertEqual(neighbor_outputs, expected_neighbor_outputs)

    counter = 0
    while True:
        counter += 1
        tc.assertFalse(
            counter > RAM_SIZE, "Exceeded runtime at {} cycles".format(counter)
        )
        channel_group_done = False
        neighbor_outputs = yield output_partials(
            ppu, channel_group_done, neighbor_cts, buffers, RAM_SIZE
        )
        expected_neighbor_outputs = [(0, -1, -1, -1)] * 8
        if neighbor_outputs[Neighbor.TOP.value] == (10, 30, 1, 0):
            expected_neighbor_outputs[Neighbor.TOP.value] = (10, 30, 1, 0)
            tc.assertEqual(neighbor_outputs, expected_neighbor_outputs)
            break
        tc.assertEqual(neighbor_outputs, expected_neighbor_outputs)


@cocotb.test()
def test_not_cts_stalls_ppu(dut):
    tc = unittest.TestCase()
    ppu = dut.ppu
    yield reset_dut(ppu)
    RAM_SIZE = 1024
    BUFFER_COUNT = 256
    BUFFER_WIDTH = 32
    buffer_info = BufferAddressInfo(BUFFER_COUNT, tile_size=32)

    #
    channel_group_done = True
    neighbor_cts = [True] * 8
    neighbor_cts[Neighbor.TOP_LEFT.value] = False
    buffers = [[0] * BUFFER_WIDTH] * BUFFER_COUNT
    buffers[0][0] = 5  # 0,0 is outside for kernel size > 1
    neighbor_outputs = yield output_partials(
        ppu, channel_group_done, neighbor_cts, buffers, RAM_SIZE
    )

    expected_neighbor_outputs = [(0, -1, -1, -1)] * 8
    tc.assertEqual(neighbor_outputs, expected_neighbor_outputs)

    neighbor_cts = [True] * 8

    neighbor_outputs = yield output_partials(
        ppu, channel_group_done, neighbor_cts, buffers, RAM_SIZE
    )

    expected_neighbor_outputs = [(0, -1, -1, -1)] * 8
    expected_neighbor_outputs[Neighbor.TOP_LEFT.value] = (5, 30, 30, 0)
    tc.assertEqual(neighbor_outputs, expected_neighbor_outputs)


@cocotb.test()
def test_after_at_most_ram_size_cycles_transmit_done(dut):
    global LONGTEST
    if not LONGTEST:
        return
    tc = unittest.TestCase()
    ppu = dut.ppu
    yield reset_dut(ppu)
    RAM_SIZE = 1024
    BUFFER_COUNT = 256
    BUFFER_WIDTH = 32
    buffer_info = BufferAddressInfo(BUFFER_COUNT, tile_size=32)

    #
    oaram = [0] * RAM_SIZE
    oaram_indices = [0] * RAM_SIZE
    neighbor_input = [(0, -1, -1, -1)] * 8
    channel_group_done = True
    neighbor_cts = [True] * 8
    neighbor_exchange_done = [False] * 8
    buffers = [[0] * BUFFER_WIDTH] * BUFFER_COUNT
    buffers[0][0] = 5  # 0,0 is outside for kernel size > 1

    ppu_output = None
    for i in range(RAM_SIZE):
        ppu_output = yield do_ppu(
            ppu,
            channel_group_done,
            oaram,
            oaram_indices,
            buffers,
            neighbor_input,
            neighbor_exchange_done,
            neighbor_cts,
        )

    tc.assertTrue(ppu_output.exchange_done)


@cocotb.test()
def test_exchange_not_done_after_one_cycle(dut):
    global LONGTEST
    if not LONGTEST:
        return
    tc = unittest.TestCase()
    ppu = dut.ppu
    yield reset_dut(ppu)
    RAM_SIZE = 1024
    BUFFER_COUNT = 256
    BUFFER_WIDTH = 32
    buffer_info = BufferAddressInfo(BUFFER_COUNT, tile_size=32)

    # state = PPUState(buffer_info)
    oaram = [0] * RAM_SIZE
    oaram_indices = [0] * RAM_SIZE
    neighbor_input = [(0, -1, -1, -1)] * 8
    channel_group_done = True
    neighbor_cts = [True] * 8
    neighbor_exchange_done = [False] * 8
    buffers = []
    for i in range(BUFFER_COUNT):
        buffers.append([0] * BUFFER_WIDTH)

    bank = bank_from_rcc(0, 1, 0, buffer_info)
    entry = entry_from_rcc(0, 1, 0, buffer_info)
    buffers[bank][entry] = 10

    bank = bank_from_rcc(0, 2, 0, buffer_info)
    entry = entry_from_rcc(0, 2, 0, buffer_info)
    buffers[bank][entry] = 10

    ppu_output = yield do_ppu(
        ppu,
        channel_group_done,
        oaram,
        oaram_indices,
        buffers,
        neighbor_input,
        neighbor_exchange_done,
        neighbor_cts,
    )

    tc.assertFalse(ppu_output.exchange_done)

    for i in range(RAM_SIZE):
        ppu_output = yield do_ppu(
            ppu,
            channel_group_done,
            oaram,
            oaram_indices,
            buffers,
            neighbor_input,
            neighbor_exchange_done,
            neighbor_cts,
        )

    tc.assertTrue(ppu_output.exchange_done)


@cocotb.test()
def test_accumulator_buffers_stored_sparsely(dut):
    global LONGTEST
    if not LONGTEST:
        return
    tc = unittest.TestCase()
    ppu = dut.ppu
    yield reset_dut(ppu)
    RAM_SIZE = 1024
    BUFFER_COUNT = 256
    BUFFER_WIDTH = 32
    buffer_info = BufferAddressInfo(BUFFER_COUNT, tile_size=32)
    oaram = [0] * RAM_SIZE
    oaram_indices = [0] * RAM_SIZE
    neighbor_exchange_done = [True] * 8

    buffers = []
    for i in range(BUFFER_COUNT):
        buffers.append([0] * BUFFER_WIDTH)

    bank = bank_from_rcc(1, 1, 0, buffer_info, bitwidth=2)
    entry = entry_from_rcc(1, 1, 0, buffer_info, bitwidth=2)
    buffers[bank][entry] = 10

    bank = bank_from_rcc(1, 2, 0, buffer_info, bitwidth=2)
    entry = entry_from_rcc(1, 2, 0, buffer_info, bitwidth=2)
    buffers[bank][entry] = 15

    done = yield output_accumulator(
        ppu,
        oaram,
        oaram_indices,
        buffers,
        neighbor_exchange_done,
        max_zero=15,
    )

    tc.assertFalse(done)

    for i in range(RAM_SIZE - 1):
        done = yield output_accumulator(
            ppu,
            oaram,
            oaram_indices,
            buffers,
            neighbor_exchange_done,
            max_zero=15,
        )

    done = yield output_accumulator(
        ppu,
        oaram,
        oaram_indices,
        buffers,
        neighbor_exchange_done,
        max_zero=15,
    )

    tc.assertTrue(done)

    tc.assertEqual(oaram[0], 58)
    tc.assertEqual(oaram[1], 10)
    tc.assertEqual(oaram[2], 15)

    tc.assertEqual(oaram_indices[0], 0)
    tc.assertEqual(oaram_indices[1], 0)


@cocotb.test()
def test_accumulator_buffers_wait_for_exchange_done(dut):
    global LONGTEST
    if not LONGTEST:
        return
    tc = unittest.TestCase()
    ppu = dut.ppu
    yield reset_dut(ppu)
    RAM_SIZE = 1024
    BUFFER_COUNT = 256
    BUFFER_WIDTH = 32
    buffer_info = BufferAddressInfo(BUFFER_COUNT, tile_size=32)
    oaram = [0] * RAM_SIZE
    oaram_indices = [0] * RAM_SIZE
    neighbor_exchange_done = [False] * 8

    buffers = []
    for i in range(BUFFER_COUNT):
        buffers.append([0] * BUFFER_WIDTH)

    bank = bank_from_rcc(1, 1, 0, buffer_info)
    entry = entry_from_rcc(1, 1, 0, buffer_info)
    buffers[bank][entry] = 10

    done = yield output_accumulator(
        ppu,
        oaram,
        oaram_indices,
        buffers,
        neighbor_exchange_done,
        max_zero=15,
    )

    tc.assertFalse(done)

    for i in range(RAM_SIZE - 1):
        done = yield output_accumulator(
            ppu,
            oaram,
            oaram_indices,
            buffers,
            neighbor_exchange_done,
            max_zero=15,
        )

    done = yield output_accumulator(
        ppu,
        oaram,
        oaram_indices,
        buffers,
        neighbor_exchange_done,
        max_zero=15,
    )

    tc.assertFalse(done)


@cocotb.test()
def test_accumulator_buffers_relu_applied(dut):
    global LONGTEST
    if not LONGTEST:
        return
    tc = unittest.TestCase()
    ppu = dut.ppu
    yield reset_dut(ppu)
    RAM_SIZE = 1024
    BUFFER_COUNT = 256
    BUFFER_WIDTH = 32
    buffer_info = BufferAddressInfo(BUFFER_COUNT, tile_size=32)
    oaram = [0] * RAM_SIZE
    oaram_indices = [0] * RAM_SIZE
    neighbor_exchange_done = [True] * 8

    buffers = []
    for i in range(BUFFER_COUNT):
        buffers.append([0] * BUFFER_WIDTH)

    bank = bank_from_rcc(1, 1, 0, buffer_info, bitwidth=2)
    entry = entry_from_rcc(1, 1, 0, buffer_info, bitwidth=2)
    buffers[bank][entry] = -10

    bank = bank_from_rcc(1, 2, 0, buffer_info, bitwidth=2)
    entry = entry_from_rcc(1, 2, 0, buffer_info, bitwidth=2)
    buffers[bank][entry] = 15

    done = yield output_accumulator(
        ppu,
        oaram,
        oaram_indices,
        buffers,
        neighbor_exchange_done,
        max_zero=15,
    )

    tc.assertFalse(done)

    for i in range(RAM_SIZE - 1):
        done = yield output_accumulator(
            ppu,
            oaram,
            oaram_indices,
            buffers,
            neighbor_exchange_done,
            max_zero=15,
        )

    done = yield output_accumulator(
        ppu,
        oaram,
        oaram_indices,
        buffers,
        neighbor_exchange_done,
        max_zero=15,
    )

    tc.assertTrue(done)

    tc.assertEqual(oaram[0], 57)
    tc.assertEqual(oaram[1], 15)

    tc.assertEqual(oaram_indices[0], 1)


@cocotb.test()
def test_max_zero_count_respected(dut):
    tc = unittest.TestCase()
    ppu = dut.ppu
    yield reset_dut(ppu)
    RAM_SIZE = 2048
    BUFFER_COUNT = 256
    BUFFER_WIDTH = 64
    buffer_info = BufferAddressInfo(BUFFER_COUNT, tile_size=128)
    oaram = [0] * RAM_SIZE
    oaram_indices = [0] * RAM_SIZE
    neighbor_exchange_done = [True] * 8

    buffers = []
    for i in range(BUFFER_COUNT):
        buffers.append([0] * BUFFER_WIDTH)

    bank = bank_from_rcc(1, 1, 0, buffer_info, bitwidth=1)
    entry = entry_from_rcc(1, 1, 0, buffer_info, bitwidth=1)
    buffers[bank][entry] = -1

    bank = bank_from_rcc(1, 2, 0, buffer_info, bitwidth=1)
    entry = entry_from_rcc(1, 2, 0, buffer_info, bitwidth=1)
    buffers[bank][entry] = 6

    bank = bank_from_rcc(1, 19, 0, buffer_info, bitwidth=1)
    entry = entry_from_rcc(1, 19, 0, buffer_info, bitwidth=1)
    buffers[bank][entry] = 2

    done = yield output_accumulator(
        ppu,
        oaram,
        oaram_indices,
        buffers,
        neighbor_exchange_done,
        max_zero=15,
        bitwidth=1,
    )

    tc.assertFalse(done)

    for i in range(128 * 2 - 1):
        done = yield output_accumulator(
            ppu,
            oaram,
            oaram_indices,
            buffers,
            neighbor_exchange_done,
            max_zero=15,
            bitwidth=1,
        )

    done = yield output_accumulator(
        ppu,
        oaram,
        oaram_indices,
        buffers,
        neighbor_exchange_done,
        max_zero=15,
        bitwidth=1,
    )

    tc.assertEqual(oaram[1], 6)
    tc.assertEqual(oaram[2], 0)
    tc.assertEqual(oaram[3], 2)

    tc.assertEqual(oaram_indices[0], 1)
    tc.assertEqual(oaram_indices[1], 15)
    tc.assertEqual(oaram_indices[2], 0)


@cocotb.test()
def test_smaller_bitwidth_works(dut):
    global LONGTEST
    if not LONGTEST:
        return
    tc = unittest.TestCase()
    ppu = dut.ppu
    yield reset_dut(ppu)
    RAM_SIZE = 2048
    BUFFER_COUNT = 256
    BUFFER_WIDTH = 64
    buffer_info = BufferAddressInfo(BUFFER_COUNT, tile_size=128)
    oaram = [0] * RAM_SIZE
    oaram_indices = [0] * RAM_SIZE
    neighbor_exchange_done = [True] * 8

    buffers = []
    for i in range(BUFFER_COUNT):
        buffers.append([0] * BUFFER_WIDTH)

    bank = bank_from_rcc(1, 1, 0, buffer_info, bitwidth=1)
    entry = entry_from_rcc(1, 1, 0, buffer_info, bitwidth=1)
    buffers[bank][entry] = -1

    bank = bank_from_rcc(1, 2, 0, buffer_info, bitwidth=1)
    entry = entry_from_rcc(1, 2, 0, buffer_info, bitwidth=1)
    buffers[bank][entry] = 6

    bank = bank_from_rcc(1, 19, 0, buffer_info, bitwidth=1)
    entry = entry_from_rcc(1, 19, 0, buffer_info, bitwidth=1)
    buffers[bank][entry] = 2

    done = yield output_accumulator(
        ppu,
        oaram,
        oaram_indices,
        buffers,
        neighbor_exchange_done,
        max_zero=15,
        bitwidth=1,
    )

    tc.assertFalse(done)

    for i in range(128 ** 2 - 1):
        done = yield output_accumulator(
            ppu,
            oaram,
            oaram_indices,
            buffers,
            neighbor_exchange_done,
            max_zero=15,
            bitwidth=1,
        )

    done = yield output_accumulator(
        ppu,
        oaram,
        oaram_indices,
        buffers,
        neighbor_exchange_done,
        max_zero=15,
        bitwidth=1,
    )

    tc.assertTrue(done)

    tc.assertEqual(oaram[0], 994)
    tc.assertEqual(oaram[1], 6)
    tc.assertEqual(oaram[2], 0)
    tc.assertEqual(oaram[3], 2)

    tc.assertEqual(oaram_indices[0], 1)
    tc.assertEqual(oaram_indices[1], 15)
    tc.assertEqual(oaram_indices[2], 0)


@cocotb.test()
def test_all_zero_outputs(dut):
    global LONGTEST
    if not LONGTEST:
        return
    tc = unittest.TestCase()
    ppu = dut.ppu
    yield reset_dut(ppu)
    RAM_SIZE = 1024
    BUFFER_COUNT = 256
    BUFFER_WIDTH = 32
    buffer_info = BufferAddressInfo(BUFFER_COUNT, tile_size=32)
    oaram = [0] * RAM_SIZE
    oaram_indices = [0] * RAM_SIZE
    neighbor_exchange_done = [True] * 8

    buffers = []
    for i in range(BUFFER_COUNT):
        buffers.append([0] * BUFFER_WIDTH)

    done = yield output_accumulator(
        ppu,
        oaram,
        oaram_indices,
        buffers,
        neighbor_exchange_done,
        max_zero=3,
    )

    tc.assertFalse(done)

    for i in range(RAM_SIZE - 1):
        done = yield output_accumulator(
            ppu,
            oaram,
            oaram_indices,
            buffers,
            neighbor_exchange_done,
            max_zero=15,
        )

    done = yield output_accumulator(
        ppu,
        oaram,
        oaram_indices,
        buffers,
        neighbor_exchange_done,
        max_zero=15,
    )

    tc.assertTrue(done)

    tc.assertEqual(oaram[0], 56)
    tc.assertEqual(oaram[1], 0)
    tc.assertEqual(oaram[2], 0)
    tc.assertEqual(oaram[3], 0)

    tc.assertEqual(oaram_indices[0], 15)
    tc.assertEqual(oaram_indices[1], 15)
    tc.assertEqual(oaram_indices[2], 15)


def update_buffer(buffers, buffer_outputs, buffer_info):
    for i in range(len(buffer_outputs)):
        elem = buffer_outputs[i]
        if elem[1] == -1:
            continue
        entry = entry_from_rcc(elem[1], elem[2], elem[3], buffer_info, bitwidth=2)
        buffers[i][entry] += elem[0]
        print(
            "Writing r={},c={}, bank={},entry={}, inc={}, new_val={}".format(
                elem[1], elem[2], i, entry, elem[0], buffers[i][entry]
            )
        )


@cocotb.test()
def test_full_unit(dut):
    global LONGTEST
    if not LONGTEST:
        return
    tc = unittest.TestCase()
    ppu = dut.ppu
    yield reset_dut(ppu)
    RAM_SIZE = 1024
    BUFFER_COUNT = 256
    BUFFER_WIDTH = 32
    buffer_info = BufferAddressInfo(BUFFER_COUNT, tile_size=32)

    oaram = [0] * RAM_SIZE
    oaram_indices = [0] * RAM_SIZE
    neighbor_input = [(0, -1, -1, -1)] * 8
    channel_group_done = True
    neighbor_cts = [True] * 8
    neighbor_exchange_done = [False] * 8
    buffers = []
    for i in range(BUFFER_COUNT):
        buffers.append([0] * BUFFER_WIDTH)

    bank = bank_from_rcc(0, 1, 0, buffer_info, bitwidth=2)
    entry = entry_from_rcc(0, 1, 0, buffer_info, bitwidth=2)
    buffers[bank][entry] = 10

    bank = bank_from_rcc(0, 2, 0, buffer_info, bitwidth=2)
    entry = entry_from_rcc(0, 2, 0, buffer_info, bitwidth=2)
    buffers[bank][entry] = 10

    bank = bank_from_rcc(1, 1, 0, buffer_info, bitwidth=2)
    entry = entry_from_rcc(1, 1, 0, buffer_info, bitwidth=2)
    print(bank, entry)
    buffers[bank][entry] = 53

    ppu_output = yield do_ppu(
        ppu,
        channel_group_done,
        oaram,
        oaram_indices,
        buffers,
        neighbor_input,
        neighbor_exchange_done,
        neighbor_cts,
    )

    tc.assertFalse(ppu_output.exchange_done)

    update_buffer(buffers, ppu_output.buffer_outputs, buffer_info)

    channel_group_done = False

    for i in range(RAM_SIZE):
        ppu_output = yield do_ppu(
            ppu,
            channel_group_done,
            oaram,
            oaram_indices,
            buffers,
            neighbor_input,
            neighbor_exchange_done,
            neighbor_cts,
        )
        update_buffer(buffers, ppu_output.buffer_outputs, buffer_info)

    tc.assertTrue(ppu_output.exchange_done)

    neighbor_exchange_done = [True] * 8

    neighbor_input[Neighbor.LEFT.value] = (5, 1, 1, 0)
    neighbor_input[Neighbor.TOP_LEFT.value] = (6, 1, 1, 0)
    ppu_output = yield do_ppu(
        ppu,
        channel_group_done,
        oaram,
        oaram_indices,
        buffers,
        neighbor_input,
        neighbor_exchange_done,
        neighbor_cts,
    )
    tc.assertFalse(ppu_output.clear_to_send)
    update_buffer(buffers, ppu_output.buffer_outputs, buffer_info)

    neighbor_input = [(0, -1, -1, -1)] * 8

    ppu_output = yield do_ppu(
        ppu,
        channel_group_done,
        oaram,
        oaram_indices,
        buffers,
        neighbor_input,
        neighbor_exchange_done,
        neighbor_cts,
    )
    # verify that we are done processing, actual value is don't care
    tc.assertTrue(ppu_output.clear_to_send)

    tc.assertFalse(ppu_output.cycle_done)
    update_buffer(buffers, ppu_output.buffer_outputs, buffer_info)

    for i in range(RAM_SIZE):
        ppu_output = yield do_ppu(
            ppu,
            channel_group_done,
            oaram,
            oaram_indices,
            buffers,
            neighbor_input,
            neighbor_exchange_done,
            neighbor_cts,
        )

    tc.assertTrue(ppu_output.cycle_done)

    tc.assertEqual(oaram[0], 57)
    tc.assertEqual(oaram[1], 64)
    tc.assertEqual(oaram[2], 0)
    tc.assertEqual(oaram[3], 0)

    tc.assertEqual(oaram_indices[0], 0)
    tc.assertEqual(oaram_indices[1], 15)
    tc.assertEqual(oaram_indices[2], 15)
