from html.parser import HTMLParser
from PIL import ImageFont, ImageDraw, Image


GLOBAL_DEBUG_FLAG = True


class TextAttr:
    # Font type
    FONT_DEFAULT = 0

    # Direction of writing text
    DIRECTION_HORIZONTAL = 0
    DIRECTION_VERTICAL = 1

    # Align for text
    ALIGN_CENTER = 0
    ALIGN_UP = 1
    ALIGN_BOTTOM = 2
    ALIGN_RIGHT = 3
    ALIGN_LEFT = 4

    def __init__(self, font="GenEiAntiqueN-Medium.otf", fontsize=16, direction=DIRECTION_VERTICAL,
                 valign=ALIGN_UP, halign=ALIGN_RIGHT, linespace=1.8,
                 color="#000000", rubysize=0.6):
        self.font = font
        self.fontsize = fontsize
        self.fontcolor = color
        self.direction = direction
        self.align = {"v": valign, "h": halign}
        self.linespace = linespace
        self.rubysize = rubysize


class Column:
    # Reference point for constraint
    REFP_UP_LEFT = 1
    REFP_UP_RIGHT = 2
    REFP_BOTTOM_LEFT = 3
    REFP_BOTTOM_RIGHT = 4

    # Reference line for constraint
    REFL_UP_LIMIT = 1
    REFL_BOTTOM_LIMIT = 2
    REFL_RIGHT_LIMIT = 3
    REFL_LEFT_LIMIT = 4
    REFL_UP_MARGIN = 5
    REFL_BOTTOM_MARGIN = 6
    REFL_LEFT_MARGIN = 7
    REFL_RIGHT_MARGIN = 8

    # Reference size for constraint
    REFS_NOVEL_H = 1
    REFS_NOVEL_V = 2
    REFS_MARGIN_UP = 3
    REFS_MARGIN_BOTTOM = 4
    REFS_MARGIN_LEFT = 5
    REFS_MARGIN_RIGHT = 6
    REFS_LIVEAREA_H = 7
    REFS_LIVEAREA_V = 8

    def __init__(self, refpoint=REFP_UP_LEFT,
                 refline=(REFL_LEFT_MARGIN, REFL_UP_MARGIN),
                 offsetx=(REFS_LIVEAREA_H, 0), offsety=(REFS_LIVEAREA_V, 0),
                 sizew=(REFS_LIVEAREA_H, 1.0), sizeh=(REFS_LIVEAREA_V, 1.0)):
        self.refpoint = refpoint
        self.refline = {"H": refline[0], "V": refline[1]}
        self.offset = {"x": {"refs": offsetx[0], "mag": offsetx[1]},
                       "y": {"refs": offsety[0], "mag": offsety[1]}}
        self.size = {"w": {"refs": sizew[0], "mag": sizew[1]},
                     "h": {"refs": sizeh[0], "mag": sizeh[1]}}

        print("Column:",self.refpoint,self.refline,self.offset,self.size)

    def get_columnarea(self, layout):
        novel = {"x": 0, "y": 0, "w": layout.w, "h": layout.h}
        margin = {"up": layout.margin_up,
                  "bottom": layout.margin_bottom,
                  "left": layout.margin_left,
                  "right": layout.margin_right}

        offset = {}
        if self.offset["x"]["refs"] == self.REFS_LIVEAREA_H:
            offset["x"] = self.offset["x"]["mag"] * layout.livearea_w
        elif self.offset["x"]["refs"] == self.REFS_NOVEL_H:
            offset["x"] = self.offset["x"]["mag"] * layout.w

        if self.offset["y"]["refs"] == self.REFS_LIVEAREA_V:
            offset["y"] = self.offset["y"]["mag"] * layout.livearea_h
        elif self.offset["y"]["refs"] == self.REFS_NOVEL_V:
            offset["y"] = self.offset["y"]["mag"] * layout.h

        if self.size["w"]["refs"] == self.REFS_NOVEL_H:
            w = int(novel["w"] * self.size["w"]["mag"])
        elif self.size["w"]["refs"] == self.REFS_LIVEAREA_H:
            w = int((novel["w"] - margin["left"] -
                     margin["right"]) * self.size["w"]["mag"])
        elif self.size["w"]["refs"] == self.REFS_MARGIN_LEFT:
            w = int(margin["left"] * self.size["w"]["mag"])
        elif self.size["w"]["refs"] == self.REFS_MARGIN_RIGHT:
            w = int(margin["right"] * self.size["w"]["mag"])

        if self.size["h"]["refs"] == self.REFS_NOVEL_V:
            h = int(novel["h"] * self.size["h"]["mag"])
        elif self.size["h"]["refs"] == self.REFS_LIVEAREA_V:
            h = int((novel["h"] - margin["up"] - margin["bottom"])
                    * self.size["h"]["mag"])
        elif self.size["h"]["refs"] == self.REFS_MARGIN_UP:
            h = int(margin["up"] * self.size["h"]["mag"])
        elif self.size["h"]["refs"] == self.REFS_MARGIN_BOTTOM:
            h = int(margin["bottom"] * self.size["h"]["mag"])

        if self.refline["H"] == self.REFL_LEFT_LIMIT:
            x = novel["x"] + offset["x"]
        elif self.refline["H"] == self.REFL_LEFT_MARGIN:
            x = novel["x"] + margin["left"] + offset["x"]
        elif self.refline["H"] == self.REFL_RIGHT_LIMIT:
            x = novel["x"] + novel["w"] - 1 + offset["x"]
        elif self.refline["H"] == self.REFL_RIGHT_MARGIN:
            x = novel["x"] + novel["w"] - margin["right"] - 1 + offset["x"]

        if self.refline["V"] == self.REFL_UP_LIMIT:
            y = novel["y"] + offset["y"]
        elif self.refline["V"] == self.REFL_UP_MARGIN:
            y = novel["y"] + margin["up"] + offset["y"]
        elif self.refline["V"] == self.REFL_BOTTOM_LIMIT:
            y = novel["y"] + novel["h"] - 1 + offset["y"]
        elif self.refline["V"] == self.REFL_BOTTOM_MARGIN:
            y = novel["y"] + novel["h"] - margin["bottom"] - 1 + offset["y"]

        if self.refpoint == self.REFP_UP_RIGHT or self.refpoint == self.REFP_BOTTOM_RIGHT:
            x = x - w - 1

        if self.refpoint == self.REFP_BOTTOM_LEFT or self.refpoint == self.REFP_BOTTOM_RIGHT:
            y = y - h - 1

        return (x, y, w, h)

