from lxml import etree
import StringIO
    
SVG_TEMPLATE = '<?xml version="1.0" standalone="no"?><svg />'
    
def get_svg_tree(version='1.1', xmlns='http://www.w3.org/2000/svg'):
    """
    Get a basic ElementTree object which represents an SVG. 
    
    :param version: The SVG version attribute. 
    :param xmlns: The SVG xmlns attribute.
    
    :returns: An ElementTree object representing an SVG.
    """
    
    f = StringIO.StringIO(SVG_TEMPLATE)
    tree = etree.parse(f)
    
    svg = tree.getroot()
    svg.attrib['version'] = version
    svg.attrib['xmlns'] = xmlns
    
    return tree
    
def set_dimensions(root, size):
    """
    Set the ``width`` and ``height`` attributes of an SVG root.
    
    :param root: The SVG root ElementTree object.
    :param size: The dimensions to set, in the form ``(width, height)``.
    
    """
    
    root.attrib['width'] = str(size[0])
    root.attrib['height'] = str(size[1])
    
def write_svg(tree, file_name):    
    """
    Write an ElementTree SVG element to the specified file. 
    
    :param tree: The ElementTree object to write. 
    :param file_name: The name of the file to write. 
    
    """

    xml_str = etree.tostring(tree, xml_declaration=True, pretty_print=True)
        
    f = open(file_name, 'w')
    f.write(xml_str);
    f.close()