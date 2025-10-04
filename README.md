# Telemetry Avionics Subteam - Question 3

This document explains my answer in detail, and how my program solves the problem.

## Intro

A rocket is initially located at (x<sub>0</sub>, y<sub>0</sub>) on a square grid and moves exactly one  unit randomly in a cardinal direction at each time step. A set of ground stations each report how many units away from them the rocket is within (inclusive) at a specific time. Write a program (in any suitable language) that takes the rockets starting position, a list of measurements and an integer k and outputs the number of possible locations for the rocket after k timesteps.

I wanted to ensure that my solution doesn’t search all the possible squares on this grid and then sees which match all criteria, since the plane is infinite and we haven’t been told that the rocket only travels between say (0,0) and (100,100)

## Data Storage

Given a more complex problem like this, I wanted to make a proper way of storing data. All positions, as 2D coordinates will be stored using the tuple type, in the format (x,y).

For the measurement, we need 3 pieces of information - the time it was taken, the maximum distance to the rocket and the position of the measurement station. For ease, this will be stored as a class

```python
class measurement:  
    def __init__(self, pos, time, radius) -> None:  
        self.pos=pos  
        self.time=time  
        self.radius=radius

    def __gt__(self, other) -> None:  
        return other.time > self.time

    def __repr__(self) -> str:  
        return f"m, p={self.pos}, r={self.radius}, t={self.time}"
```

We define an `__gt__` method, overloading the `>` operator so that 2 measurements can be compared. I quickly realised that it would be most efficient to start at the end and work backwards, since the measurement taken latest gives us the most information, so having this comparison allows an easy way of checking which measurement was most recent.

## Bounding Boxes

The way my algorithm works is as follows:

1. For each measurement, create the bounding box, that is all points on the square that the rocket could be in based on that measurement  
2. Repeat this for all the measurements  
3. The points where these bounding boxes all intersect give the possible positions of the rocket

One problem was that the measurements are not taken at the end time we want, but during the flight of the rocket. I overcame this by creating a new value - the effective radius of the measurement. For example:

* A measurement is taken at t=7, with a radius of 2  
* The end time we want in this case is t=10

The effective radius is calculated by the following method:

* Since this measurement, there were 3 more seconds unaccounted for  
* The rocket could’ve moved 1 unit/second further away maximum, assuming it was always heading away from the measurement station  
* So the effective radius is 2 + 3 = 5 units

reffective=rmeasurement+tend-tmeasurement

The next part was to draw the bounding box. Since we cannot move diagonally (the rocket only moves in 1 cardinal direction each time), the pattern looks more like a cross / star shape rather than a true box. However, this gives an advantage that we can calculate the time it takes to get from the centre of the bounding box to any other point on the plane.

To get from (2,3) to (6,5), we must travel a distance of +4 on the x axis and +2 on the y axis, so the total time moving 1 square / second is 4+2 = 6 seconds. This is a minimum time, since that assumes we always move directly between the 2 points. Let’s define a function for this:

```python
def getMinTime(p1: tuple, p2: tuple) -> int:  
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
```

Note that we use `abs()` since going from x=0 to x=-4 takes 4 seconds not -4 seconds.

Looking back at the bounding box pattern:

```python
#    r=0               r=1            r=2            r=3  
# - - - - - - -  - - - - - - -   - - - - - - -  - - - ■ - - -  
# - - - - - - -  - - - - - - -   - - - ■ - - -  - - ■ ■ ■ - -  
# - - - - - - -  - - - ■ - - -   - - ■ ■ ■ - -  - ■ ■ ■ ■ ■ -  
# - - - ■ - - -  - - ■ ■ ■ - -   - ■ ■ ■ ■ ■ -  ■ ■ ■ ■ ■ ■ ■  
# - - - - - - -  - - - ■ - - -   - - ■ ■ ■ - -  - ■ ■ ■ ■ ■ -  
# - - - - - - -  - - - - - - -   - - - ■ - - -  - - ■ ■ ■ - -  
# - - - - - - -  - - - - - - -   - - - - - - -  - - - ■ - - -
```

One thing that I noticed was that for every valid point in the bounding box, getMinTime(centre of bounding box, valid point in bounding box) is always less than or equal to the radius of the bounding box. And the extent of the bounding box is given by centre + radius and centre - radius. So with a finite number of points to check and a way of making sure they are valid, we can define a function that iterates over all of them and finds the bounding box.

## Overlapping

One last thing we need to do is work out how the overlapping will work. It’s not possible to check for overlaps for the first bounding box, since there's nothing to check against. For all other attempts, we will pass in the current solutions, and then reassign the current solutions to the remaining solutions once all the ones that do not overlap have been removed.

This is accomplished by the following method:

* Create a set called “new possible solutions”, and optionally receive one called “current solutions”  
* For every valid point in the bounding box:  
  * If no “current solutions” has been passed:  
    * This must be the first time  
    * Add straight to the new possible solutions  
  * Otherwise, is this solution already in “current solutions”?  
    * If so, this overlaps so add to “new possible solutions”  
    * If not, no overlap so discard this solution  
* Return “new possible solutions”, which will become “current solutions” for the next bounding box

This gives the structure of the function “boundingBox“:

```python
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
```

## Tying it Together

There is one final thing to do - tie all these functions together into 1 called “FindSolutions”. This is a simple function that sorts the measurements by time order (descending), then creates the bounding boxes and overlaps them before returning the final solutions.

```python
def FindSolutions(startPos: tuple, endTime: int, measurements: list[measurement]) -> set[tuple]:  
    measurements.sort()

    measurements.append(measurement(startPos, 0, 0))

    solutions: set[tuple] = boundingBox(measurements[0].pos, measurements[0].radius + endTime-measurements[0].time, None)  
     
    # already handled the first one  
    measurements.remove(measurements[0])

    for m in measurements:  
        solutions = boundingBox(m.pos, m.radius + endTime-m.time, solutions)  
     
    return solutions  
```
