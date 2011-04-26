import math

from pysvg.structure import svg, g
from pysvg.shape import circle, line, rect
from pysvg.text import text
from pysvg.builders import ShapeBuilder, StyleBuilder, TransformBuilder

# lowest num is lighter
GREEN_1 = '#8ae234'
GREEN_2 = '#73d216'
GREEN_3 = '#4e9a06'

RED_3 = '#a40000'

ORANGE_3 = '#ce5c00'
BLACK = '#000000'
ALUM_1 = '#eeeeec'
ALUM_6 = '#2e3436'


def branch_section():
    x = 0
    y = 0
    elems = rev_path(x, y, x+25, y)
    # down to right
    elems.extend(rev_path(x+25, y, x+75, y+50, "fixme"))
    # up to right
    elems.extend(rev_path(x+75, y+50, x+125, y, ""))
    # across
    elems.extend(rev_path(x+25, y, x+125, y, "master"))

    elems.append(translate(revision(), x+25, y))
    elems.append(translate(revision(), x+75, y+50))
    elems.append(translate(revision(), x+125, y))

    # small numbers
    elems.append(translate(num('1', GREEN_3), x+15, y+10))
    elems.append(translate(num('2', GREEN_3), x+35, y+30))
    elems.append(translate(num('3', GREEN_3), x+50, y+45))

    # large numbers
    elems.append(translate(command('1', 
                                   'git checkout -t fixme',
                                   'use -t to set up remote tracking',
                                   GREEN_3),
                           x, y+70))
    elems.append(translate(command('2', 
                                   '',
                                   'edit file',
                                   GREEN_3),
                           x, y+110))
    elems.append(translate(command('3', 
                                   'git commit -m \'fix bug\' file.py',
                                   '',
                                   GREEN_3),
                           x, y+150))
    elems.append(translate(command('4',
                                   'git diff fixme master -- file.py',
                                   '',
                                   GREEN_3),
                           x, y+190))

    return elems
    

def diff(spikes=9, radius=10):
    points = []
    sb = ShapeBuilder()
    
    for i, angle in enumerate(xrange(0, 360+1, float(180)/spikes)):
        if i % 2 == 0:
            r = radius * .8
        else:
            r = radius
        radians = angle * math.pi/180
        coord = '{0},{1}'.format(r*math.cos(radians),
                                 r*math.sin(radians))
        print "ANGLE", angle, "COOR", coord, "RAD", radians
        points.append(coord)
    print "POINTS", points
    line = sb.createPolyline(points=' '.join(points))
    fill = BLACK
    stroke = ORANGE_3
    style = 'fill:{0};stroke-width:{1};stroke:{2}'.format(fill, 2, stroke)
    line.set_style(style)
    return [line]

def revision():
    c = circle(0, 0, 10)
    stroke = RED_3
    style = 'fill:{0};stroke-width:{1};stroke:{2}'.format(stroke, 5, stroke)
    c.set_style(style)
    return [c]

def middle(x1, y1, x2, y2):
    return (x1+x2)/2. , (y1+y2)/2.

def slope_angle(x1, y1, x2, y2):
    """
    0 is flat
    45 is pointing down to right
    """
    rise = 1.*(y2-y1)
    run = x2-x1
    slope = rise/run

    result = math.atan(slope)*180/math.pi
    print "ROTATE", result, rise, run, slope
    return result

def command(num_txt, cmd, explanation, color):
    x = 0
    y = 0
    elems = [scale(num(num_txt, color), 2)]
    cmd_txt = text(cmd, x+40, y+12)
    s = StyleBuilder()
    s.setFontWeight('bold')
    s.setFontFamily('Bitstream Vera Sans Mono')
    cmd_txt.set_style(s.getStyle())
    elems.append(cmd_txt)

    exp_txt = text(explanation, x+45, y+27)
    s = StyleBuilder()
    #s.setFontWeight('bold')
    s.setFontFamily('Bitstream Vera Serif')
    s.setFontSize('10px')
    exp_txt.set_style(s.getStyle())
    elems.append(exp_txt)
    return elems

