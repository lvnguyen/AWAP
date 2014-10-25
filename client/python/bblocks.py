BLOCKS_POINTS = [

    [[0, 0]],                                                                                                                                                                           

    [[0, 0], [0, 1]],                                                                                                                                                            

    [[0, 0], [0, 1], [1, 0]],                                                                                                                                                       

    [[0, 0], [0, 1], [0, 2]],                                                                                                                                                       

    [[0, 0], [0, 1], [1, 0], [1, 1]],                                                                                                                                                  

    [[0, 0], [1, 0], [2, 0], [1, 1]],                                                                                                                                                 

    [[0, 0], [1, 0], [2, 0], [3, 0]],                                                                                                                                            

    [[0, 0], [0, 1], [1, 0], [0, 2]],                                                                                                                                                 

    [[0, 0], [1, 0], [1, 1], [2, 1]],                                                                                                                                                 

    [[0, 0], [1, 0], [2, 0], [3, 0], [0, 1]],                                                                                                                                           

    [[0, 0], [1, 0], [2, 0], [1, 1], [1, 2]],                                                                                                                                           

    [[0, 0], [1, 0], [2, 0], [0, 1], [0, 2]],                                                                                                                                     

    [[0, 0], [1, 0], [1, 1], [2, 1], [3, 1]],                                                                                                                                      

    [[0, 0], [0, 1], [1, 1], [2, 1], [2, 2]],                                                                                                                                          

    [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0]],                                                                                                                                     

    [[0, 0], [1, 0], [0, 1], [1, 1], [0, 2]],                                                                                                                                            

    [[0, 0], [1, 0], [1, 1], [2, 1], [2, 2]],                                                                                                                                        

    [[0, 0], [1, 0], [0, 1], [0, 2], [1, 2]],                                                                                                                                  

    [[0, 0], [1, 0], [1, 1], [1, 2], [2, 1]],                                                                                                                                 

    [[0, 0], [-1, 0], [0, -1], [1, 0], [0, 1]],                                                                                                                                 

    [[0, 0], [1, 0], [2, 0], [3, 0], [1, 1]]

];

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

    def __hash__(self):
        return self.x*100 + self.y

    def __str__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

    # rotates 90deg counterclockwise
    def rotate(self, num_rotations):
        if num_rotations == 1: return Point(-self.y, self.x)
        if num_rotations == 2: return Point(-self.x, -self.y)
        if num_rotations == 3: return Point(self.y, -self.x)
        return self

    def distance(self, point):
        return abs(point.x - self.x) + abs(point.y - self.y)

    
BLOCKS = []
for b in BLOCKS_POINTS:
    t = []
    for p in b:
        t.append(Point(p[0], p[1]))
    BLOCKS.append(t)
def hash_block(block):
    sum_x = 0
    sum_y = 0
    s = 0
    for offset in block:
        sum_x += offset.x
        sum_y += offset.y
    k = len(block)
    for offset in block:
        x = (sum_x - k*offset.x)
        y = (sum_y - k*offset.y)
        s += x*x*x*x + y*y*y*y
    return s

S = {}
for index, block in enumerate(BLOCKS):
    S[hash_block(block)] = index
    

