from lxml import etree
import math

from dxfwrite import DXFEngine as dxf

import svg_utils

class Geometry:
    def __init__(self, items = []):
        self.items = items
    
    def get_bounds(self):
        """
        Get the bounding rectangle for the items.
        
        :returns: A bounding rectangle, in the form ``((min_x, min_y), (max_x, max_y))``.
        
        """
        
        if len(self.items) == 0:
            return None
        
        bounds = self.items[0].get_bounds()
        
        for i in range(1, len(self.items)):
            b = self.items[i].get_bounds()
            bounds = ((min(bounds[0][0], b[0][0]), min(bounds[0][1], b[0][1])), (max(bounds[1][0], b[1][0]), max(bounds[1][1], b[1][1])))
            
        return bounds
            
    def get_bounds_and_margin(self, margin_factor=0.2, scale=1):
        """
        Get the width and height of the geometry with a margin specified as a ratio of the dimensions. 
        
        :param margin_factor: The factor by which to multiply the dimensions to yield the margin.
        
        :return: The dimensions of the geometry and the amount by which the geometry must be offset, in the form ``((width, height), (offset_x, offset_y))``.
        
        """
        
        bounds = self.get_bounds()
        
        geom_width = (bounds[1][0] - bounds[0][0])
        geom_height = (bounds[1][1] - bounds[0][1])
        
        margin_x = geom_width * margin_factor / 2
        margin_y = geom_height * margin_factor / 2
        
        width = geom_width + 2 * margin_x
        height = geom_height + 2 * margin_y
        
        x_offset = -bounds[0][0] + margin_x
        y_offset = -bounds[0][1] + margin_y
        
        return ((width*scale, height*scale), (x_offset*scale, y_offset*scale))
        
    def write_dxf(self, file_name, layer='GEOMETRY'):
        """
        Create a DXF.
        
        :param file_name: The name of the DXF file to write.
        :param layer: The name of the layer to which to add the geometry.
        
        """
        
        drawing = dxf.drawing(file_name)
        
        self.append_to_dxf(drawing)
    
        drawing.save()
        
    def append_to_dxf(self, drawing):  
        for g in self.items:
            g.append_to_dxf(drawing)
    
    def write_svg(self, file_name, scale=1, margin_factor=0.2, style={}):
        tree = svg_utils.get_svg_tree()
        root = tree.getroot()
        
        size, offset = self.get_bounds_and_margin(margin_factor, scale)
        
        root.attrib['width'] = str(size[0])
        root.attrib['height'] = str(size[1])
        
        self.append_to_svg(root, scale=scale, offset=offset, style=style)
    
        svg_utils.write_svg(tree, file_name)
    
    def append_to_svg(self, root, scale=1, offset=(0,0), style={}):
        for g in self.items:
            g.append_to_svg(root, offset, scale, style)
    
class Polyline():
    def __init__(self, points):
        self.points = points

    def get_bounds(self):
        
        min_x = self.points[0][0]
        max_x = self.points[0][0]
        
        min_y = self.points[0][1]
        max_y = self.points[0][1]
        
        for i in range(1, len(self.points)):
            if self.points[i][0] < min_x:
                min_x = self.points[i][0]
            elif self.points[i][0] > max_x:
                max_x = self.points[i][0]
                
            if self.points[i][1] < min_y:
                min_y = self.points[i][1]
            elif self.points[i][1] > max_y:
                max_y = self.points[i][1]
            
        return ((min_x, min_y), (max_x, max_y))

    def append_to_svg(self, _n, offset=(0, 0), scale_factor = 1, style = {}):
        n = etree.SubElement(_n, 'path')
        
        d="M{0} {1}".format(self.points[0][0] * scale_factor + offset[0],
                            self.points[0][1] * scale_factor + offset[1])
        
        for i in range(1, len(self.points)):
            d += ' L {0} {1}'.format(self.points[i][0] * scale_factor + offset[0],
                                     self.points[i][1] * scale_factor + offset[1])

        n.attrib['d'] = d
        
        if style.has_key('stroke'):
            n.attrib['stroke'] = style['stroke']
        
        if style.has_key('stroke-width'):
            n.attrib['stroke-width'] = str(style['stroke-width'] * scale_factor)
            
        if style.has_key('fill'):
            n.attrib['fill'] = style['fill']
            
    def append_to_dxf(self, drawing):
        adj_points = []
        for p in self.points:
            adj_points.append((p[0], -p[1]))
        
        drawing.add(dxf.polyline(adj_points))



