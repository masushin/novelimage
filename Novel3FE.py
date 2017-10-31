import argparse
import os.path
import xml.etree.ElementTree as ET
import Novel3 as Novel


class NovelElement:

    def __init__(self, element):
        self.element = element
        self.width = int(self.element.attrib["width"])
        self.height = int(self.element.attrib["height"])
        self.margin_up = float(self.element.attrib["margin_up"])
        self.margin_bottom = float(self.element.attrib["margin_bottom"])
        self.margin_left = float(self.element.attrib["margin_left"])
        self.margin_right = float(self.element.attrib["margin_right"])

    @property
    def size(self):
        return (self.width, self.height)

    @property
    def margin(self):
        return (self.margin_up, self.margin_bottom, self.margin_left, self.margin_right)


class ColumnChainElement:

    direction_tbl = {"VERTICAL": Novel.TextAttr.DIRECTION_VERTICAL,
                     "HORIZONTAL": Novel.TextAttr.DIRECTION_HORIZONTAL}

    def __init__(self, element):
        self.element = element
        self.name = self.element.attrib["name"]
        if "font" in self.element.attrib:
            self.font = self.element.attrib["font"]
        else:
            self.font = None            
        self.fontsize = int(self.element.attrib["fontsize"])
        self.direction = self.direction_tbl[self.element.attrib["direction"]]
        self.linespace = float(self.element.attrib["linespace"])
        self.color = self.element.attrib["color"]


class ColumnElement:

    refp_tbl = {"UP_LEFT": Novel.Column.REFP_UP_LEFT,
                "UP_RIGHT": Novel.Column.REFP_UP_RIGHT,
                "BOTTOM_LEFT": Novel.Column.REFP_BOTTOM_LEFT,
                "BOTTOM_RIGHT": Novel.Column.REFP_BOTTOM_RIGHT}

    refl_tbl = {"LIMIT_UP": Novel.Column.REFL_UP_LIMIT,
                "LIMIT_BOTTOM": Novel.Column.REFL_BOTTOM_LIMIT,
                "LIMIT_LEFT": Novel.Column.REFL_LEFT_LIMIT,
                "LIMIT_RIGHT": Novel.Column.REFL_RIGHT_LIMIT,
                "MARGIN_UP": Novel.Column.REFL_UP_MARGIN,
                "MARGIN_BOTTOM": Novel.Column.REFL_BOTTOM_MARGIN,
                "MARGIN_LEFT": Novel.Column.REFL_LEFT_MARGIN,
                "MARGIN_RIGHT": Novel.Column.REFL_RIGHT_MARGIN}

    refs_tbl = {"NOVEL_H": Novel.Column.REFS_NOVEL_H,
                "NOVEL_V": Novel.Column.REFS_NOVEL_V,
                "MARGIN_UP": Novel.Column.REFS_MARGIN_UP,
                "MARGIN_BOTTOM": Novel.Column.REFS_MARGIN_BOTTOM,
                "MARGIN_LEFT": Novel.Column.REFS_MARGIN_LEFT,
                "MARGIN_RIGHT": Novel.Column.REFS_MARGIN_RIGHT,
                "LIVEAREA_H": Novel.Column.REFS_LIVEAREA_H,
                "LIVEAREA_V": Novel.Column.REFS_LIVEAREA_V}

    def separateRefSizeParam(self, param):
        key, _, value = str(param).partition(":")
        return self.refs_tbl[key], float(value)

    def __init__(self, element):
        self.element = element
        self.refp = self.refp_tbl[element.attrib["refp"]]
        self.reflh = self.refl_tbl[element.attrib["reflh"]]
        self.reflv = self.refl_tbl[element.attrib["reflv"]]
        self.offsetx_ref, self.offsetx_val = self.separateRefSizeParam(
            element.attrib["offsetx"])
        self.offsety_ref, self.offsety_val = self.separateRefSizeParam(
            element.attrib["offsety"])
        self.sizew_ref, self.sizew_val = self.separateRefSizeParam(
            element.attrib["sizew"])
        self.sizeh_ref, self.sizeh_val = self.separateRefSizeParam(
            element.attrib["sizeh"])

    @property
    def refline(self):
        return (self.reflh, self.reflv)

    @property
    def offsetx(self):
        return (self.offsetx_ref, self.offsetx_val)

    @property
    def offsety(self):
        return (self.offsety_ref, self.offsety_val)

    @property
    def sizew(self):
        return (self.sizew_ref, self.sizew_val)

    @property
    def sizeh(self):
        return (self.sizeh_ref, self.sizeh_val)


class TextElement:

    def __init__(self, element, basepath):
        self.element = element
        self.columnchain = self.element.attrib["columnchain"]
        self.src = self.element.attrib["src"]
        src_path = os.path.join(basepath, self.src)
        src_file = open(src_path)
        self.text = src_file.read()


def main():
    print("Novel Image Generator.")

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("infile")
    arguments = argument_parser.parse_args()

    infile_abspath = os.path.abspath(arguments.infile)
    infile_path = os.path.dirname(infile_abspath)
    if not os.path.exists(infile_abspath):
        print("{} is not found.".format(infile_abspath))
        return

    print("Infile:{}".format(infile_abspath))

    tree = ET.parse(infile_abspath)
    for element in tree.iter():
        print(element)

    e = tree.getroot()
    if not e.tag == "novel":
        print("Root element must be <novel>.")

    ne = NovelElement(e)
    novel = Novel.Novel(ne.size, ne.margin)

    for cc in e.iter("columnchain"):
        cce = ColumnChainElement(cc)
        columnlist = []

        for c in cc.iter("column"):
            ce = ColumnElement(c)
            columnlist.append(Novel.Column(ce.refp, ce.refline, ce.offsetx,
                                           ce.offsety, ce.sizew, ce.sizeh))

        if cce.font == None:
            textattr = Novel.TextAttr(fontsize=cce.fontsize, direction=cce.direction,
                                      linespace=cce.linespace, color=cce.color)
        else:
            textattr = Novel.TextAttr(font=cce.font, fontsize=cce.fontsize, direction=cce.direction,
                                      linespace=cce.linespace, color=cce.color)
            
        novel.add_columnchain(cce.name, columnlist, textattr)

    for t in e.iter("text"):
        te = TextElement(t, infile_path)
        novel.add_textsource(te.text, te.columnchain)

#    novel.debugDrawColumnLine()
    novel.write()

if __name__ == '__main__':
    main()
