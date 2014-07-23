"""
Contains functionality for generating involute gears.

Gears can be exported in SVG or DXF format.

This module can be invoked from the command line. For help, use

    python gear.py -h
    
See the testing/ directory for examples of using this module.

"""

from geometry import primitives
import math
import geometric_functions

def get_t_value(r, od):
    """
    Get the t value which corresponds to a distance of ``od`` from the origin.
    
    t is defined over the range (0, 1):
    * At t=0, (x,y) = (r,0). 
    * At t=1, (x,y) = (r*pi/2,r).
    
    :param r: The radius of the circle. 
    :param od: The distance from the origin. 
    
    :returns: The corresponding ``t`` value. 
    
    """
    
    return math.sqrt(math.pow(od, 2) / (4*math.pow(r, 2)) - 1) * 2 / math.pi
    
def get_point_for_t(r, t):
    """
    Get the point which corresponds to the value of t along the involute curve.
    
    t is defined over the range (0, 1):
    * At t=0, (x,y) = (r,0). 
    * At t=1, (x,y) = (r*pi/2,r).
    
    :param r: The radius of the circle.
    :param t: The point at which to evaluate the involute. 
    
    :returns: The corresponding point in the form ``(x,y)``. 
    
    """
    
    angle = t*math.pi / 2
    
    x = r*math.cos(angle) + r*angle*math.sin(angle)
    y = r*math.sin(angle) - r*angle*math.cos(angle)
    
    return (x, y)


class Gear:
    DEFAULT_ADDENDUM = 1
    DEFAULT_DEDENDUM = 1.25
    DEFAULT_APPROXIMATION_STEPS = 20
    
    def __init__(self, pitch, teeth, pressure_angle, addendum_factor = DEFAULT_ADDENDUM, dedendum_factor = DEFAULT_DEDENDUM):
        self.pitch = pitch
        self.teeth = teeth
        self.pressure_angle = pressure_angle
        self.addendum_factor = addendum_factor
        self.dedendum_factor = dedendum_factor
        
    def get_pitch_diameter(self):
        """
        Get the pitch diameter of the gear. 
        
        :returns: The pitch diameter.
        """
        
        teeth = float(self.teeth)
        pitch = float(self.pitch)
        
        return teeth / pitch
    
    def get_base_diameter(self):
        """
        Get the base diameter of the gear. 
        
        :returns: The base diameter.
        """
        pressure_angle = float(self.pressure_angle)
        return self.get_pitch_diameter() * math.cos(pressure_angle * math.pi / 180)
    
    def get_outside_diameter(self):
        """
        Get the outside diameter of the gear.
        
        :returns: The outside diameter.
        """
        pitch = float(self.pitch)
        return self.get_pitch_diameter() + 2 * self.addendum_factor / pitch
    
    def get_root_diameter(self):
        """
        Get the root diameter of the gear. 
        
        :returns: The root diameter.
        """
        pitch = float(self.pitch)
        return self.get_base_diameter() - 2 * self.dedendum_factor / pitch
    
    def get_circular_pitch(self):
        """
        Get the circular pitch of the gear. 
        
        :returns: The circular pitch.
        """
        teeth = float(self.teeth)
        return 2 * math.pi / teeth
        
    def get_geometry(self, approximation_steps = DEFAULT_APPROXIMATION_STEPS, kerf = 0, bore = 0):
        """
        Get a geometry.primitives.Geometry object which represents the gear.
        
        :param approximation_steps: The number of steps to use to approximate the involute.
        :param kerf: The amount by which to offset the output gear profile (to account for kerf).
        :param bore: The diameter of the bore of the gear (or 0 for no bore).
        
        :returns: A geometry.primitives.Geometry objects which represents the gear.
        """
        
        # Ensure that teeth is a floating point value so that all division operations are floating point
        teeth = float(self.teeth)
        
        # Get the derived properties of the gear
        base_diameter = self.get_base_diameter()
        outside_diameter = self.get_outside_diameter()
        root_diameter = self.get_root_diameter()
        pitch_diameter = self.get_pitch_diameter()
        circular_pitch = self.get_circular_pitch()
        
        # The base radius
        r = base_diameter / 2
        
        # Get the value of t for the point at which the involute intersects
        # the outside diameter.
        t_od = get_t_value(r, outside_diameter)
        
        # Given the specified number of points at which to approximate the involute,
        # determine the amount by which t should be incremented for each step
        step_inc = t_od / approximation_steps
        
        # An array to hold the approximation point values
        vals = []
        
        # Add the value of the approximation at the intersection of the root circle
        vals.append((root_diameter / 2, 0))
        
        # Populate the list of values
        for i in range(approximation_steps+1):
            vals.append(get_point_for_t(r, i * step_inc))
            
        # Get the position of the pinch point
        t = get_t_value(r, pitch_diameter)
        p = get_point_for_t(r, t)
        a_t = math.atan2(p[1], p[0])
        
        # Determine the angle to which the pinch point should be rotated so that
        # the circular pitch is correct
        rot_angle = (2*math.pi) / teeth / 4 - a_t
        
        # Rotate the list of values to the appropriate point for the first tooth
        vals = geometric_functions.get_rotated_points(vals, rot_angle)
            
        # Mirror the points about the y axis
        vals_2 = geometric_functions.get_scaled_points(vals, 1, -1)
        
        # calculate the angle between the top of the edges of the teet
        t = get_t_value(r, outside_diameter)
        p = get_point_for_t(r, t_od)
        a_t_2 = math.atan2(p[1], p[0])
        
        top_rot_angle = (circular_pitch - 2 * a_t_2 - 2 * rot_angle) / 2
        
        # Offset the points by the specified kerf
        if kerf != 0:
            vals_os = geometric_functions.offset_line(vals, kerf)
            
            # Extend or trim the line so that the ends are the appropriate
            # distance from the center
            vals_os = geometric_functions.extend_or_trim_end_of_line(vals_os, outside_diameter / 2 + kerf)
            vals_os = geometric_functions.extend_or_trim_start_of_line(vals_os, root_diameter / 2 + kerf)
            
            # Mirror the points about the x-axis
            vals_2_os = geometric_functions.get_scaled_points(vals_os, 1, -1)
            
            # Update the angles
            rot_angle_os = rot_angle + geometric_functions.get_angle_between_points(vals[0], vals_os[0])
            top_rot_angle_os = (circular_pitch - 2 * math.atan2(vals_os[-1][1], vals_os[-1][0])) / 2
        else:
            # The geometry will not be offset
            vals_os = vals
            vals_2_os = vals_2
            rot_angle_os = rot_angle
            top_rot_angle_os = top_rot_angle
            
        # Create a list for the geometry
        geom = primitives.Geometry([])
        
        # Add the tooth geometry
        for i in range(self.teeth):
            # Draw two edges per tooth
            vals_os_rot = geometric_functions.get_rotated_points(vals_os, i*circular_pitch)
            geom.items.append(primitives.Polyline(vals_os_rot))
            
            vals_os_rot = geometric_functions.get_rotated_points(vals_2_os, i*circular_pitch)
            geom.items.append(primitives.Polyline(vals_os_rot))
            
            # Draw two arcs per tooth
            # Inner arc
            a = i * circular_pitch
            geom.items.append(primitives.Arc((0, 0),
                                root_diameter / 2 + kerf,
                                a - rot_angle_os,
                                a + rot_angle_os))
            
            # Outer arc
            geom.items.append(primitives.Arc((0, 0),
                                outside_diameter / 2 + kerf,
                                a + circular_pitch / 2 - top_rot_angle_os,
                                a + circular_pitch / 2 + top_rot_angle_os))
            
        # Draw the bore
        if bore > 0:
            geom.items.append(primitives.Circle((0, 0),
                                   bore / 2 - kerf))
            
        return geom

