from PIL import ImageFont, ImageDraw, Image

class Writer:
    pass

class Cursor:
    def __init__(self):
        pass

class Page:
    def __init__(self, size):
        print (size)
        self.image = Image.new(mode="RGB", size=(int(size[0]),int(size[1])), color="#ffffff")

    def write(self, text):
        pass

class Book:
    def __init__(self, param):
        self.text = []
        self.layout = []
        self.param = param
        print(self.param)

    def addLayout(self, layout):
        print("Adding layout..")
        self.layout.append(layout)

    def addText(self, text):
        print("Adding text..")
        self.text.append(text)

    def write(self, **param):
        print("Writing ...")
        for text in self.text:
            if text.IsRemain():
                page = Page(size=(self.param["width"],self.param["height"]))
                
            page.image.save("test.png","PNG")


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
    NAME = "TEXT"
    def __init__(self):
        self.content = None
        self.description = None

    def print(self):
        print("{}:{}:{}".format(self.NAME, self.content, self.description))

class PlainTextPart(TextPart):
    NAME = "PLAIN"
    def __init__(self, source):
        super().__init__()
        self.content = source

class RubyTextPart(TextPart):
    NAME = "RUBY"
    def __init__(self, source):
        super().__init__()
        self.content, descriptor, self.description = source.partition(':')

class DotTextPart(TextPart):    
    NAME = "DOT"
    def __init__(self, source):
        super().__init__()
        self.content = source

class Descriptor:
    NAME="NONE"
    START='||'
    END='|'
    def __init__(self):
        pass

    def createPart(self, source):
        pass

class RubyDescriptor(Descriptor):
    NAME="RUBY"
    START='|r'
    END='|'
    def __init__(self):
        super().__init__()

    def createPart(self,source):
        return RubyTextPart(source)

class DotDescriptor(Descriptor):
    NAME="DOT"
    START='|.'
    END='|'
    def __init__(self):
        super().__init__()

    def createPart(self, source):
        return DotTextPart(source)

class DescriptionParser:                             
    def __init__(self):                   
        self.descriptors = {RubyDescriptor.NAME:RubyDescriptor(),
                            DotDescriptor.NAME:DotDescriptor()}

    def parse(self, source):
        parts = []

        while True:
            pos = {}
            for desc in self.descriptors:
                desc_pos = source.find(self.descriptors[desc].START)
                if not desc_pos == -1:
                    pos[self.descriptors[desc].NAME] = source.find(self.descriptors[desc].START)

            if len(pos) == 0:
                parts.append(PlainTextPart(source))
                break

            key = min(pos)
            plaintext, start_descriptor, remain = source.partition(self.descriptors[key].START)
            content, end_descriptor, remain = remain.partition(self.descriptors[key].END)

            source = remain

            if not plaintext == "":
                 parts.append(PlainTextPart(plaintext))
            parts.append(self.descriptors[key].createPart(content))

        return parts

class Text:
    def __init__(self, columnchain, source):
        self.source = source
        self.columnchain = columnchain
        self.parts = None
        self.plaintext = None

        parser = DescriptionParser()
        source_text = self.source
        self.parts = parser.parse(source_text)
        for part in self.parts:
            part.print()

    def IsRemain(self):
        if self.parts == None:
            return False
        else:
            return True

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
