"""
The simplest example of genearting a gear and exporting it in SVG and DXF formats.

The outputs are saved in the same dictory as "basic_gear.svg" and "basic_gear.dxf".

"""

import gear

# Create a gear
g = gear.Gear(48, 32, 20)
 
# Get the geometry
geom = g.get_geometry(bore = 0.125)

# Save the DXF
geom.write_dxf('basic_gear.dxf')

# Save the SVG
# ------------

# SVG attributes
scale = 500
margin_factor = 0.2
 
# Draw using a black line
style = {'stroke': 'black', 
     'stroke-width': 0.002, 
     'fill': 'transparent' }

# Add the geometry to the SVG
geom.write_svg('basic_gear.svg', scale, style=style)