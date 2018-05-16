# -*- encoding=utf8 -*-
import argparse
import os
import time
from collections import defaultdict
import logging

from Board import Board
from Game import Game
from Util import load_current_best_player

logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Log等级总开关
rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
log_name = './logs/' + 'contest-' +rq + '.log'
logfile = log_name

fh = logging.FileHandler(logfile, mode='w')
fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)


def contest(directory_name, n_games=20):
    """
    比较directory下各个模型间棋力最强的模型
    :param directory_name:
    :param n_games: 模型间对弈次数
    :return: 最强模型对应的文件名
    """

    filenames = os.listdir(directory_name)

    cur_players = []
    for filename in filenames:
        if filename.endswith("pkl"):
            player = load_current_best_player(os.path.join(directory_name, filename))
            player.filename = filename
            cur_players.append(player)

    board_width = 6
    board_height = 6
    n_in_row = 4
    board = Board(width=board_width, height=board_height, n_in_row=n_in_row)
    game = Game(board)
    player1, player2 = None, None
    round = 0
    while len(cur_players) >= 2:
        next_round_players = []
        for player in cur_players:
            if player1 is None:
                player1 = player
            else:
                player2 = player
                win_cnt = defaultdict(int)
                for i in range(n_games):
                    print("evaluate game %d" % i)
                    winner = game.start_game(player1, player2, who_first=i % 2, is_shown=0)
                    win_cnt[winner] += 1
                win_ratio = 1.0 * (win_cnt[1] + 0.5 * win_cnt[-1]) / n_games
                info = player1.filename + " vs " + player2.filename + " : win %d lose %d tie %d round %d" % (
                    win_cnt[1], win_cnt[2], win_cnt[-1], round)
                logger.info(info)
                if win_ratio > 0.5:
                    next_round_players.append(player1)
                elif win_ratio == 0.5:
                    next_round_players.append(player1)
                    next_round_players.append(player2)
                else:
                    next_round_players.append(player2)
                player1, player2 = None, None
        else:
            if player1:
                next_round_players.append(player1)
        cur_players = next_round_players
        round += 1
    logger.info(cur_players[0].filename +" is final winner!")
    return cur_players[0].filename


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AlphaZero Contest....')
    parser.add_argument("--dir", default=None, type=str, help="dir of models")
    parser.add_argument('--n', default=20, type=int,
                        help='number of games for each contest')
    args = parser.parse_args()
    contest(args.dir, args.n)
