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

    def test_non_zero_partial_after_reset_yields_one_output(self):

        RAM_SIZE = 1024
        BUFFER_COUNT = 32
        BUFFER_WIDTH = 32
        buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT)
        ranges = [0] * 32
        # for i in range(0, 32):
        #     string = ""
        #     for k in range(0, 32):
        #         val = ""
        #         mi = 2
        #         ma = 29
        #         if i <= mi or i >= ma or k <= mi or k >= ma:
        #             val = ppu.bank_from_rcc(i, k, buffer_info)
        #             ranges[val] += 1
        #         string += "{}\t".format(val)
        #         # if val == 0:
        #             # print("({}, {})".format(i, k))
        #     # print(string)
        # for i in range(0, 32):
        #     print("{}: {}".format(i, ranges[i]))

        state = ppu.PPUState(buffer_info)
        channel_group_done = True
        neighbor_cts = [True] * 8
        buffers = [[0] * BUFFER_WIDTH] * BUFFER_COUNT
        buffers[0][0] = 5 # 0,0 is outside for kernel size > 1
        neighbor_outputs = ppu.output_partials(state, channel_group_done, neighbor_cts, buffers, buffer_info)

        expected_neighbor_outputs = [(0, -1, -1, -1)] * 8
        expected_neighbor_outputs[ppu.Neighbor.TOP_LEFT.value] = (5, 30, 30, 0) # remove padding bottom right corner
        self.assertEqual(neighbor_outputs, expected_neighbor_outputs)


if __name__ == "__main__":
    unittest.main()