def _positive_int(raw_val):
    """
    Parse the input value and ensure that it is a positive integer.
    
    :param raw_val: The input value.
    :raises: An Exception if the input value is not an integer or is not positive.
    :returns: A positive integer.
    
    """
    
    try:
        val = int(raw_val)
    except:
        raise Exception('Expecting an integer value; got {0}'.format(raw_val))
    
    if val <= 0:
        raise Exception('Expecting a positive integer value; got {0}'.format(raw_val))
    
    return val

def _positive_float(raw_val):
    """
    Parse the input value and ensure that it is a positive float.
    
    :param raw_val: The input value.
    :raises: An Exception if the input value is not a float or is not positive.
    :returns: A positive float.
    
    """
    
    try:
        val = float(raw_val)
    except:
        raise Exception('Expecting a float value; got {0}'.format(raw_val))
    
    if val <= 0:
        raise Exception('Expecting a positive float value; got {0}'.format(raw_val))
    
    return val

import argparse
import sys

def run_with_args(input_args):
    parser = argparse.ArgumentParser(description='Generate involute gears.')
    parser.add_argument('-n', type=_positive_int, required=True, help='The number of teeth.')
    parser.add_argument('-p', type=_positive_int, required=True, help='The pitch.')
    parser.add_argument('-a', type=_positive_float, required=True, help='The pressure angle.')
    parser.add_argument('-b', type=_positive_float, default=None, help='The center bore.')
    parser.add_argument('-k', type=float, default=0, help='The amount of kerf.')
    parser.add_argument('--addendum', type=_positive_float, default=Gear.DEFAULT_ADDENDUM, help='The addendum factor.')
    parser.add_argument('--dedendum', type=_positive_float, default=Gear.DEFAULT_DEDENDUM, help='The dedendum factor.')
    parser.add_argument('-r', type=_positive_int, default=Gear.DEFAULT_APPROXIMATION_STEPS, help='The number of steps to use to approximate the involute.')
    parser.add_argument('-s', type=str, help='The SVG file to output.')
    parser.add_argument('--svg_scale', type=_positive_float, default=1, help='The amount by which to scale the SVG output.')
    parser.add_argument('-d', type=str, help='The DXF file to output.')
    args = parser.parse_args(input_args)
    
    # Make sure at least one output file was specified
    if args.s == None and args.d == None:
        raise Exception('No output file specified (use the -s or -d flags).')
    
    g = Gear(args.p, args.n, args.a, args.addendum, args.dedendum)
    
    geom = g.get_geometry(args.r, args.k, args.b)
    
    # Generate an SVG
    if args.s != None:
        # Draw using a black line
        style = {'stroke': 'black', 
             'stroke-width': 0.002, 
             'fill': 'transparent' }
        
        geom.write_svg(args.s, args.svg_scale, style=style)
    
    # Generate a DXF
    if args.d != None:
        geom.write_dxf(args.d)

if __name__ == '__main__':
    run_with_args(sys.argv)