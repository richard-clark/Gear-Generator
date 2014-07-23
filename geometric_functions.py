"""
Contains functions for working with lists of points.

Each point is in the form of a tuple:

    (x, y)
"""

import math

def get_rotated_points(points, angle, center = (0, 0)):
    """
    Rotate a list of points around a center point. 
    
    :param points: The input list of points. 
    :param angle: The angle to rotate the points, in radians. 
    :param center: The center point.
    
    :return: The rotated list of points. 
    """
    
    points_out = []
    
    for p in points:
        a = math.atan2(p[1] - center[1], p[0] - center[0])
        r = math.sqrt(math.pow(p[0] - center[0], 2) + math.pow(p[1] - center[1], 2))
        points_out.append((r*math.cos(a+angle), r*math.sin(a+angle)))
    
    return points_out

def get_scaled_points(points, x_scale, y_scale):
    """
    Scale a list of point values.
    
    :param points: The input list of points.
    :param x_scale: The amount to scale the x-components. 
    :param y_scale: The amount to scale the y-components.
    
    :return: The scaled list of points. 
    
    """
    
    points_out = []
    
    for p in points:
        points_out.append((p[0]*x_scale, p[1]*y_scale))
        
    return points_out



def offset_line(points, offset):
    """
    Offet a polyline (a list of points) by a specified amount.
    
    For points which occur at the intersection of two lines (Every point
    except the first and last point), offset the point by the average of the
    normals of the adjoining segments. For the start and end points, offset
    by the normal of the only adjoining segment.
    
    """
    
    # A list of the angles for every line segment
    seg_angles = []
    
    # Iterate over each line segment. Determine its angle and store it
    # in the array. 
    for i in range(0, len(points)-1):
        angle = math.atan2(points[i+1][1] - points[i][1],
                           points[i+1][0] - points[i][0])
        seg_angles.append(angle)
        
    points_out = []
    
    # Offset the start point
    x = points[0][0] + offset * math.cos(seg_angles[0] - math.pi / 2)
    y = points[0][1] + offset * math.sin(seg_angles[0] - math.pi / 2)
    points_out.append((x, y))
    
    # Offset the itermediate points
    for i in range(1, len(points)-1):
        angle_1 = seg_angles[i-1] - math.pi / 2
        angle_2 = seg_angles[i] - math.pi / 2
        
        avg_angle = (angle_1 + angle_2) / 2
        
        x = points[i][0] + offset * math.cos(avg_angle)
        y = points[i][1] + offset * math.sin(avg_angle)
        
        points_out.append((x, y))

    # Offset the end point
    x = points[-1][0] + offset * math.cos(seg_angles[-1] - math.pi / 2)
    y = points[-1][1] + offset * math.sin(seg_angles[-1] - math.pi / 2)
    points_out.append((x, y))
    
    return points_out

def extend_or_trim_start_of_line(points, r):
    """
    Either extend or trim a polyline so that its first point is a distance r from the origin. 
    
    If a point must be added, it will be added along the line between the first and second points.
    
    :param points: The points which comprise the polyline.
    :param r: The target distance from the origin
    """

    # Calculate the distance from the origin to the first point
    r_calc = math.sqrt(math.pow(points[0][0], 2) + math.pow(points[0][1], 2))
    
    # If the calculated value is less than the target distance, an additional
    # point must be added to the list. Otherwise, point(s) must be removed. 
    
    if r_calc < r:
        # Points must be removed from the list. 
        
        # First, find the segments whose radius is larger than the desired radius. 
        for i in range(1, len(points)):
            
            # Calculate the distance from the first point in the segment to the origin.
            r_calc = math.sqrt(math.pow(points[i][0], 2) + math.pow(points[i][1], 2))
    
            if r_calc >= r:
                # The segment which intersects the circle with the desired radius has been found
                
                # The x and y coordinates of the point whose radius is less than r
                x = points[i-1][0]
                y = points[i-1][1]
                
                # The x and y coordinates of the point whose radius is greater than r
                x2 = points[i][0]
                y2 = points[i][1]
                
                # The angle between the two points
                angle = math.atan2(y2 - y, x2 -x)
                
                # Used to simplify the next equation
                A = math.cos(angle)
                B = math.sin(angle)
                
                A2 = math.pow(A, 2)
                B2 = math.pow(B, 2)
                r2 = math.pow(r, 2)

                # Calculate the length of the segment from (x, y) to the point at
                # which the segments intersects the circle of radius r.
                l = -(A*x + B*y - math.sqrt(A2*r2 - A2*math.pow(y,2) 
                                   + 2*A*B*x*y + B2*r2 - B2*math.pow(x,2)))/(A2 + B2)


                # Using the calculated value of l, determine the final x and y coordinates.
                x_new = x + l * math.cos(angle)
                y_new = y + l * math.sin(angle)

                # Add the point to the list (copy the list first)
                points_out = points[i:]
                points_out.insert(0, (x_new, y_new))

                return points_out
    else:
        # An additional point must be added to the list
        raise Exception('Points must be added to the line, but this functionality is not implemented.')

def extend_or_trim_end_of_line(points, r):
    """
    Either extend or trim a polyline so that its last point is a distance specified from the origin. 
    
    If a point must be added, it will be added along the line between the last and second-to-last points.
    
    :param points: The points which comprise the polyline.
    :param r: The target distance from the origin
    
    """
    # Calculate the distance from the origin to the last point
    r_calc = math.sqrt(math.pow(points[-1][0], 2) + math.pow(points[-1][1], 2))
    
    # If the calculated value is less than the target distance, an additional
    # point must be added to the list
    if r_calc <= r:
        # The x and ycoordinates of the last point
        x = points[-1][0]
        y = points[-1][1]
        
        # The angle between the last point and second-to-last point. 
        angle = math.atan2(y - points[-2][1], x - points[-2][0])
        
        # Used to simplify the next equation
        A = math.cos(angle)
        B = math.sin(angle)

        A2 = math.pow(A, 2)
        B2 = math.pow(B, 2)
        r2 = math.pow(r, 2)

        # Calculate the length of the segment from the last point
        # with the specified angle that intersects the circle of radius r.
        l = -(A*x + B*y - math.sqrt(A2*r2 - A2*math.pow(y,2) 
                           + 2*A*B*x*y + B2*r2 - B2*math.pow(x,2)))/(A2 + B2)

        # Using the calculated value of l, determine the final x and y coordinates.
        x_new = x + l * math.cos(angle)
        y_new = y + l * math.sin(angle)

        # Add the point to the list (copy the list first)
        points_out = list(points)
        points_out.append((x_new, y_new))

        return points_out
    else:
        raise Exception('The line must be trimmed, but this functionality is not implemented.')
    
def get_angle_between_points(p1, p2, center = (0, 0)):
    """
    Get the angle between two points with respect to the specified center.
    
    :param p1: The first point. 
    :param p2: The second point.
    :param center: The point to use as the center. 
    
    """
    
    a1 = math.atan2(p1[1] - center[1], p1[0] - center[0])
    a2 = math.atan2(p2[1] - center[1], p2[0] - center[0])
    return a2 - a1