class Arc():
    def __init__(self, center, radius, start_angle, end_angle):
        self.center = center
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle

    def get_start_point(self):
        start_x = self.center[0] + self.radius * math.cos(self.start_angle)
        start_y = self.center[1] - self.radius * math.sin(self.start_angle)
        return (start_x, start_y)

    def get_end_point(self):
        end_x = self.center[0] + self.radius * math.cos(self.end_angle)
        end_y = self.center[1] - self.radius * math.sin(self.end_angle)
        return (end_x, end_y)

    def get_bounds(self):
        
        start_x, start_y = self.get_start_point()
        end_x, end_y = self.get_end_point()
        
        m1 = math.floor(self.start_angle*2/math.pi)
        m2 = math.floor(self.end_angle*2/math.pi)
    
        min_x = min(start_x, end_x)
        max_x = max(start_x, end_x)
    
        min_y = min(start_y, end_y)
        max_y = max(start_y, end_y)
        
        m = m1 + 1
        while m <= m2:
            if m % 4 == 0:
                max_x = max(max_x, self.center[0] + self.radius)
            elif m % 4 == 3:
                max_y = max(max_y, self.center[1] + self.radius)
            elif m % 4 == 2:
                min_x = min(min_x, self.center[0] - self.radius)
            elif m % 4 == 1:
                min_y = min(min_y, self.center[1] - self.radius)
                  
            m += 1
            
        return ((min_x, min_y), (max_x, max_y))

    def append_to_svg(self, _n, offset=(0, 0), scale_factor = 1, style = {}):
        n = etree.SubElement(_n, 'path')
        
        start_x, start_y = self.get_start_point()
        end_x, end_y = self.get_end_point()
        
        if self.end_angle - self.start_angle >  math.pi:
            flag = '1'
        else:
            flag = '0'
        
        d = "M{0} {1} A {2} {2}, 0, {5}, 0, {3} {4}".format(start_x * scale_factor + offset[0],
                                                          start_y * scale_factor + offset[1],
                                                          self.radius * scale_factor,
                                                          end_x * scale_factor + offset[0],
                                                          end_y * scale_factor + offset[1],
                                                          flag)
        
        n.attrib['d'] = d
        
        if style.has_key('stroke'):
            n.attrib['stroke'] = style['stroke']
        
        if style.has_key('stroke-width'):
            n.attrib['stroke-width'] = str(style['stroke-width'] * scale_factor)
            
        if style.has_key('fill'):
            n.attrib['fill'] = style['fill']
        
    def append_to_dxf(self, drawing):
        drawing.add(dxf.arc(self.radius, (self.center[0], -self.center[1]), self.start_angle * 180 / math.pi, self.end_angle * 180 / math.pi))
        

class Circle():
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
        
    def get_bounds(self):
        return (((self.center[0] - self.radius), (self.center[1] - self.radius)),
                ((self.center[0] + self.radius), (self.center[1] + self.radius)))
        
    def append_to_svg(self, _n, offset = (0, 0), scale_factor = 1, style = {}):
        n = etree.SubElement(_n, 'circle')
        n.attrib['cx'] = str(self.center[0] * scale_factor + offset[0])
        n.attrib['cy'] = str(self.center[1] * scale_factor + offset[1])
        n.attrib['r'] = str(self.radius * scale_factor)
        
        if style.has_key('stroke'):
            n.attrib['stroke'] = style['stroke']
        
        if style.has_key('stroke-width'):
            n.attrib['stroke-width'] = str(style['stroke-width'] * scale_factor)
            
        if style.has_key('fill'):
            n.attrib['fill'] = style['fill']
        
    def append_to_dxf(self, drawing):
        drawing.add(dxf.circle(self.radius, (self.center[0], -self.center[1])))
        
class Rect():
    def __init__(self, origin, dimensions):
        self.origin = origin
        self.dimensions = dimensions
        
    def get_bounds(self):
        x1 = self.origin[0]
        x2 = self.origin[0] + self.dimensions[0]
        
        y1 = self.origin[1]
        y2 = self.origin[1] + self.dimensions[1]
        
        return((min(x1, x2), min(y1, y2)), (max(x1, x2), max(y1, y2)))
        
    def append_to_svg(self, _n, offset = (0, 0), scale_factor = 1, style = {}):
        n = etree.SubElement(_n, 'rect')
        n.attrib['x'] = str(self.origin[0] * scale_factor + offset[0])
        n.attrib['y'] = str(self.origin[1] * scale_factor + offset[1])
        n.attrib['width'] = str(self.dimensions[0] * scale_factor)
        n.attrib['height'] = str(self.dimensions[1] * scale_factor)
        
        if style.has_key('stroke'):
            n.attrib['stroke'] = style['stroke']
        
        if style.has_key('stroke-width'):
            n.attrib['stroke-width'] = str(style['stroke-width'] * scale_factor)
            
        if style.has_key('fill'):
            n.attrib['fill'] = style['fill']
            