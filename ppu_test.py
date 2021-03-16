import unittest
import ppu


class PPUTest(unittest.TestCase):
    def test_ppu_done_on_first_cycle(self):
        RAM_SIZE = 1024
        BUFFER_COUNT = 32
        BUFFER_WIDTH = 32
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT)
        state = ppu.PPUState(buffer_info)
        oaram = [0] * RAM_SIZE
        oaram_indices = [0] * RAM_SIZE
        back_buffers = [[0] * BUFFER_WIDTH] * BUFFER_COUNT
        neighbor_input = [(0, -1, -1, -1)] * 8
        neighbor_cts = [False] * 8
        done, buffer_outputs, neighbor_outputs, cts = ppu.ppu(
            state,
            False,
            oaram,
            oaram_indices,
            back_buffers,
            neighbor_input,
            neighbor_cts,
            kernel_size=3,
            buffer_address_info=buffer_info,
        )
        self.assertTrue(done)
        self.assertTrue(cts)

    def test_ppu_saves_incoming_partial_sum(self):
        RAM_SIZE = 1024
        BUFFER_COUNT = 32
        BUFFER_WIDTH = 32
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT)

        state = ppu.PPUState(buffer_info)
        oaram = [0] * RAM_SIZE
        oaram_indices = [0] * RAM_SIZE
        back_buffers = [[0] * BUFFER_WIDTH] * BUFFER_COUNT
        neighbor_input = [(3, 1, 1, 1)] + [(0, -1, -1, -1)] * 7
        neighbor_cts = [False] * 8
        done, buffer_outputs, neighbor_outputs, cts = ppu.ppu(
            state,
            False,
            oaram,
            oaram_indices,
            back_buffers,
            neighbor_input,
            neighbor_cts,
            kernel_size=3,
            buffer_address_info=buffer_info,
        )

        expected_buffer_outputs = [(0, -1, -1, -1)] * BUFFER_COUNT
        expected_buffer_outputs[ppu.bank_from_rcc(1, 1, 1, buffer_info)] = (3, 1, 1, 1)
        self.assertEqual(buffer_outputs, expected_buffer_outputs)

    def test_has_leftover_inputs(self):
        RAM_SIZE = 1024
        BUFFER_COUNT = 32
        BUFFER_WIDTH = 32
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT)

        state = ppu.PPUState(buffer_info)
        self.assertFalse(ppu.has_leftover_inputs(state))

        state.neighbor_inputs[0] = (1, 2, 2)

        self.assertTrue(ppu.has_leftover_inputs(state))

    def test_ppu_saves_sets_cts_false_when_conflicting_bank(self):
        RAM_SIZE = 1024
        BUFFER_COUNT = 32
        BUFFER_WIDTH = 32
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT)

        state = ppu.PPUState(buffer_info)
        oaram = [0] * RAM_SIZE
        oaram_indices = [0] * RAM_SIZE
        back_buffers = [[0] * BUFFER_WIDTH] * BUFFER_COUNT
        neighbor_input = [(3, 1, 1, 1), (1,1,1, 1)] + [(0, -1, -1, -1)] * 6
        neighbor_cts = [False] * 8
        done, buffer_outputs, neighbor_outputs, cts = ppu.ppu(
            state,
            False,
            oaram,
            oaram_indices,
            back_buffers,
            neighbor_input,
            neighbor_cts,
            kernel_size=3,
            buffer_address_info=buffer_info,
        )
        self.assertFalse(done)
        self.assertFalse(cts)

        expected_buffer_outputs = [(0, -1, -1, -1)] * BUFFER_COUNT
        expected_buffer_outputs[ppu.bank_from_rcc(1, 1, 1, buffer_info)] = (3, 1, 1, 1)
        self.assertEqual(buffer_outputs, expected_buffer_outputs)

        done, buffer_outputs, neighbor_outputs, cts = ppu.ppu(
            state,
            False,
            oaram,
            oaram_indices,
            back_buffers,
            neighbor_input,
            neighbor_cts,
            kernel_size=3,
            buffer_address_info=buffer_info,
        )

        self.assertTrue(done)
        self.assertTrue(cts)

        expected_buffer_outputs = [(0, -1, -1, -1)] * BUFFER_COUNT
        expected_buffer_outputs[ppu.bank_from_rcc(1, 1, 1, buffer_info)] = (1, 1, 1, 1)
        self.assertEqual(buffer_outputs, expected_buffer_outputs)

    def test_no_partials_in_reset_state(self):
        RAM_SIZE = 1024
        BUFFER_COUNT = 32
        BUFFER_WIDTH = 32
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT)

        state = ppu.PPUState(buffer_info)
        channel_group_done = False
        neighbor_cts = [True] * 8
        buffers = [[0] * BUFFER_WIDTH] * BUFFER_COUNT
        neighbor_outputs = ppu.output_partials(state, channel_group_done, neighbor_cts, buffers, buffer_info)

        expected_neighbor_outputs = [(0, -1, -1, -1)] * 8
        self.assertEqual(neighbor_outputs, expected_neighbor_outputs)

    def test_all_zero_partials_after_reset_yields_no_outputs(self):
        RAM_SIZE = 1024
        BUFFER_COUNT = 32
        BUFFER_WIDTH = 32
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT)

        state = ppu.PPUState(buffer_info)
        channel_group_done = True
        neighbor_cts = [True] * 8
        buffers = [[0] * BUFFER_WIDTH] * BUFFER_COUNT
        neighbor_outputs = ppu.output_partials(state, channel_group_done, neighbor_cts, buffers, buffer_info)

        expected_neighbor_outputs = [(0, -1, -1, -1)] * 8
        self.assertEqual(neighbor_outputs, expected_neighbor_outputs)

    def test_bank_entry_to_rcc_inverts_bank(self):
        BUFFER_COUNT = 32
        BUFFER_WIDTH = 32
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT)

        row = 0
        column = 0
        channel = 0
        bank = ppu.bank_from_rcc(row, column, channel, buffer_info)
        entry = ppu.entry_from_rcc(row, column, channel, buffer_info)
        rcc = ppu.bank_entry_to_rcc(bank, entry, buffer_info)
        self.assertEqual(rcc, (row, column, channel))

        row = 5
        column = 0
        channel = 0
        bank = ppu.bank_from_rcc(row, column, channel, buffer_info)
        entry = ppu.entry_from_rcc(row, column, channel, buffer_info)
        rcc = ppu.bank_entry_to_rcc(bank, entry, buffer_info)
        self.assertEqual(rcc, (row, column, channel))

        row = 0
        column = 3
        channel = 0
        bank = ppu.bank_from_rcc(row, column, channel, buffer_info)
        entry = ppu.entry_from_rcc(row, column, channel, buffer_info)
        rcc = ppu.bank_entry_to_rcc(bank, entry, buffer_info)
        self.assertEqual(rcc, (row, column, channel))

        row = 7
        column = 20
        channel = 0
        bank = ppu.bank_from_rcc(row, column, channel, buffer_info)
        entry = ppu.entry_from_rcc(row, column, channel, buffer_info)
        rcc = ppu.bank_entry_to_rcc(bank, entry, buffer_info)
        self.assertEqual(rcc, (row, column, channel))

        row = 1
        column = 29
        channel = 0
        bank = ppu.bank_from_rcc(row, column, channel, buffer_info)
        entry = ppu.entry_from_rcc(row, column, channel, buffer_info)
        rcc = ppu.bank_entry_to_rcc(bank, entry, buffer_info)
        self.assertEqual(rcc, (row, column, channel))

        row = 7
        column = 5
        bank = ppu.bank_from_rcc(row, column, 0, buffer_info, 2)
        entry = ppu.entry_from_rcc(row, column, 0, buffer_info, 2)
        rcc = ppu.bank_entry_to_rcc(bank, entry, buffer_info, 2)
        self.assertEqual(rcc, (row, column, 0))

        buffer_info = ppu.BufferAddressInfo(32)
        used_width = 8
        vals = []
        for i in range(0, 32):
            vals.append([(0,0)] * 2)
        for i in range(0, used_width):
            string = ""
            for k in range(0,used_width):
                bank = ppu.bank_from_rcc(i, k, 0, buffer_info, 2)
                entry = ppu.entry_from_rcc(i, k, 0, buffer_info, 2)
                vals[bank][entry] = (i,k)
                rcc = ppu.bank_entry_to_rcc(bank, entry, buffer_info, 2)
                self.assertEqual(rcc[0], i)
                self.assertEqual(rcc[1], k)
                string += "({},{})\t".format(bank,entry)
            # print(string)

        # for row in vals:
            # print(row)


    def test_neighbor_from_rcc(self):
        BUFFER_COUNT = 6
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT, tile_size=6)
        kernel_size = 3

        self.assertEqual(ppu.Neighbor.TOP_LEFT, ppu.neighbor_from_rcc((0, 0, 0), buffer_info))
        self.assertEqual(ppu.Neighbor.TOP, ppu.neighbor_from_rcc((0, 2, 0), buffer_info))
        self.assertEqual(ppu.Neighbor.TOP_RIGHT, ppu.neighbor_from_rcc((0, 5, 0), buffer_info))
        self.assertEqual(ppu.Neighbor.LEFT, ppu.neighbor_from_rcc((4, 0, 0), buffer_info))
        self.assertEqual(ppu.Neighbor.RIGHT, ppu.neighbor_from_rcc((3, 5, 0), buffer_info))
        self.assertEqual(ppu.Neighbor.BOTTOM_LEFT, ppu.neighbor_from_rcc((5, 0, 0), buffer_info))
        self.assertEqual(ppu.Neighbor.BOTTOM, ppu.neighbor_from_rcc((5, 3, 0), buffer_info))
        self.assertEqual(ppu.Neighbor.BOTTOM_RIGHT, ppu.neighbor_from_rcc((5, 5, 0), buffer_info))

    def test_neighbor_rcc(self):
        BUFFER_COUNT = 6
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT, tile_size=6)
        kernel_size = 3
        
        rcc = (0, 0, 0)
        rcc_neighbor = ppu.get_neighbor_rcc(rcc, ppu.Neighbor.TOP_LEFT, buffer_info, kernel_size=kernel_size)
        self.assertEqual(rcc_neighbor, (4, 4, 0))

        rcc = (0, 2, 0)
        rcc_neighbor = ppu.get_neighbor_rcc(rcc, ppu.Neighbor.TOP, buffer_info, kernel_size=kernel_size)
        self.assertEqual(rcc_neighbor, (4, 2, 0))

        rcc = (0, 5, 0)
        rcc_neighbor = ppu.get_neighbor_rcc(rcc, ppu.Neighbor.TOP_RIGHT, buffer_info, kernel_size=kernel_size)
        self.assertEqual(rcc_neighbor, (4, 1, 0))

        rcc = (0, 5, 0)
        rcc_neighbor = ppu.get_neighbor_rcc(rcc, ppu.Neighbor.TOP_RIGHT, buffer_info, kernel_size=5)
        self.assertEqual(rcc_neighbor, (2, 3, 0))

        rcc = (3, 0, 0)
        rcc_neighbor = ppu.get_neighbor_rcc(rcc, ppu.Neighbor.LEFT, buffer_info, kernel_size=kernel_size)
        self.assertEqual(rcc_neighbor, (3, 4, 0))

        rcc = (2, 5, 0)
        rcc_neighbor = ppu.get_neighbor_rcc(rcc, ppu.Neighbor.RIGHT, buffer_info, kernel_size=kernel_size)
        self.assertEqual(rcc_neighbor, (2, 1, 0))

        rcc = (5, 0, 0)
        rcc_neighbor = ppu.get_neighbor_rcc(rcc, ppu.Neighbor.BOTTOM_LEFT, buffer_info, kernel_size=kernel_size)
        self.assertEqual(rcc_neighbor, (1, 4, 0))

        rcc = (5, 3, 0)
        rcc_neighbor = ppu.get_neighbor_rcc(rcc, ppu.Neighbor.BOTTOM, buffer_info, kernel_size=kernel_size)
        self.assertEqual(rcc_neighbor, (1, 3, 0))

        rcc = (5, 5, 0)
        rcc_neighbor = ppu.get_neighbor_rcc(rcc, ppu.Neighbor.BOTTOM_RIGHT, buffer_info, kernel_size=kernel_size)
        self.assertEqual(rcc_neighbor, (1, 1, 0))


        BUFFER_COUNT = 32
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT, tile_size=32)
        rcc = (0, 1, 1)
        rcc_neighbor = ppu.get_neighbor_rcc(rcc, ppu.Neighbor.TOP, buffer_info, kernel_size=kernel_size)
        self.assertEqual(rcc_neighbor, (30, 1, 1))

    def test_non_zero_partial_after_reset_yields_one_output(self):
        RAM_SIZE = 1024
        BUFFER_COUNT = 32
        BUFFER_WIDTH = 32
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT, tile_size=32)

        state = ppu.PPUState(buffer_info)
        channel_group_done = True
        neighbor_cts = [True] * 8
        buffers = [[0] * BUFFER_WIDTH] * BUFFER_COUNT
        buffers[0][0] = 5 # 0,0 is outside for kernel size > 1
        neighbor_outputs = ppu.output_partials(state, channel_group_done, neighbor_cts, buffers, buffer_info)

        expected_neighbor_outputs = [(0, -1, -1, -1)] * 8
        expected_neighbor_outputs[ppu.Neighbor.TOP_LEFT.value] = (5, 30, 30, 0) # remove padding bottom right corner
        self.assertEqual(neighbor_outputs, expected_neighbor_outputs)

    def test_non_zero_partial_no_reset_yields_no_outputs(self):
        RAM_SIZE = 1024
        BUFFER_COUNT = 32
        BUFFER_WIDTH = 32
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT, tile_size=32)

        state = ppu.PPUState(buffer_info)
        channel_group_done = False
        neighbor_cts = [True] * 8
        buffers = [[0] * BUFFER_WIDTH] * BUFFER_COUNT
        buffers[0][0] = 5 # 0,0 is outside for kernel size > 1
        neighbor_outputs = ppu.output_partials(state, channel_group_done, neighbor_cts, buffers, buffer_info)

        expected_neighbor_outputs = [(0, -1, -1, -1)] * 8
        self.assertEqual(neighbor_outputs, expected_neighbor_outputs)

    def test_non_zero_partials_after_reset_output_in_order(self):
        RAM_SIZE = 1024
        BUFFER_COUNT = 32
        BUFFER_WIDTH = 32
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT, tile_size=32)

        state = ppu.PPUState(buffer_info)
        channel_group_done = True
        neighbor_cts = [True] * 8
        buffers = []
        for i in range(BUFFER_COUNT):
            buffers.append([0] * BUFFER_WIDTH)
        buffers[0][0] = 5 # 0,0 is outside for kernel size > 1

        bank = ppu.bank_from_rcc(0, 1, 0, buffer_info)
        entry = ppu.entry_from_rcc(0, 1, 0, buffer_info)
        buffers[bank][entry] = 10
        neighbor_outputs = ppu.output_partials(state, channel_group_done, neighbor_cts, buffers, buffer_info)

        expected_neighbor_outputs = [(0, -1, -1, -1)] * 8
        expected_neighbor_outputs[ppu.Neighbor.TOP_LEFT.value] = (5, 30, 30, 0) # remove padding bottom right corner
        self.assertEqual(neighbor_outputs, expected_neighbor_outputs)

        counter = 0
        while True:
            counter += 1
            self.assertFalse(counter > RAM_SIZE, "Exceeded runtime at {} cycles".format(counter))
            channel_group_done = False
            neighbor_outputs = ppu.output_partials(state, channel_group_done, neighbor_cts, buffers, buffer_info)
            expected_neighbor_outputs = [(0, -1, -1, -1)] * 8
            if neighbor_outputs[ppu.Neighbor.TOP.value] == (10, 30, 1, 0):
                expected_neighbor_outputs[ppu.Neighbor.TOP.value] = (10, 30, 1, 0)
                self.assertEqual(neighbor_outputs, expected_neighbor_outputs)
                break
            self.assertEqual(neighbor_outputs, expected_neighbor_outputs)

    def test_not_cts_stalls_ppu(self):
        RAM_SIZE = 1024
        BUFFER_COUNT = 32
        BUFFER_WIDTH = 32
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT, tile_size=32)

        state = ppu.PPUState(buffer_info)
        channel_group_done = True
        neighbor_cts = [True] * 8
        neighbor_cts[ppu.Neighbor.TOP_LEFT.value] = False
        buffers = [[0] * BUFFER_WIDTH] * BUFFER_COUNT
        buffers[0][0] = 5 # 0,0 is outside for kernel size > 1
        neighbor_outputs = ppu.output_partials(state, channel_group_done, neighbor_cts, buffers, buffer_info)

        expected_neighbor_outputs = [(0, -1, -1, -1)] * 8
        self.assertEqual(neighbor_outputs, expected_neighbor_outputs)

        neighbor_cts = [True] * 8

        neighbor_outputs = ppu.output_partials(state, channel_group_done, neighbor_cts, buffers, buffer_info)

        expected_neighbor_outputs = [(0, -1, -1, -1)] * 8
        expected_neighbor_outputs[ppu.Neighbor.TOP_LEFT.value] = (5, 30, 30, 0)
        self.assertEqual(neighbor_outputs, expected_neighbor_outputs)

    def test_after_at_most_ram_size_cycles_transmit_done(self):
        RAM_SIZE = 1024
        BUFFER_COUNT = 32
        BUFFER_WIDTH = 32
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT, tile_size=32)

        state = ppu.PPUState(buffer_info)
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
            ppu_output = ppu.ppu(
                state,
                channel_group_done,
                oaram,
                oaram_indices,
                buffers,
                neighbor_input,
                neighbor_exchange_done,
                neighbor_cts,
                buffer_address_info=buffer_info,
            )

        self.assertTrue(ppu_output.exchange_done)

    def test_exchange_not_done_after_one_cycle(self):
        RAM_SIZE = 1024
        BUFFER_COUNT = 32
        BUFFER_WIDTH = 32
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT, tile_size=32)

        state = ppu.PPUState(buffer_info)
        oaram = [0] * RAM_SIZE
        oaram_indices = [0] * RAM_SIZE
        neighbor_input = [(0, -1, -1, -1)] * 8
        channel_group_done = True
        neighbor_cts = [True] * 8
        neighbor_exchange_done = [False] * 8
        buffers = []
        for i in range(BUFFER_COUNT):
            buffers.append([0] * BUFFER_WIDTH)

        bank = ppu.bank_from_rcc(0, 1, 0, buffer_info)
        entry = ppu.entry_from_rcc(0, 1, 0, buffer_info)
        buffers[bank][entry] = 10

        bank = ppu.bank_from_rcc(0, 2, 0, buffer_info)
        entry = ppu.entry_from_rcc(0, 2, 0, buffer_info)
        buffers[bank][entry] = 10

        ppu_output = ppu.ppu(
            state,
            channel_group_done,
            oaram,
            oaram_indices,
            buffers,
            neighbor_input,
            neighbor_exchange_done,
            neighbor_cts,
            buffer_address_info=buffer_info,
        )

        self.assertFalse(ppu_output.exchange_done)

        for i in range(RAM_SIZE):
            ppu_output = ppu.ppu(
                state,
                channel_group_done,
                oaram,
                oaram_indices,
                buffers,
                neighbor_input,
                neighbor_exchange_done,
                neighbor_cts,
                buffer_address_info=buffer_info,
            )

        self.assertTrue(ppu_output.exchange_done)

    def test_accumulator_buffers_stored_sparsely(self):
        RAM_SIZE = 1024
        BUFFER_COUNT = 32
        BUFFER_WIDTH = 32
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT, tile_size=32)
        oaram = [0] * RAM_SIZE
        oaram_indices = [0] * RAM_SIZE
        neighbor_exchange_done = [True] * 8

        state = ppu.PPUState(buffer_info)
        buffers = []
        for i in range(BUFFER_COUNT):
            buffers.append([0] * BUFFER_WIDTH)

        bank = ppu.bank_from_rcc(1, 1, 0, buffer_info)
        entry = ppu.entry_from_rcc(1, 1, 0, buffer_info)
        buffers[bank][entry] = 10

        bank = ppu.bank_from_rcc(1, 2, 0, buffer_info)
        entry = ppu.entry_from_rcc(1, 2, 0, buffer_info)
        buffers[bank][entry] = 15

        done = ppu.output_accumulator(
            state,
            oaram,
            oaram_indices,
            buffers,
            neighbor_exchange_done,
            buffer_info,
            max_zero=15,
        )

        self.assertFalse(done)

        for i in range(RAM_SIZE - 1):
            done = ppu.output_accumulator(
                state,
                oaram,
                oaram_indices,
                buffers,
                neighbor_exchange_done,
                buffer_info,
                max_zero=15,
            )

        done = ppu.output_accumulator(
            state,
            oaram,
            oaram_indices,
            buffers,
            neighbor_exchange_done,
            buffer_info,
            max_zero=15,
        )

        self.assertTrue(done)

        self.assertEqual(oaram[0], 58)
        self.assertEqual(oaram[1], 10)
        self.assertEqual(oaram[2], 15)

        self.assertEqual(oaram_indices[0], 0)
        self.assertEqual(oaram_indices[1], 0)

    def test_accumulator_buffers_wait_for_exchange_done(self):
        RAM_SIZE = 1024
        BUFFER_COUNT = 32
        BUFFER_WIDTH = 32
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT, tile_size=32)
        oaram = [0] * RAM_SIZE
        oaram_indices = [0] * RAM_SIZE
        neighbor_exchange_done = [False] * 8

        state = ppu.PPUState(buffer_info)
        buffers = []
        for i in range(BUFFER_COUNT):
            buffers.append([0] * BUFFER_WIDTH)

        bank = ppu.bank_from_rcc(1, 1, 0, buffer_info)
        entry = ppu.entry_from_rcc(1, 1, 0, buffer_info)
        buffers[bank][entry] = 10

        done = ppu.output_accumulator(
            state,
            oaram,
            oaram_indices,
            buffers,
            neighbor_exchange_done,
            buffer_info,
            max_zero=15,
        )

        self.assertFalse(done)

        for i in range(RAM_SIZE - 1):
            done = ppu.output_accumulator(
                state,
                oaram,
                oaram_indices,
                buffers,
                neighbor_exchange_done,
                buffer_info,
                max_zero=15,
            )

        done = ppu.output_accumulator(
            state,
            oaram,
            oaram_indices,
            buffers,
            neighbor_exchange_done,
            buffer_info,
            max_zero=15,
        )

        self.assertFalse(done)

    def test_accumulator_buffers_relu_applied(self):
        RAM_SIZE = 1024
        BUFFER_COUNT = 32
        BUFFER_WIDTH = 32
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT, tile_size=32)
        oaram = [0] * RAM_SIZE
        oaram_indices = [0] * RAM_SIZE
        neighbor_exchange_done = [True] * 8

        state = ppu.PPUState(buffer_info)
        buffers = []
        for i in range(BUFFER_COUNT):
            buffers.append([0] * BUFFER_WIDTH)

        bank = ppu.bank_from_rcc(1, 1, 0, buffer_info)
        entry = ppu.entry_from_rcc(1, 1, 0, buffer_info)
        buffers[bank][entry] = -10

        bank = ppu.bank_from_rcc(1, 2, 0, buffer_info)
        entry = ppu.entry_from_rcc(1, 2, 0, buffer_info)
        buffers[bank][entry] = 15

        done = ppu.output_accumulator(
            state,
            oaram,
            oaram_indices,
            buffers,
            neighbor_exchange_done,
            buffer_info,
            max_zero=15,
        )

        self.assertFalse(done)

        for i in range(RAM_SIZE - 1):
            done = ppu.output_accumulator(
                state,
                oaram,
                oaram_indices,
                buffers,
                neighbor_exchange_done,
                buffer_info,
                max_zero=15,
            )

        done = ppu.output_accumulator(
            state,
            oaram,
            oaram_indices,
            buffers,
            neighbor_exchange_done,
            buffer_info,
            max_zero=15,
        )

        self.assertTrue(done)

        self.assertEqual(oaram[0], 57)
        self.assertEqual(oaram[1], 15)

        self.assertEqual(oaram_indices[0], 1)

    def test_max_zero_count_respected(self):
        RAM_SIZE = 1024
        BUFFER_COUNT = 32
        BUFFER_WIDTH = 32
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT, tile_size=32)
        oaram = [0] * RAM_SIZE
        oaram_indices = [0] * RAM_SIZE
        neighbor_exchange_done = [True] * 8

        state = ppu.PPUState(buffer_info)
        buffers = []
        for i in range(BUFFER_COUNT):
            buffers.append([0] * BUFFER_WIDTH)

        bank = ppu.bank_from_rcc(1, 1, 0, buffer_info)
        entry = ppu.entry_from_rcc(1, 1, 0, buffer_info)
        buffers[bank][entry] = -10

        bank = ppu.bank_from_rcc(1, 2, 0, buffer_info)
        entry = ppu.entry_from_rcc(1, 2, 0, buffer_info)
        buffers[bank][entry] = 15

        bank = ppu.bank_from_rcc(1, 7, 0, buffer_info)
        entry = ppu.entry_from_rcc(1, 7, 0, buffer_info)
        buffers[bank][entry] = 2

        done = ppu.output_accumulator(
            state,
            oaram,
            oaram_indices,
            buffers,
            neighbor_exchange_done,
            buffer_info,
            max_zero=3,
        )

        self.assertFalse(done)

        for i in range(RAM_SIZE - 1):
            done = ppu.output_accumulator(
                state,
                oaram,
                oaram_indices,
                buffers,
                neighbor_exchange_done,
                buffer_info,
                max_zero=3,
            )

        done = ppu.output_accumulator(
            state,
            oaram,
            oaram_indices,
            buffers,
            neighbor_exchange_done,
            buffer_info,
            max_zero=3,
        )

        self.assertTrue(done)

        self.assertEqual(oaram[0], 226)
        self.assertEqual(oaram[1], 15)
        self.assertEqual(oaram[2], 0)
        self.assertEqual(oaram[3], 2)

        self.assertEqual(oaram_indices[0], 1)
        self.assertEqual(oaram_indices[1], 3)
        self.assertEqual(oaram_indices[2], 0)

    def test_all_zero_outputs(self):
        RAM_SIZE = 1024
        BUFFER_COUNT = 32
        BUFFER_WIDTH = 32
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT, tile_size=32)
        oaram = [0] * RAM_SIZE
        oaram_indices = [0] * RAM_SIZE
        neighbor_exchange_done = [True] * 8

        state = ppu.PPUState(buffer_info)
        buffers = []
        for i in range(BUFFER_COUNT):
            buffers.append([0] * BUFFER_WIDTH)

        done = ppu.output_accumulator(
            state,
            oaram,
            oaram_indices,
            buffers,
            neighbor_exchange_done,
            buffer_info,
            max_zero=3,
        )

        self.assertFalse(done)

        for i in range(RAM_SIZE - 1):
            done = ppu.output_accumulator(
                state,
                oaram,
                oaram_indices,
                buffers,
                neighbor_exchange_done,
                buffer_info,
                max_zero=3,
            )

        done = ppu.output_accumulator(
            state,
            oaram,
            oaram_indices,
            buffers,
            neighbor_exchange_done,
            buffer_info,
            max_zero=3,
        )

        self.assertTrue(done)

        self.assertEqual(oaram[0], 225)
        self.assertEqual(oaram[1], 0)
        self.assertEqual(oaram[2], 0)
        self.assertEqual(oaram[3], 0)

        self.assertEqual(oaram_indices[0], 3)
        self.assertEqual(oaram_indices[1], 3)
        self.assertEqual(oaram_indices[2], 3)

    def update_buffer(self, buffers, buffer_outputs, buffer_info):
        for i in range(len(buffer_outputs)):
            elem = buffer_outputs[i]
            if elem[1] == -1:
                continue
            entry = ppu.entry_from_rcc(elem[1], elem[2], elem[3], buffer_info)
            buffers[i][entry] += elem[0]

    def test_full_unit(self):
        RAM_SIZE = 1024
        BUFFER_COUNT = 32
        BUFFER_WIDTH = 32
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT, tile_size=32)

        state = ppu.PPUState(buffer_info)
        oaram = [0] * RAM_SIZE
        oaram_indices = [0] * RAM_SIZE
        neighbor_input = [(0, -1, -1, -1)] * 8
        channel_group_done = True
        neighbor_cts = [True] * 8
        neighbor_exchange_done = [False] * 8
        buffers = []
        for i in range(BUFFER_COUNT):
            buffers.append([0] * BUFFER_WIDTH)

        bank = ppu.bank_from_rcc(0, 1, 0, buffer_info)
        entry = ppu.entry_from_rcc(0, 1, 0, buffer_info)
        buffers[bank][entry] = 10

        bank = ppu.bank_from_rcc(0, 2, 0, buffer_info)
        entry = ppu.entry_from_rcc(0, 2, 0, buffer_info)
        buffers[bank][entry] = 10

        bank = ppu.bank_from_rcc(1, 1, 0, buffer_info)
        entry = ppu.entry_from_rcc(1, 1, 0, buffer_info)
        buffers[bank][entry] = 53

        ppu_output = ppu.ppu(
            state,
            channel_group_done,
            oaram,
            oaram_indices,
            buffers,
            neighbor_input,
            neighbor_exchange_done,
            neighbor_cts,
            buffer_address_info=buffer_info,
        )

        self.assertFalse(ppu_output.exchange_done)

        self.update_buffer(buffers, ppu_output.buffer_outputs, buffer_info)

        channel_group_done = False

        for i in range(RAM_SIZE):
            ppu_output = ppu.ppu(
                state,
                channel_group_done,
                oaram,
                oaram_indices,
                buffers,
                neighbor_input,
                neighbor_exchange_done,
                neighbor_cts,
                buffer_address_info=buffer_info,
            )
            self.update_buffer(buffers, ppu_output.buffer_outputs, buffer_info)

        self.assertTrue(ppu_output.exchange_done)

        neighbor_exchange_done = [True] * 8

        neighbor_input[ppu.Neighbor.LEFT.value] = (5, 1, 1, 0)
        neighbor_input[ppu.Neighbor.TOP_LEFT.value] = (6, 1, 1, 0)
        ppu_output = ppu.ppu(
            state,
            channel_group_done,
            oaram,
            oaram_indices,
            buffers,
            neighbor_input,
            neighbor_exchange_done,
            neighbor_cts,
            buffer_address_info=buffer_info,
        )
        self.assertFalse(ppu_output.clear_to_send)
        self.update_buffer(buffers, ppu_output.buffer_outputs, buffer_info)

        neighbor_input = [(0, -1, -1, -1)] * 8

        ppu_output = ppu.ppu(
            state,
            channel_group_done,
            oaram,
            oaram_indices,
            buffers,
            neighbor_input,
            neighbor_exchange_done,
            neighbor_cts,
            buffer_address_info=buffer_info,
        )
        # verify that we are done processing, actual value is don't care
        self.assertTrue(ppu_output.clear_to_send)

        self.assertFalse(ppu_output.cycle_done)
        self.update_buffer(buffers, ppu_output.buffer_outputs, buffer_info)

        for i in range(RAM_SIZE):
            ppu_output = ppu.ppu(
                state,
                channel_group_done,
                oaram,
                oaram_indices,
                buffers,
                neighbor_input,
                neighbor_exchange_done,
                neighbor_cts,
                buffer_address_info=buffer_info,
            )

        self.assertTrue(ppu_output.cycle_done)

        self.assertEqual(oaram[0], 57)
        self.assertEqual(oaram[1], 64)
        self.assertEqual(oaram[2], 0)
        self.assertEqual(oaram[3], 0)

        self.assertEqual(oaram_indices[0], 0)
        self.assertEqual(oaram_indices[1], 15)
        self.assertEqual(oaram_indices[2], 15)


if __name__ == "__main__":
    unittest.main()
