import xml.dom.minidom
import zipfile

import odio.v1_1
import odio.v1_2
from odio.common import H, P, Span


def create_spreadsheet(f, version="1.2", compressed=True):
    if version == "1.1":
        return odio.v1_1.SpreadsheetWriter(f, compressed)
    elif version == "1.2":
        return odio.v1_2.SpreadsheetWriter(f, compressed)
    else:
        raise Exception(
            f"The version '{version}' isn't recognized. The valid version strings "
            f"are '1.1' and '1.2'."
        )


def parse_spreadsheet(f):
    with zipfile.ZipFile(f, "r") as z:
        content = z.read("content.xml")
    dom = xml.dom.minidom.parseString(content)
    version = dom.documentElement.getAttribute("office:version")
    spreadsheet_elem = dom.getElementsByTagName("office:spreadsheet")[0]

    if version == "1.1":
        return odio.v1_1.SpreadsheetReader(spreadsheet_elem)
    elif version == "1.2":
        return odio.v1_2.SpreadsheetReader(spreadsheet_elem)
    else:
        raise Exception(
            "The version '{version}' isn't recognized. The valid version strings "
            "are '1.1' and '1.2'."
        )


class Formula:
    def __init__(self, formula):
        self.formula = formula

    def __repr__(self):
        return f"odio.Formula('{self.formula}')"

    def __str__(self):
        return self.formula

    def __eq__(self, other):
        return isinstance(other, Formula) and self.formula == other.formula


def create_text(f, version="1.2"):
    if version == "1.1":
        return odio.v1_1.TextWriter(f)
    elif version == "1.2":
        return odio.v1_2.TextWriter(f)
    else:
        raise Exception(
            f"The version '{version}' isn't recognized. The valid version strings "
            f"are '1.1' and '1.2'."
        )


def parse_text(f):
    with zipfile.ZipFile(f, "r") as z:
        content = z.read("content.xml")
    f.close()
    dom = xml.dom.minidom.parseString(content)
    version = dom.documentElement.getAttribute("office:version")
    text_elem = dom.getElementsByTagName("office:text")[0]

    if version == "1.1":
        return odio.v1_1.TextReader(text_elem)
    elif version == "1.2":
        return odio.v1_2.TextReader(text_elem)
    else:
        raise Exception(
            f"The version '{version}' isn't recognized. The valid version strings "
            f"are '1.1' and '1.2'."
        )


__all__ = ["H", "P", "Span"]
