import argparse
from pathlib import Path
import xml.etree.ElementTree as ET
import Book

class Error(Exception):
    pass

class BookParserError(Error):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("infile")
    arguments = argument_parser.parse_args()

    infilePath = Path(arguments.infile).resolve()
    print (infilePath)
    if infilePath.exists() == False:
        raise BookParserError("File not found", infilePath)

    element_tree = ET.parse(infilePath)
    root = element_tree.getroot()

    if root.tag == "book":
        book = Book.Book(root.attrib)
    else:
        raise BookParserError("Root tag is not <book>.", None)

    for layout in root.iter('layout'):
        booklayout = Book.Layout(layout.attrib)
        for columnchain in root.iter('columnchain'):
            booklayout.addColumnChain(columnchain.attrib)
            for column in columnchain.iter('column'):
                booklayout.getColumnChain(columnchain.attrib['name']).addColumn(column.attrib)

    book.addLayout(booklayout)

    for text in root.iter('text'):
        textPath = Path(text.attrib['src']).resolve()
        if textPath.exists() == True:
            print("Reading text source..")
            with textPath.open() as file:
                booktext = Book.Text(text.attrib['columnchain'], file.read())
                book.addText(booktext)
        else:
            print("File not found..")

    book.write(file="test")

if __name__ == '__main__':
    main()
