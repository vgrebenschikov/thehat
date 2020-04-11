from pair import Pair


class NextPairAlg:
    @staticmethod
    def get_start_pair(config):
        pass

    @staticmethod
    def get_next_pair(config, cur_pair, cur_turn):
        pass


class Original(NextPairAlg):
    @staticmethod
    def get_start_pair(config):
        return Pair(0, int(config.number_players / 2))

    @staticmethod
    def get_next_pair(config, cur_pair, cur_turn):
        return Pair((cur_pair.explaining + 1) % config.number_players,
                    (cur_pair.guessing + 1) % config.number_players)


class AVA(NextPairAlg):
    @staticmethod
    def get_round_shift(config, cur_turn):
        number_rounds = 1 + AVA.get_cur_round(config, cur_turn)
        return (number_rounds + config.number_players - 2) % (config.number_players - 1) + 1

    @staticmethod
    def get_turn_in_round(config, cur_turn):
        return cur_turn % config.number_players

    @staticmethod
    def get_cur_round(config, cur_turn):
        return int(cur_turn / config.number_players)

    @staticmethod
    def get_start_pair(config):
        return Pair(0, 1)

    @staticmethod
    def get_next_pair(config, cur_pair, cur_turn):
        if cur_pair.explaining + 1 == config.number_players:
            return Pair(0, AVA.get_round_shift(config, cur_turn))
        return Pair((cur_pair.explaining + 1) % config.number_players,
                    (cur_pair.explaining + AVA.get_round_shift(config, cur_turn) + 1) % config.number_players)


class AVAF(AVA):
    @staticmethod
    def get_start_pair(config):
        return Pair(0, 1)

    @staticmethod
    def get_next_pair(config, cur_pair, cur_turn):
        round_shift = AVAF.get_round_shift(config, cur_turn)

        is_less_than_two_blocks = int(config.number_players / (2 * round_shift)) == 0

        block_size = config.number_players % round_shift if is_less_than_two_blocks else round_shift

        is_in_even_block = 0 <= cur_pair.explaining % (2 * block_size) < block_size
        is_last_in_block = cur_pair.explaining % block_size == block_size - 1

        if not is_last_in_block and cur_pair.explaining + 1 < config.number_players:
            return Pair((cur_pair.explaining + 1) % config.number_players,
                        (cur_pair.guessing + 1) % config.number_players)
        if is_last_in_block and cur_pair.explaining + block_size + 1 < config.number_players:
            return Pair((cur_pair.explaining + block_size + 1) % config.number_players,
                        (cur_pair.guessing + block_size + 1) % config.number_players)
        if is_in_even_block:
            return Pair(block_size, (block_size + round_shift) % config.number_players)
        return Pair(0, (round_shift + 1 + config.number_players - 2) % (config.number_players - 1) + 1)