class TextCursorBasement():

    prohibition_letter = "、。「」『』"

    def __init__(self, columnarea, textattr, pilimage):
        self.area = columnarea
        self.textattr = textattr
        self.pilimage = pilimage
        self.is_started = False
        self.position_x = 0
        self.position_y = 0
        self.step_offset = 0 

    def get_position(self):
        return self.position_x, self.position_y

    def _is_protruded(self):
        pass

    def write_letter(self, letter):
        pass

    def _reset_cursor(self):
        pass

    def _next_position(self):
        pass

    def _new_line(self):
        pass


class TextCursorVertical(TextCursorBasement):
    def _reset_cursor(self):
        self.position_x = self.area[0]+self.area[2]-(self.textattr.fontsize/2)
        self.position_x -= self.textattr.fontsize * self.textattr.rubysize
        self.position_y = self.area[1]

    def _next_position(self,letter):
        if self.is_started is False:
            self._reset_cursor()
            self.is_started = True
        else:
            self.position_y += self.textattr.fontsize + self.step_offset

        if self._is_protruded() and not letter in list(self.prohibition_letter):
            if self._new_line() == False:
                return False

        if letter == "\n":
            if self._new_line() == False:
                return False

        return True

    def _new_line(self):
        self.position_x -= self.textattr.fontsize * self.textattr.linespace
        self.position_y = self.area[1]

        if self._is_protruded():
            return False
        return True

    def _is_protruded(self):
        if (self.position_x - (self.textattr.fontsize/2)) < self.area[0]:
            return True

        if (self.position_y + (self.textattr.fontsize/2)) > (self.area[1]+self.area[3]):
            return True

        return False

    def write_letter(self, letter):
        if self._next_position(letter) is False:
            return False

        if letter=="\n":
            return True

        letter_x = self.position_x - (self.textattr.fontsize/2)
        letter_y = self.position_y

        draw = ImageDraw.Draw(self.pilimage)
        font = ImageFont.truetype(self.textattr.font, self.textattr.fontsize,encoding="unic", layout_engine=ImageFont.LAYOUT_RAQM)
        draw.text((letter_x, letter_y), letter, font=font, fill=(0,0,0))

class TextCursorHorizontal(TextCursorBasement):
    def _reset_cursor(self):
        self.position_x = self.area[0]
        self.position_y = self.area[1]+(self.textattr.fontsize/2)
        self.position_y += self.textattr.fontsize * self.textattr.rubysize

    def _next_position(self,letter):
        if self.is_started is False:
            self._reset_cursor()
            self.is_started = True
        else:
            self.position_x += self.textattr.fontsize + self.step_offset

        if self._is_protruded() and not letter in list(self.prohibition_letter):
            if self._new_line() == False:
                return False

        if letter == "\n":
            if self._new_line() == False:
                return False

        return True

    def _new_line(self):
        self.position_x = self.area[0]
        self.position_y += self.textattr.fontsize * self.textattr.linespace

        if self._is_protruded():
            return False
        return True

    def _is_protruded(self):
        if (self.position_x - (self.textattr.fontsize/2)) > self.area[0]+self.area[2]:
            return True

        if (self.position_y + (self.textattr.fontsize/2)) > (self.area[1]+self.area[3]):
            return True

        return False

    def write_letter(self, letter):
        if self._next_position(letter) is False:
            return False

        if letter=="\n":
            return True

        letter_x = self.position_x
        letter_y = self.position_y - (self.textattr.fontsize/2)
        draw = ImageDraw.Draw(self.pilimage)
        font = ImageFont.truetype(self.textattr.font, self.textattr.fontsize, encoding="unic")
        draw.text((letter_x, letter_y), letter, font=font, fill="#000020")


