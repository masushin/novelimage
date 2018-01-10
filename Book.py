

class Writer:
    pass

class Cursor:
    def __init__(self):
        pass

class Page:
    def __init__(self):
        pass

class Book:
    def __init__(self, param):
        self.text = []
        self.layout = []

    def addLayout(self, layout):
        print("Adding layout..")
        self.layout.append(layout)

    def addText(self, text):
        print("Adding text..")
        self.text.append(text)

    def write(self, **param):
        print("Writing ...")
        




class Layout:
    def __init__(self, param):
        print("Creating Layout : {}".format(param))
        self.param = param
        self.columnchain = {}

    def addColumnChain(self, param):
        self.columnchain[param['name']] = ColumnChain(param)

    def getColumnChain(self, name):
        return self.columnchain[name]        

class ColumnChain:
    def __init__(self, param):
        print(" Creating ColumnChain : {}".format(param))
        self.param = param
        self.column = []

    def addColumn(self, param):
        self.column.append(Column(param))

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

    def __init__(self, param):
        self.param = param
        print("  Creating Column : {}".format(param))


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
        self.count = {"part":0, "letter":0}

        descriptor = TextDescriptors()
        descriptor.add(RubyTextPart)
        descriptor.add(DotTextPart)

        source_text = self.source
        self.parts = descriptor.parse(source_text)


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
