# Import necessary modules
from typing import Iterable, Optional
import tic_tac_toe_pb2_grpc as ttt_grpc
import tic_tac_toe_pb2 as ttt
import argparse
from concurrent import futures
import grpc
import logging

# Function to determine the winner of the game
def get_winner(moves: Iterable[ttt.Move]) -> ttt.Mark:
    # Define the winning combinations
    winning_combinations = (
        (1, 2, 3), (4, 5, 6), (7, 8, 9),  # Rows
        (1, 4, 7), (2, 5, 8), (3, 6, 9),  # Cols
        (1, 5, 9), (3, 5, 7),             # Diagonals
    )

    # Initialize lists to store moves of each player
    x_moves = []
    o_moves = []

    # Separate the moves of each player
    for move in moves:
        if move.mark == ttt.MARK_CROSS:
            x_moves.append(move.cell)
        elif move.mark == ttt.MARK_NOUGHT:
            o_moves.append(move.cell)
        
    # Check if any player has a winning combination
    for combination in winning_combinations:
        if all((cell in x_moves) for cell in combination):
            return ttt.MARK_CROSS
        if all((cell in o_moves) for cell in combination):
            return ttt.MARK_NOUGHT
        
     # Return None if there is no winner
    return None

# Define the gRPC service
class TicTacToeServicer(ttt_grpc.TicTacToeServicer):
    def __init__(self):
        # Initialize the games dictionary
        self.games = {}
        logging.basicConfig(level=logging.INFO, format='%(message)s')  

    # Method to create a new game
    def CreateGame(self, request, context):
        logging.info("CreateGame()")
        game_id = len(self.games) + 1
        game = ttt.Game(id=game_id, is_finished=False, turn=ttt.MARK_CROSS, winner=None, moves=[])
        self.games[game_id] = game
        return game

     # Method to get the state of a game
    def GetGame(self, request, context):
        game_id = request.game_id
        logging.info(f"GetGame(game_id={game_id})")
        if game_id not in self.games:
            context.abort(grpc.StatusCode.NOT_FOUND, "Game not found")
        return self.games[game_id]

    # Method to make a move in a game
    def MakeMove(self, request, context):
        game_id = request.game_id
        if game_id not in self.games:
            context.abort(grpc.StatusCode.NOT_FOUND, "Game not found")

        game = self.games[game_id]
        if game.is_finished:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Game is already finished")

        move = request.move
        logging.info(f"MakeMove(game_id={game_id}, move=Move(mark={move.mark}, cell={move.cell}))")
        
        if move.mark != game.turn:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "It's not the player's turn")

        if move.cell < 1 or move.cell > 9:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Move's cell is invalid")

        if any(m.cell == move.cell for m in game.moves):
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Move's cell is already occupied")

        # Add the move to the game
        game.moves.append(ttt.Move(mark=game.turn, cell=move.cell))
    
        # Check if the game is finished and determine the winner
        winner = get_winner(game.moves)
        if winner is not None:
            game.is_finished = True
            game.winner = winner
        elif len(game.moves) == 9:
            game.is_finished = True
        else:
            game.turn = ttt.MARK_CROSS if game.turn == ttt.MARK_NOUGHT else ttt.MARK_NOUGHT

        return game

# Main function to start the server
def main():
    parser = argparse.ArgumentParser(description='Tic Tac Toe server')
    parser.add_argument('port', type=int, help='the port to listen on')
    args = parser.parse_args()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ttt_grpc.add_TicTacToeServicer_to_server(TicTacToeServicer(), server)
    server.add_insecure_port(f'[::]:{args.port}')
    
    print(f'Server listening on 0.0.0.0:{args.port}')

    try:
        while True:
            server.start()
            server.wait_for_termination()

    except KeyboardInterrupt:
        print("Shutting down the server...")
        server.stop(0)


if __name__ == "__main__":
    main()