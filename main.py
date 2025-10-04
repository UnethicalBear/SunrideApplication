# YOU CAN READ ABOUT HOW THIS CODE WORKS HERE: https://docs.google.com/document/d/1FO8qN4qwx0Ue3TIYqGPF30waNAQ0ZcPBltJySlZOknI/
# OR HERE: 

# I WOULD REALLY APPRECIATE THIS AS IT EXPLAINS MY ALGORITHM'S DESIGN AND STRUCTURE MUCH BETTER THAN COMMENTS COULD

class measurement:
    def __init__(self, pos:tuple, time:int, radius:int) -> None:
        self.pos=pos
        self.time=time
        self.radius=radius

    def __gt__(self, other) -> bool:
        return other.time > self.time

    def __repr__(self) -> str:
        return f"m, p={self.pos}, r={self.radius}, t={self.time}"

def getMinTime(p1: tuple, p2: tuple) -> int:
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def boundingBox(centre:tuple, radius:int, toCompare) -> set[tuple]:
    out: set[tuple] = set()

    for i in range(centre[0]-radius-1, centre[0]+radius+1):
        for j in range(centre[0]-radius-1, centre[0]+radius+1):

            if getMinTime(centre, (i,j)) <= radius:
                # this is a valid point in the bounding box!
                # but does it overlap with the others?

                if not toCompare:
                    # first time, must assume this is ok
                    out.add((i,j))
                
                elif (i,j) in toCompare:
                        out.add((i,j)) 
    
    return out

def FindSolutions(startPos: tuple, endTime: int, measurements: list[measurement]) -> set[tuple]:
    measurements.sort()

    measurements.append(measurement(startPos, 0, 0))

    solutions: set[tuple] = boundingBox(measurements[0].pos, measurements[0].radius + endTime-measurements[0].time, None)
    
    # already handled the first one
    measurements.remove(measurements[0])

    for m in measurements:
        solutions = boundingBox(m.pos, m.radius + endTime-m.time, solutions)
    
    return solutions

print(f"SOLUTIONS: {FindSolutions(
    (4,5),  # start point
    10,     # end time
    [
        measurement(pos=(2,2),time=4,radius=2),
        measurement(pos=(3,8),time=7,radius=3), 
        measurement(pos=(6,5),time=10,radius=1)
    ]
)}")
