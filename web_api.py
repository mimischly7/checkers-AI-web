from flask import Flask, request

import services

app = Flask(__name__)


@app.route("/getPossMoves", methods=['GET'])
def getPossMovesEndpoint():
    """
    Expects a JSON body consisting of: the gameboard, the player_id, whether the player is a king

    :return:
    """
    json_dict = request.get_json()

    board = json_dict['board']
    stone = json_dict['stone']  # this contains the id of the stone and whether it is a king or not

    poss_moves = services.getPossMoves(board, stone['id'], stone['isKing'])

    return poss_moves


@app.route("/makeMove", methods=['GET'])
def makeMoveEndpoint():
    """
    Expects a JSON body consisting of: the gameboard, the player_id, whether the player is a king

    :return:
    """
    json_dict = request.get_json()

    board = json_dict['board']
    stone = json_dict['stone']  # this contains the id of the stone and whether it is a king or not
    move = json_dict['move']

    updated_state = services.makeMove(board, stone['id'], stone['isKing'], move)

    return updated_state