class TextCursor():
    def __init__(self, columnarea, textattr, pilimage):
        if textattr.direction == TextAttr.DIRECTION_HORIZONTAL:
            self.cursor = TextCursorHorizontal(columnarea,textattr, pilimage)
        elif textattr.direction == TextAttr.DIRECTION_VERTICAL:
            self.cursor = TextCursorVertical(columnarea,textattr, pilimage)
        self.cursor._reset_cursor()

    def write_letter(self, letter):
        return self.cursor.write_letter(letter)



class TextPart():
    PLAIN = 0
    RUBY = 1
    DOT = 2

    def __init__(self, mode, text, value=None):
        self.mode = mode
        self.text = text
        self.value = value

    def set_text(self, text):
        self.text = text
        print(text)

    def write(self,cursor):
        for letter in list(self.text)[:]:
            cursor.write_letter(letter)


class Text(HTMLParser):
    def __init__(self,source):
        super().__init__()
        self.source = source
        self.parts = []
        self.part_mode = TextPart.PLAIN
        print(source)
        self.feed(self.source)

    def handle_starttag(self, tag, attrs):
        if tag in ["ruby","r"]:
            self.part_mode = TextPart.RUBY
            self.parts.append(TextPart(TextPart.RUBY, None, attrs[0][1]))
        if tag in ["dot","d"]:
            self.part_mode = TextPart.DOT
            if len(attrs) is not 0:
                self.parts.append(TextPart(TextPart.RUBY, None, attrs[0][1]))
            else:
                self.parts.append(TextPart(TextPart.RUBY, None))

    def handle_endtag(self, tag):
        if tag in ["ruby","dot","r","d"]:
            self.part_mode = TextPart.PLAIN

    def handle_data(self, data):
        if self.part_mode == TextPart.PLAIN:
            self.parts.append(TextPart(self.part_mode, data))
        elif self.part_mode in [TextPart.RUBY, TextPart.DOT]:
            self.parts[-1].set_text(data)

    def write(self,cursor):
        for part in self.parts:
            part.write(cursor)


class ColumnChain:

    def __init__(self, name, columns, textattr):
        self.name = name
        self.columns = columns
        self.textattr = textattr
        self.textsource = None

    def set_textsource(self, source):
        self.textsource = source
        self.text = Text(source)

    def write(self, layout, pilimage):
        for column in self.columns:
            column_area = column.get_columnarea(layout)
            cursor = TextCursor(column_area, self.textattr, pilimage)
            self.text.write(cursor)


class NovelLayout:

    def __init__(self, size=(960, 540), margin=(0.1, 0.1, 0.1, 0.1)):
        self._margin = {"up": margin[0], "bottom": margin[1],
                        "left": margin[2], "right": margin[3]}
        self._size = {"w": size[0], "h": size[1]}

    @property
    def margin_mag(self):
        return self._margin

    @property
    def margin(self):
        return (int(self._margin["up"] * self._size["h"]),
                int(self._margin["bottom"] * self._size["h"]),
                int(self._margin["left"] * self._size["w"]),
                int(self._margin["right"] * self._size["w"]))

    @property
    def margin_up(self):
        return int(self._margin["up"] * self._size["h"])

    @property
    def margin_bottom(self):
        return int(self._margin["bottom"] * self._size["h"])

    @property
    def margin_left(self):
        return int(self._margin["left"] * self._size["w"])

    @property
    def margin_right(self):
        return int(self._margin["right"] * self._size["w"])

    @property
    def w(self):
        return self._size["w"]

    @property
    def h(self):
        return self._size["h"]

    @property
    def livearea_w(self):
        return self.w - self.margin_left - self.margin_right

    @property
    def livearea_h(self):
        return self.h - self.margin_up - self.margin_bottom



class Novel:
    def __init__(self, size=(960,540), margin=(0.1,0.1,0.1,0.1)):
        self.layout = NovelLayout(size, margin)
        self.columnchains = {}

    def add_columnchain(self, name, columns, textattr):
        if name in list(self.columnchains.keys()):
            print("Duplicated ColumnChain Name..")
        else:
            self.columnchains[name] = ColumnChain(name,columns,textattr)

    def add_textsource(self, source, columnchain_name):
        if columnchain_name in list(self.columnchains.keys()):
            self.columnchains[columnchain_name].set_textsource(source)
        else:
            print("Cannot find ColumnChain which have specified name.")

    def drawing_is_done(self):
        return False

    def write(self):
        image_index = 0

        while self.drawing_is_done() == False:
            pilimage = Image.new(mode='RGB', size=(self.layout.w, self.layout.h), color="#fff0f0")

            for key,columnchain in self.columnchains.items():
                print("Writing .. for {}".format(columnchain.name))
                columnchain.write(self.layout,pilimage)
            
            pilimage.save("test{}.png".format(image_index), "PNG")
            pilimage.close()
            image_index += 1
            break