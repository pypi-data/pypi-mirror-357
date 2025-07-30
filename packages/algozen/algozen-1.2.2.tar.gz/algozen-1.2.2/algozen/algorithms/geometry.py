"""
Computational geometry algorithms for AlgoZen.

This module provides various geometric algorithms and computations.
"""
from typing import List, Tuple
import math


Point = Tuple[float, float]
Line = Tuple[Point, Point]


def distance(p1: Point, p2: Point) -> float:
    """Calculate Euclidean distance between two points.
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def cross_product(o: Point, a: Point, b: Point) -> float:
    """Calculate cross product of vectors OA and OB.
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def convex_hull_graham(points: List[Point]) -> List[Point]:
    """Find convex hull using Graham scan algorithm.
    
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    if len(points) < 3:
        return points
    
    # Find bottom-most point (or leftmost if tie)
    start = min(points, key=lambda p: (p[1], p[0]))
    
    # Sort points by polar angle with respect to start point
    def polar_angle(p):
        dx, dy = p[0] - start[0], p[1] - start[1]
        return math.atan2(dy, dx)
    
    sorted_points = sorted([p for p in points if p != start], key=polar_angle)
    
    # Graham scan
    hull = [start, sorted_points[0]]
    
    for point in sorted_points[1:]:
        # Remove points that make clockwise turn
        while len(hull) > 1 and cross_product(hull[-2], hull[-1], point) <= 0:
            hull.pop()
        hull.append(point)
    
    return hull


def line_intersection(line1: Line, line2: Line) -> Point:
    """Find intersection point of two lines.
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2
    
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-10:
        raise ValueError("Lines are parallel")
    
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    
    x = x1 + t * (x2 - x1)
    y = y1 + t * (y2 - y1)
    
    return (x, y)


def point_in_polygon(point: Point, polygon: List[Point]) -> bool:
    """Check if point is inside polygon using ray casting.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    x, y = point
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        
        p1x, p1y = p2x, p2y
    
    return inside


def closest_pair_points(points: List[Point]) -> Tuple[Point, Point, float]:
    """Find closest pair of points using divide and conquer.
    
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    def closest_pair_rec(px: List[Point], py: List[Point]) -> Tuple[Point, Point, float]:
        n = len(px)
        
        # Base case for small arrays
        if n <= 3:
            min_dist = float('inf')
            p1, p2 = None, None
            for i in range(n):
                for j in range(i + 1, n):
                    d = distance(px[i], px[j])
                    if d < min_dist:
                        min_dist = d
                        p1, p2 = px[i], px[j]
            return p1, p2, min_dist
        
        # Divide
        mid = n // 2
        midpoint = px[mid]
        
        pyl = [p for p in py if p[0] <= midpoint[0]]
        pyr = [p for p in py if p[0] > midpoint[0]]
        
        # Conquer
        p1_l, p2_l, dl = closest_pair_rec(px[:mid], pyl)
        p1_r, p2_r, dr = closest_pair_rec(px[mid:], pyr)
        
        # Find minimum of the two halves
        if dl <= dr:
            min_dist = dl
            p1, p2 = p1_l, p2_l
        else:
            min_dist = dr
            p1, p2 = p1_r, p2_r
        
        # Check points near the dividing line
        strip = [p for p in py if abs(p[0] - midpoint[0]) < min_dist]
        
        for i in range(len(strip)):
            j = i + 1
            while j < len(strip) and (strip[j][1] - strip[i][1]) < min_dist:
                d = distance(strip[i], strip[j])
                if d < min_dist:
                    min_dist = d
                    p1, p2 = strip[i], strip[j]
                j += 1
        
        return p1, p2, min_dist
    
    if len(points) < 2:
        raise ValueError("Need at least 2 points")
    
    px = sorted(points, key=lambda p: p[0])
    py = sorted(points, key=lambda p: p[1])
    
    return closest_pair_rec(px, py)


def polygon_area(vertices: List[Point]) -> float:
    """Calculate area of polygon using shoelace formula.
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    n = len(vertices)
    if n < 3:
        return 0
    
    area = 0
    for i in range(n):
        j = (i + 1) % n
        area += vertices[i][0] * vertices[j][1]
        area -= vertices[j][0] * vertices[i][1]
    
    return abs(area) / 2


def rotate_point(point: Point, angle: float, center: Point = (0, 0)) -> Point:
    """Rotate point around center by given angle (in radians).
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    # Translate to origin
    x = point[0] - center[0]
    y = point[1] - center[1]
    
    # Rotate
    new_x = x * cos_a - y * sin_a
    new_y = x * sin_a + y * cos_a
    
    # Translate back
    return (new_x + center[0], new_y + center[1])


def line_segment_intersection(seg1: Line, seg2: Line) -> bool:
    """Check if two line segments intersect.
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    def on_segment(p: Point, q: Point, r: Point) -> bool:
        return (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and
                q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1]))
    
    def orientation(p: Point, q: Point, r: Point) -> int:
        val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
        if abs(val) < 1e-10:
            return 0  # Collinear
        return 1 if val > 0 else 2  # Clockwise or Counterclockwise
    
    p1, q1 = seg1
    p2, q2 = seg2
    
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)
    
    # General case
    if o1 != o2 and o3 != o4:
        return True
    
    # Special cases
    if (o1 == 0 and on_segment(p1, p2, q1) or
        o2 == 0 and on_segment(p1, q2, q1) or
        o3 == 0 and on_segment(p2, p1, q2) or
        o4 == 0 and on_segment(p2, q1, q2)):
        return True
    
    return False