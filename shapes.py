import math

from pysvg.core import BaseElement
from pysvg.structure import defs, svg, g
from pysvg.shape import circle, line, path, rect
from pysvg.text import text
from pysvg.builders import ShapeBuilder, StyleBuilder, TransformBuilder


INKSCAPE_HACK = True # apparently markers tweak backwards in inkscape

# lowest num is lighter
ALPHA = 'none'
GREEN_1 = '#8ae234'
GREEN_2 = '#73d216'
GREEN_3 = '#4e9a06'

RED_3 = '#a40000'

PUR_3 = '#5c3566'

ORANGE_3 = '#ce5c00'
BLACK = '#000000'
ALUM_1 = '#eeeeec'
ALUM_6 = '#2e3436'

HALF = '88'

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

    elems.extend(between(x+75, 0, x+75, 50))
    #cap_elems = triangle(-1,1, 0,3, 1,1, RED_3+HALF)
    if INKSCAPE_HACK:
        cap_elems = triangle(0,1, -2,0, 0,-1, RED_3)
    else:
        cap_elems = triangle(0,1, 2,0, 0,-1, RED_3)
    elems.append(cap_def('RED_3END', cap_elems))
    elems.extend(arc_curve(x+100, 0, x+100, 70, cap_def='RED_3END'))

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


def between(x,y, x2,y2, outie=10, angle=45,
            color=PUR_3, width=4):
    """outie direction is billowing if it were traveling counterclockwise"""
    points = []
    sb = ShapeBuilder()
    points.append('{0},{1}'.format(x,y))
    slope = slope_angle(x,y, x2,y2)
    out_angle = slope + angle
    out_r = out_angle* math.pi/180
    next_x = x+ outie*math.cos(out_r)
    next_y = y - outie*math.sin(out_r)
    points.append('{0},{1}'.format(next_x, next_y))
    slope_r = slope*math.pi/180

    distance = math.sqrt((x2-x)**2 + (y2-y)**2)
    flat_len = distance - 2 * outie*(math.cos(out_r))
    next_x2 = next_x + flat_len*math.cos(slope_r)
    next_y2 = next_y - flat_len*math.sin(slope_r)

    points.append('{0},{1}'.format(next_x2, next_y2))
    points.append('{0},{1}'.format(x2,y2))
    line = sb.createPolyline(points=' '.join(points))
    style = 'fill:{0};stroke-width:{1};stroke:{2};stroke-linecap:round'.format(ALPHA, width, color)
    line.set_style(style)
    return [line]

def marker_end_def(name, color, root_elem):
    """add root_elem as child of svg/defs/marker@id=name"""
    pass


def cap_def(name, children):
    d = defs()
    m = BaseElement('marker')
    m.setAttribute('id', name)
    m.setAttribute('orient', 'auto')
    #m.setAttribute('markerUnits', 'strokeWidth')
    d.addElement(m)
    for c in children:
        m.addElement(c)
    return d

def triangle(x1,y1, x2,y2, x3,y3, fill):
    points = []
    sb = ShapeBuilder()
    for x, y in [(x1,y1), (x2,y2), (x3,y3), (x1, y1)]:
        points.append('{0},{1}'.format(x,y))
    pl = sb.createPolyline(points=' '.join(points))
    style = 'fill:{0}'.format(fill)
    pl.set_style(style)
    return [pl]


def arc_curve(x,y, x2,y2, curve_angle=45, width=10, color=RED_3,
              cap_def=None):
    """clockwise curve.
    Note that you need to create cap_def"""
    p = path(pathData='M {0},{1}'.format(x,y))
    # M is move absolute
    angle = slope_angle(x,y, x2,y2)
    mid_x, mid_y = middle(x,y, x2,y2)
    rx = ry = distance(x,y,x2,y2)
    #p.appendCubicShorthandCurveToPath(x2,y2)
    p.appendArcToPath(rx, ry, x2, y2, relative=False)
    style = 'fill:{0};stroke-width:{1};stroke:{2};stroke-linecap:round'.format(ALPHA, width, color)
    if cap_def:
        p.set_marker_end('url(#{0})'.format(cap_def))
        #style += ';marker-end;url(#{0})'.format(cap_def)
    p.set_style(style)
    return [p]


def revision():
    c = circle(0, 0, 10)
    stroke = RED_3
    style = 'fill:{0};stroke-width:{1};stroke:{2}'.format(stroke, 5, stroke)
    c.set_style(style)
    return [c]

def middle(x1, y1, x2, y2):
    return (x1+x2)/2. , (y1+y2)/2.

def distance(x1, y1, x2, y2):
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)

def slope_angle(x1, y1, x2, y2):
    """
    0 is flat
    45 is pointing down to right
    """
    rise = 1.*(y2-y1)
    run = x2-x1
    slope = None
    if run != 0:
        slope = rise/run
        result = math.atan(slope)*180/math.pi
    elif y2 > y1:
        result = 270
    else:
        result = 90


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
