##############################################################################
# game.py - Responsible for generating moves to give to client.py            #
# Moves via stdout in the form of "# # # #" (block index, # rotations, x, y) #
# Important function is find_move, which should contain the main AI          #
##############################################################################

import sys
import json
from blocks import *


class Game:
    blocks = []
    grid = []
    bonus_squares = []
    my_number = -1
    dimension = -1 # Board is assumed to be square
    turn = -1

    def __init__(self, args):
        if type(args) == type(list):
            self.blocks = args[0]
            self.grid = args[1]
            self.bonus_squares = args[2]
            self.my_number = args[3]
            self.dimension = args[4]
            self.turn = args[5]
        else:
            self.interpret_data(args)

    # find_move is your place to start. When it's your turn,
    # find_move will be called and you must return where to go.
    # You must return a tuple (block index, # rotations, x, y)

    def simple_evaluation(self, player):
        return 1

    def get_possible_moves(self, player):
        all_blocks = [(index, block) for index, block in enumerate(self.blocks)]
        all_blocks = sorted(all_blocks, key=lambda x: len(x[1]), reverse=True)
        N = self.dimension
        all_moves = []
        for index, block in all_blocks:
            for i in range(0, N * N):
                x = i / N
                y = i % N

                for rotations in range(0, 4):
                    new_block = self.rotate_block(block, rotations)
                    if self.can_place(new_block, Point(x, y)):
                        all_moves.append((new_block, Point(x,y), index, rotations))
        return all_moves

    def get_next_player(self, player):
        return (1 + player) % 4

    def get_score(self, player, heuristic):
        ans = []
        s_player = player
        while True:
            ans.append(heuristic(s_player))
            s_player = self.get_next_player(s_player)
            if s_player == player:
                break
        return ans

    def apply_next_move(self, move):
        block, point, index, rotations = move
        n = self.get_next_move(block, point)
        return n    

    def search(self, state, depth, player, heuristic):
        # Find the best move with respect to this player
        # Return score + move
        if depth == 0: # We run out of depth
            return [state.get_score(player, heuristic), (0, 0, 0, 0)]

        best_score = [0, 0, 0, 0]
        best_move = (0, 0, 0, 0) # We accept null move
        all_moves = state.get_possible_moves(player)
        for move in all_moves:
            next_state = state.apply_next_move(move)
            if (not(next_state)): continue
            # This returns the unrefined score, we need to refine for our own good
            next_eval = self.search(next_state, depth - 1, self.get_next_player(player), heuristic)[0]
            debug("next_eval = ")
            debug(next_eval)
            next_score = [next_eval[-1]]
            debug(next_score)
            next_score.append(next_eval[:len(next_eval) - 1])

            if best_score[0] < next_score[0]:
                best_score = next_score
                best_move = move

        if (best_move != (0,0,0,0)):                                        
            block, point, index, rotations = best_move
            best_move = (index, rotations, point.x, point.y)
        return [best_score, best_move]

    # find_move is your place to start. When it's your turn,
    # find_move will be called and you must return where to go.
    # You must return a tuple (block index, # rotations, x, y)
    def find_move(self):
        return self.search(self, depth=4, player=self.my_number, heuristic=self.simple_evaluation)[1]


    def get_number(self, point):
        return self.grid[point.x][point.y]
    
    def get_neighbors(self, point):
        x, y = point.x, point.y
        N = self.dimension
        neighbors = []
        if (x > 0):
            neighbors.append(Point(x-1, y))
        if (x < N-1):
            neighbors.append(Point(x+1, y))
        if (y > 0):
            neighbors.append(Point(x, y-1))
        if (y < N-1):
            neighbors.append(Point(x, y+1))

        return neighbors

    def bfs(self, point):
        block = set([])
        agenda = [point]
        number = self.get_number(point)
        count = 0
        while len(agenda) > 0:
            for p in agenda:
                block.add(p)
                
            next_agenda = []
            for p in agenda:
                for child in self.get_neighbors(p):
                    if self.get_number(child) == number and not(child in block):
                        next_agenda.append(child)
            agenda = next_agenda
            
        return list(block)
        
    def get_all_current_blocks(self, grid, number):
        visited = set([])
        blocks = []
        for x in range(self.dimension):
            for y in range(self.dimension):
                point = Point(x, y)
                if self.get_number(point) != number:
                    continue
                if point in visited:
                    continue
                block = self.bfs(point)
                blocks.append(block)
                for p in block:
                    visited.add(p)
        return blocks
    

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

    def get_next_move(self, block, point):
        # Get the next move
        # Need to check if this move is legal or not
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
            ):
                return False

            onAbsCorner = onAbsCorner or (p == corner)
            onRelCorner = onRelCorner or (
                (x > 0 and y > 0 and self.grid[x - 1][y - 1] == self.my_number) or
                (x > 0 and y < N and self.grid[x - 1][y + 1] == self.my_number) or
                (x < N and y > 0 and self.grid[x + 1][y - 1] == self.my_number) or
                (x < N and y < N and self.grid[x + 1][y + 1] == self.my_number)
            )

        if self.grid[corner.x][corner.y] < 0 and not onAbsCorner:
            return False
        if not onAbsCorner and not onRelCorner:
            return False

        # Okay, it is legal, let return the next move
        # Get the next player
        next_number = (self.my_number + 1) % 4
        next_turn = (self.turn + 1) % 4
        # grid
        grid = [row[:] for row in self.grid]
        for offset in block:
            p = point + offset
            x = p.x
            y = p.y
            grid[x][y] = self.my_number
            
        # Get blocks
        used_blocks = self.get_all_current_blocks(self.grid, next_number)
        used_hash_blocks = []
        for block in used_blocks:
            used_hash_blocks.append(hash_block(block))
        remain_blocks = []
        for block in BLOCKS:
            if not(hash_block(block) in used_hash_blocks):
                remain_blocks.append(block)
        
        return Game([remain_blocks, grid, self.bonus_squares, next_number, self.dimension, next_turn])
    
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