def num(txt, color):
    txt = str(txt)
    elems = []
    r = rect(0, 0, 16, 16)
    s = StyleBuilder()
    s.setFilling(color)
    r.set_style(s.getStyle())
    elems.append(r)
    if txt:
        style2 = StyleBuilder()
        #style2.setFontFamily('envy code r')
        style2.setFontFamily('arial')
        style2.setFontWeight('bold')
        style2.setFilling(ALUM_1)
        # shift text left and up by a bit
        if len(txt) == 1:
            x = 5
        elif len(txt) == 2:
            x = 1.5
        t = text(txt, x, 12.5)
        t.set_style(style2.getStyle())
        elems.append(t)
    return elems
    
    
    

def rev_path(x1,y1, x2,y2, txt=None):
    elements = []
    # x1, y1 = r1.get_cx(), r1.get_cy()
    # x2, y2 = r2.get_cx(), r2.get_cy(),
    l = line(x1, y1,
             x2, y2)
    elements.append(l)
    style = 'stroke-width:{0};stroke:{1}'.format(16, ALUM_6)
    l.set_style(style)
    if txt:
        x, y = middle(x1, y1, x2, y2)
        style2 = StyleBuilder()
        #style2.setFontFamily('envy code r')
        style2.setFontFamily('arial')
        style2.setFontWeight('bold')
        style2.setFilling(ALUM_1)
        # shift text left and up by a bit
        # whole alphabet in this font is 167 px width
        per_char = 167./26
        t = text(txt, -len(txt)/2*per_char, 4)
        t.set_style(style2.getStyle())
        
        #import pdb; pdb.set_trace()
        group = rotate([t], slope_angle(x1, y1, x2, y2))
        group = translate([group], x, y)
        elements.append(group)


    return elements

def translate(elems, x, y):
    group = g()
    for e in elems:
        group.addElement(e)
    tb = TransformBuilder()
    #tb.setRotation(rotate(x1, y1, x2, y2))
    tb.setTranslation('{0},{1}'.format(x,y))
    group.set_transform(tb.getTransform())
    return group

def scale(elems, amount):
    """1 = 100%"""
    group = g()
    for e in elems:
        group.addElement(e)
    tb = TransformBuilder()
    #tb.setRotation(rotate(x1, y1, x2, y2))
    tb.setScaling(amount, amount)
    group.set_transform(tb.getTransform())
    return group

def rotate(elems, angle):
    group = g()
    for e in elems:
        group.addElement(e)
    tb = TransformBuilder()
    #tb.setRotation(rotate(x1, y1, x2, y2))
    tb.setRotation(angle)
    #tb.setTranslation('{0},{1}'.format(x,y))
    group.set_transform(tb.getTransform())
    return group

def test2():
    fout = svg('test')
    r1 = revision()
    r2 = revision()
    # import pdb; pdb.set_trace()
    r2.set_cx(100)
    r2.set_cy(200)
    elems = rev_path(r1.get_cx(), r1.get_cy(),
                     r2.get_cx(), r2.get_cy(),
                     "first")
    for e in elems:
        fout.addElement(e)
    fout.addElement(r1)
    fout.addElement(r2)
    r3 = revision()
    r3.set_cx(200)
    r3.set_cy(50)
    for e in rev_path(r1.get_cx(), r1.get_cy(),
                     r3.get_cx(), r3.get_cy(),
                     "second"):
        fout.addElement(e)
    fout.addElement(r3)
    n = translate(num("4", GREEN_3), 50, 40)
    fout.addElement(n)
    n = scale([translate(num("11", GREEN_1), 50, 40)], 2)
    fout.addElement(n)
    fout.save('/tmp/test.svg')


def test():
    fout = svg()
    fout.addElement(translate(diff(), 120, 60))
    for elem in branch_section():
        fout.addElement(elem)
    fout.save('/tmp/git.svg')
    


if __name__ == '__main__':
    test()
