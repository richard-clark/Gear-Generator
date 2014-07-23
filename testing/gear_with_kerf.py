"""
Generates the same gear with and without kerf.

The gear without kerf is stroked in magenta;
the gear with kerf is stroked in black.

The gear is saved as an SVG named "gear_with_kerf.svg" in the same directory.

"""

import gear
from geometry import svg_utils

# Create a gear
g = gear.Gear(48, 32, 20)
 
# Get the geometry
geom = g.get_geometry(approximation_steps = 5, bore = 0.125)

# Get an SVG tree
tree = svg_utils.get_svg_tree()
root = tree.getroot()
 
# SVG attributes
scale = 500
margin_factor = 0.2
 
size, offset = geom.get_bounds_and_margin(margin_factor, scale)

# Set the size of the SVG
root.attrib['width'] = str(size[0])
root.attrib['height'] = str(size[1])
 
# Draw using a magenta line
style = {'stroke': 'magenta', 
     'stroke-width': 0.002, 
     'fill': 'transparent' }

# Add the geometry to the SVG
geom.append_to_svg(root, scale, offset, style)

# Draw using a black line
style = {'stroke': 'black', 
     'stroke-width': 0.002, 
     'fill': 'transparent' }

# Get the geometry with kerf
geom_2 = g.get_geometry(approximation_steps = 5, bore = 0.125, kerf = 1/128.0)

# Add the geometry to the SVG
geom_2.append_to_svg(root, scale, offset, style)

svg_utils.write_svg(tree, 'gear_with_kerf.svg')