##############################################################################
# game.py - Responsible for generating moves to give to client.py            #
# Moves via stdout in the form of "# # # #" (block index, # rotations, x, y) #
# Important function is find_move, which should contain the main AI          #
##############################################################################

import sys
import json

# Simple point class that supports equality, addition, and rotations
class Point:
    x = 0
    y = 0

    # Can be instantiated as either Point(x, y) or Point({'x': x, 'y': y})
    def __init__(self, x=0, y=0):
        if isinstance(x, dict):
            self.x = x['x']
            self.y = x['y']
        else:
            self.x = x
            self.y = y

    def __add__(self, point):
        return Point(self.x + point.x, self.y + point.y)

    def __eq__(self, point):
        return self.x == point.x and self.y == point.y

    # rotates 90deg counterclockwise
    def rotate(self, num_rotations):
        if num_rotations == 1: return Point(-self.y, self.x)
        if num_rotations == 2: return Point(-self.x, -self.y)
        if num_rotations == 3: return Point(self.y, -self.x)
        return self

    def distance(self, point):
        return abs(point.x - self.x) + abs(point.y - self.y)

class Game:
    blocks = []
    grid = []
    bonus_squares = []
    my_number = -1
    dimension = -1 # Board is assumed to be square
    turn = -1

    def __init__(self, args):
        self.interpret_data(args)

    # find_move is your place to start. When it's your turn,
    # find_move will be called and you must return where to go.
    # You must return a tuple (block index, # rotations, x, y)

    def simple_evaluation(self, player):
        return 0

    def get_possible_moves(self, player):
        return []

    def get_next_player(self, player):
        return (1 + player) % 4

    def get_score(self, player, heuristic):
        ans = []
        s_player = player
        while True:
            ans.append(heuristic(player))
            s_player = self.get_next_player(s_player)
            if s_player == player:
                break
        return ans

    def apply_next_move(self, move):
        pass

    def search(self, state, depth, player, heuristic):
        # Find the best move with respect to this player
        # Return score + move
        if depth == 0: # We run out of depth
            return [state.get_score(player, heuristic), (0, 0, 0, 0)]

        best_score = 0
        best_move = (0, 0, 0, 0) # We accept null move
        all_moves = state.get_possible_moves(player)
        for move in all_moves:
            next_state = state.apply_next_move(move)
            # This returns the unrefined score, we need to refine for our own good
            next_eval = self.search(next_state, depth - 1, self.next_player(player), heuristic)[0]
            next_score = next_eval[-1]
            next_score.append(next_eval[:len(next_eval - 1)])

            if best_score < next_score:
                best_score = next_score
                best_move = move
        return [best_score, best_move]

    def find_move(self):
        return self.search(self, depth=4, player=self.my_number, heuristic=self.simple_evaluation)[1]

    # Check if we can claim any bonus square
    def is_bonus(self, block, point):
        for offset in block:
            p = point + offset
            for q in self.bonus_squares:
                if p.x == q[0] and p.y == q[1]:
                    return True
        return False

    # Checks if a block can be placed at the given point
    def can_place(self, block, point):
        onAbsCorner = False
        onRelCorner = False
        N = self.dimension - 1

        corners = [Point(0, 0), Point(N, 0), Point(N, N), Point(0, N)]
        corner = corners[self.my_number]

        for offset in block:
            p = point + offset
            x = p.x
            y = p.y
            if (x > N or x < 0 or y > N or y < 0 or self.grid[x][y] != -1 or
                (x > 0 and self.grid[x - 1][y] == self.my_number) or
                (y > 0 and self.grid[x][y - 1] == self.my_number) or
                (x < N and self.grid[x + 1][y] == self.my_number) or
                (y < N and self.grid[x][y + 1] == self.my_number)
            ): return False

            onAbsCorner = onAbsCorner or (p == corner)
            onRelCorner = onRelCorner or (
                (x > 0 and y > 0 and self.grid[x - 1][y - 1] == self.my_number) or
                (x > 0 and y < N and self.grid[x - 1][y + 1] == self.my_number) or
                (x < N and y > 0 and self.grid[x + 1][y - 1] == self.my_number) or
                (x < N and y < N and self.grid[x + 1][y + 1] == self.my_number)
            )

        if self.grid[corner.x][corner.y] < 0 and not onAbsCorner: return False
        if not onAbsCorner and not onRelCorner: return False

        return True

    # rotates block 90deg counterclockwise
    def rotate_block(self, block, num_rotations):
        return [offset.rotate(num_rotations) for offset in block]

    # updates local variables with state from the server
    def interpret_data(self, args):
        if 'error' in args:
            debug('Error: ' + args['error'])
            return

        if 'number' in args:
            self.my_number = args['number']

        if 'board' in args:
            self.dimension = args['board']['dimension']
            self.turn = args['turn']
            self.grid = args['board']['grid']
            self.blocks = args['blocks'][self.my_number]
            self.bonus_squares = args['board']['bonus_squares']

            for index, block in enumerate(self.blocks):
                self.blocks[index] = [Point(offset) for offset in block]

        if (('move' in args) and (args['move'] == 1)):
            send_command(" ".join(str(x) for x in self.find_move()))

    def is_my_turn(self):
        return self.turn == self.my_number

def get_state():
    return json.loads(raw_input())

def send_command(message):
    print message
    sys.stdout.flush()

def debug(message):
    send_command('DEBUG ' + str(message))

def main():
    setup = get_state()
    game = Game(setup)

    while True:
        state = get_state()
        game.interpret_data(state)

if __name__ == "__main__":
    main()
