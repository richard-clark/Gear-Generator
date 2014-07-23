Involute Gear Generator
=======================

This is a Python package for generating involute gears&mdash;both within Python and from the command line. Gears can be exported in either DXF or SVG format.

The tooth faces are comprised of polylines, which consist of anumber of points connected by straight lines; thus, the faces are approximations.

Command-Line Usage
------------------

Gears can be generated from the command line. 

The following example will generate a 48-pitch, 32-tooth, 20-degree pressure angle gear and export it as a DXF:

	python gear.py -n 32 -p 48 -a 20 -d gear.dxf
	
The following example will generate a 48-pitch, 24-tooth, 20-degree pressure angle gear with a kerf of 1/100 and a bore of 1/8 and export it as an SVG (scaled by a factor of 500):

	python gear.py -n 24 -p 48 -a 20 -b 0.125 -k 0.01 --svg_scale 500 -s gear.svg

To see all options, use the ``-h`` flag:

	python gear.py -h 

Python Usage
------------

The following example will generate a 48-pitch, 32-tooth, 20-degree pressure angle gear and export it as a DXF:

	import gear

	g = gear.Gear(48, 32, 20)
	geom = g.get_geometry()
	geom.write_dxf('gear.dxf')

The following example will generate a 48-pitch, 24-tooth, 20 degree pressure angle gear with a kerf of 1/100 and a bore of 1/8 and export it as an SVG (scaled by a factor of 500) with a magenta stroke color:

	import gear
	
	svg_scale_factor = 500
		
	g = gear.Gear(48, 24, 20)
	geom = g.get_geometry(kerf = 1/100.0)
	
	style= {'fill': 'transparant', 
		'stroke-width': 0.002, 
		'stroke': 'magenta'}
	
	geom.write_svg('gear.svg', svg_scale_factor, style=style)
	
More examples of Python usage can be found within the ``testing/`` directory.