"""
Tests the functionality of the geometry.primtives classes.
"""

from geometry import primitives, svg_utils
import math

def generate_circles():
    """
    Generate a geometry.primitives.Geometry object with circles of various radii and locations.
    """
    
    # The radii of the circles to generate
    RADII = [5, 10, 25, 50, 100, 250, 500]
    
    # The space between circles, and between the circles and the boundaries of the SVG. 
    MARGIN = 25
    
    # A collection of circle geometry
    geom = primitives.Geometry([])
    
    # A collection of the boundary geometry of each circle
    bounds_geom = primitives.Geometry([])
    
    width = 2 * MARGIN + 2 * RADII[-1]
    x = MARGIN + RADII[-1]
    y = MARGIN
    
    for r in RADII:
        y += r
        
        c = primitives.Circle((x,y), r)
        geom.items.append(c)
        
        bounds = c.get_bounds()
        bounds_geom.items.append(primitives.Rect(bounds[0], (bounds[1][0]-bounds[0][0], bounds[1][1]-bounds[0][1])))
        
        y += r
        y += MARGIN
    
    height = y
    
    tree = svg_utils.get_svg_tree()
    root = tree.getroot()
    
    svg_utils.set_dimensions(root, (width, height))
    
    # Draw using a magenta line
    style = {'stroke': 'magenta', 
         'stroke-width': 1, 
         'fill': 'transparent' }
    
    bounds_geom.append_to_svg(root, style=style)
    
    # Draw using a black line
    style = {'stroke': 'black', 
         'stroke-width': 1, 
         'fill': 'gainsboro' }
    
    geom.append_to_svg(root, style=style)
        
    # Save
    svg_utils.write_svg(tree, 'circles.svg')
    
    # Save as DXF
    geom.write_dxf('circles.dxf')

def generate_polygons():
    MIN_NUM_SIDES = 3
    MAX_NUM_SIDES = 32
    COLS = 5
    RADIUS = 100
    POLYGON_MARGIN = 25
    
    geom = primitives.Geometry([])
    bounds_geom = primitives.Geometry([])
    
    sides = range(MIN_NUM_SIDES, MAX_NUM_SIDES+1)
    
    for h in range(len(sides)):
        row = int(h/COLS)
        col = h%COLS
        
        x = POLYGON_MARGIN + RADIUS + (2*RADIUS + POLYGON_MARGIN)*col
        y = POLYGON_MARGIN + RADIUS + (2*RADIUS + POLYGON_MARGIN)*row
        
        angle = 2*math.pi/sides[h]
        points = []
        for i in range(sides[h]):
            _x = x + RADIUS * math.cos(angle*i)
            _y = y + RADIUS * math.sin(angle*i)
            points.append((_x,_y))
        points.append((points[0][0], points[0][1]))
        line = primitives.Polyline(points)
        geom.items.append(line)
        
        bounds = line.get_bounds()
        bounds_geom.items.append(primitives.Rect(bounds[0], (bounds[1][0]-bounds[0][0], bounds[1][1]-bounds[0][1])))
        
    rows = int(math.ceil(len(sides)/float(COLS)))
        
    width = 2*POLYGON_MARGIN + RADIUS + (2*RADIUS + POLYGON_MARGIN)*COLS
    height = 2*POLYGON_MARGIN + RADIUS + (2*RADIUS + POLYGON_MARGIN)*rows
    
    tree = svg_utils.get_svg_tree()
    root = tree.getroot()
    
    svg_utils.set_dimensions(root, (width, height))
    
    # Draw using a magenta line
    style = {'stroke': 'magenta', 
         'stroke-width': 1, 
         'fill': 'transparent' }
    
    bounds_geom.append_to_svg(root, style=style)
    
    # Draw using a black line
    style = {'stroke': 'black', 
         'stroke-width': 1, 
         'fill': 'gainsboro' }
    
    geom.append_to_svg(root, style=style)
        
    # Save
    svg_utils.write_svg(tree, 'polygons.svg')
    
    # Save as DXF
    geom.write_dxf('polygons.dxf')
    
def generate_arcs():
    RADIUS = 100
    MARGIN = 25
    
    POINT_RADIUS = 5
    
    start_angles = range(0, 360, 45)
    sweep_angles = range(45, 360, 45)
    
    geom = primitives.Geometry([])
    bounds_geom = primitives.Geometry([])
    point_geom = primitives.Geometry([])
    
    for i in range(len(start_angles)):
        for j in range(len(sweep_angles)):
            y = MARGIN + RADIUS + (2 * RADIUS + MARGIN) * i
            x = MARGIN + RADIUS + (2 * RADIUS + MARGIN) * j
            
            start_angle = start_angles[i] * math.pi / 180.0
            end_angle = (start_angles[i] + sweep_angles[j]) * math.pi / 180
            
            a = primitives.Arc((x,y), RADIUS, start_angle, end_angle)
            geom.items.append(a)
            
            point_geom.items.append(primitives.Circle((x, y), POINT_RADIUS))
            point_geom.items.append(primitives.Circle(a.get_start_point(), POINT_RADIUS))
            point_geom.items.append(primitives.Circle(a.get_end_point(), POINT_RADIUS))
            
            bounds = a.get_bounds()
            r = primitives.Rect(bounds[0], (bounds[1][0] - bounds[0][0], bounds[1][1] - bounds[0][1]))
            bounds_geom.items.append(r)
    
    
    width = 2*MARGIN + RADIUS + (2*RADIUS + MARGIN)*len(sweep_angles)
    height = 2*MARGIN + RADIUS + (2*RADIUS + MARGIN)*len(start_angles)
    
    tree = svg_utils.get_svg_tree()
    root = tree.getroot()
    
    svg_utils.set_dimensions(root, (width, height))
    
    # Draw using a magenta line
    style = {'stroke': 'magenta', 
         'stroke-width': 1, 
         'fill': 'transparent' }
    
    bounds_geom.append_to_svg(root, style=style)
    
    # Draw using a black line
    style = {'stroke': 'black', 
         'stroke-width': 2, 
         'fill': 'gainsboro' }
    
    geom.append_to_svg(root, style=style)
        
    # Draw the centers
    style = {'stroke': 'black', 
         'stroke-width': 1, 
         'fill': 'gray' }
    
    point_geom.append_to_svg(root, style=style)
        
    # Save
    svg_utils.write_svg(tree, 'arcs.svg')
    
    # Save as DXF
    geom.write_dxf('arcs.dxf')
    
if __name__ == '__main__':
    generate_arcs()
    generate_circles()
    generate_polygons()