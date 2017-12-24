class Writer:
    pass

class Book:
    def __init__(self):
        self.text = []

    def addText(self, text):
        self.text.append(text)

class Page:
    def __init__(self, param):
        # self._margin = {"up": margin[0], "bottom": margin[1],
        #                 "left": margin[2], "right": margin[3]}
        # self._size = {"w": size[0], "h": size[1]}
        pass

class ColumnChain:
    def __init__(self, name, columns, textattr):
        self.name = name
        self.columns = columns
        self.textattr = textattr

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

    def __init__(self, refpoint, refline, offsetx, offsety, sizew, sizeh):
        self.refpoint = refpoint
        self.refline = {"H": refline[0], "V": refline[1]}
        self.offset = {"x": {"refs": offsetx[0], "mag": offsetx[1]},
                       "y": {"refs": offsety[0], "mag": offsety[1]}}
        self.size = {"w": {"refs": sizew[0], "mag": sizew[1]},
                     "h": {"refs": sizeh[0], "mag": sizeh[1]}}


class TextPart:
    name = 'text'
    start_descriptor = '||'
    end_descriptor = '|'
    def __init__(self, source):
        self.source = source
        self.text = None
        self.parse()

    def parse(self):
        self.text = self.source

    def print(self):
        pass

class PlainTextPart(TextPart):
    def print(self):
        print("{}:{}".format(self.name, self.text))

class RubyTextPart(TextPart):
    name = 'ruby'
    start_descriptor = '|r'

    def __init__(self,source):
        self.ruby = None
        super().__init__(source)

    def parse(self):
        text, sep, ruby = self.source.partition(u':')
        self.text = text
        self.ruby = ruby

    def print(self):
        print("{}:{}:{}".format(self.name, self.text, self.ruby))

class DotTextPart(TextPart):
    name = 'dot'
    start_descriptor = '|.'

    def print(self):
        print("{}:{}".format(self.name, self.text))


class TextDescriptors:
    def __init__(self):
        self.descriptors = []

    def add(self, descriptor_class):
        self.descriptors.append({'key':descriptor_class.name, 'start':descriptor_class.start_descriptor,
                                 'end':descriptor_class.end_descriptor, 'constractor':descriptor_class})

    def get(self, key):
        for desc in self.descriptors:
            if key == desc['key']:
                return desc

    def find(self, source):
        ### reutns a descriptor key which is found fisrt, and parts class.
        pos = {}
        for desc in self.descriptors:
            if not source.find(desc['start']) == -1:
                pos[desc['key']] = source.find(desc['start'])
        
        if len(pos) == 0:
            # みつからない
            return (None, [PlainTextPart(source)], None)
        else:
            key = min(pos)
            plain, ssep, remain = source.partition(self.get(key)['start'])
            content, esep, remain = remain.partition(self.get(key)['end'])
            if plain == "":
                return (key, [self.get(key)['constractor'](content)], remain)
            else:
                return (key, [PlainTextPart(plain) ,self.get(key)['constractor'](content)], remain)

    def parse(self, source):
        all_parts = []
        while True:
            key, parts, source = self.find(source)
            all_parts += parts
            if key == None:
                break
        return all_parts

class Text:
    def __init__(self, columnchain, source):
        self.source = source
        self.columnchain = columnchain
        self.parts = None

        descriptor = TextDescriptors()
        descriptor.add(RubyTextPart)
        descriptor.add(DotTextPart)

        source_text = self.source
        self.parts = descriptor.parse(source_text)

        print(self.columnchain)
        for part in self.parts:
            print (part)

class TextAttribute:
    # Direction of writing text
    DIRECTION_HORIZONTAL = 0
    DIRECTION_VERTICAL = 1

    def __init__(self, font, fontsize, direction, linespace, rubysize, color):
        self.font = font
        self.fontsize = fontsize
        self.direction = direction
        self.linespace = linespace
        self.rubysize = rubysize
        self.color = color
