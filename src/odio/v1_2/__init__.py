import xml.dom.minidom
import zipfile
from datetime import datetime as Datetime
from decimal import Decimal
from tempfile import NamedTemporaryFile
from xml.dom import Node

import odio
from odio.common import H, P, Span


OFFICE_VALUE_TYPE = "office:value-type"


def escape(data):
    return data.replace("&", "&amp;").replace(">", "&gt;").replace("<", "&lt;")


def quoteattr(data):
    data = escape(data)

    if '"' in data:
        if "'" in data:
            data = '"%s"' % data.replace('"', "&quot;")
        else:
            data = "'%s'" % data
    else:
        data = '"%s"' % data
    return data


class XmlWriter:
    def __init__(self, output):
        self.indentation = 0
        self.output = output
        self._write('<?xml version="1.0" encoding="utf-8"?>\n')

    @staticmethod
    def atts_to_str(attrs):
        if len(attrs) == 0:
            return ""
        else:
            return " " + " ".join(
                f"{k}={quoteattr(v)}" for k, v in sorted(attrs.items())
            )

    def _write(self, line, indent=True):
        if indent:
            self.output.write((" " * self.indentation * 2).encode("utf8"))
        self.output.write(line.encode("utf8"))

    def start_tag(self, name, attrs):
        self._write(f"<{name}{XmlWriter.atts_to_str(attrs)}>\n")
        self.indentation += 1

    def end_tag(self, name):
        self.indentation -= 1
        self._write(f"</{name}>\n")

    def simple_tag(self, name, attrs, contents=None):
        if contents is None:
            self._write(f"<{name}{XmlWriter.atts_to_str(attrs)}/>\n")
        else:
            self._write(f"<{name}{XmlWriter.atts_to_str(attrs)}>")
            content = escape(contents)
            if name in (
                "text:a",
                "text:h",
                "text:meta",
                "text:meta-field",
                "text:p",
                "text:ruby-base",
                "text:span",
            ):
                content = "<text:line-break/>".join(content.splitlines())
            self._write(content, indent=False)
            self._write(f"</{name}>\n", indent=False)


class SpreadsheetWriter:
    def __init__(self, f, compressed):
        self.f = f
        if compressed:
            compression = zipfile.ZIP_DEFLATED
        else:
            compression = zipfile.ZIP_STORED
        self.z = zipfile.ZipFile(f, "w", compression)
        self.z.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
        self.z.writestr(
            "META-INF/manifest.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest
    manifest:version="1.2"
    xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
  <manifest:file-entry
      manifest:full-path="/"
      manifest:media-type="application/vnd.oasis.opendocument.spreadsheet"/>
  <manifest:file-entry
      manifest:full-path="settings.xml" manifest:media-type="text/xml"/>
  <manifest:file-entry
      manifest:full-path="content.xml" manifest:media-type="text/xml"/>
  <manifest:file-entry
      manifest:full-path="meta.xml" manifest:media-type="text/xml"/>
  <manifest:file-entry
      manifest:full-path="styles.xml" manifest:media-type="text/xml"/>
</manifest:manifest>
""",
        )
        self.z.writestr(
            "meta.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<office:document-meta
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
    xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"
    office:version="1.2">
  <office:meta>
      <meta:generator>Odio</meta:generator>
  </office:meta>
</office:document-meta>
""",
        )

        self.z.writestr(
            "settings.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<office:document-settings
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0"
    xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"
    office:version="1.2">
</office:document-settings>
""",
        )

        self.z.writestr(
            "styles.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
    xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
    xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
    xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
    xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0"
    xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"
    xmlns:math="http://www.w3.org/1998/Math/MathML"
    xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0"
    xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0"
    xmlns:dom="http://www.w3.org/2001/xml-events"
    xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"
    xmlns:xhtml="http://www.w3.org/1999/xhtml"
    xmlns:css3t="http://www.w3.org/TR/css3-text/"
    office:version="1.2">
</office:document-styles>
""",
        )
        self.tmp = NamedTemporaryFile()
        self.writer = XmlWriter(self.tmp)
        attrs = {
            "xmlns:office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
            "xmlns:office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
            "xmlns:style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
            "xmlns:text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
            "xmlns:table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
            "xmlns:draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
            "xmlns:fo": "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
            "xmlns:xlink": "http://www.w3.org/1999/xlink",
            "xmlns:dc": "http://purl.org/dc/elements/1.1/",
            "xmlns:meta": "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
            "xmlns:number": "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0",
            "xmlns:presentation": "urn:oasis:names:tc:opendocument:xmlns"
            ":presentation:1.0",
            "xmlns:svg": "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
            "xmlns:chart": "urn:oasis:names:tc:opendocument:xmlns:chart:1.0",
            "xmlns:dr3d": "urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0",
            "xmlns:math": "http://www.w3.org/1998/Math/MathML",
            "xmlns:form": "urn:oasis:names:tc:opendocument:xmlns:form:1.0",
            "xmlns:script": "urn:oasis:names:tc:opendocument:xmlns:script:1.0",
            "xmlns:dom": "http://www.w3.org/2001/xml-events",
            "xmlns:xforms": "http://www.w3.org/2002/xforms",
            "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xmlns:of": "urn:oasis:names:tc:opendocument:xmlns:of:1.2",
            "xmlns:xhtml": "http://www.w3.org/1999/xhtml",
            "xmlns:css3t": "http://www.w3.org/TR/css3-text/",
            "office:version": "1.2",
        }
        self.writer.start_tag("office:document-content", attrs)
        self.writer.simple_tag("office:scripts", {})
        self.writer.start_tag("office:automatic-styles", {})
        self.writer.start_tag("number:date-style", {"style:name": "date"})
        self.writer.simple_tag("number:year", {"number:style": "long"})
        self.writer.simple_tag("number:text", {}, "-")
        self.writer.simple_tag("number:month", {"number:style": "long"})
        self.writer.simple_tag("number:text", {}, "-")
        self.writer.simple_tag("number:day", {"number:style": "long"})
        self.writer.simple_tag("number:text", {}, " ")
        self.writer.simple_tag("number:hours", {"number:style": "long"})
        self.writer.simple_tag("number:text", {}, ":")
        self.writer.simple_tag("number:minutes", {"number:style": "long"})
        self.writer.end_tag("number:date-style")
        self.writer.simple_tag(
            "style:style",
            {
                "style:name": "cell_date",
                "style:family": "table-cell",
                "style:parent-style-name": "Default",
                "style:data-style-name": "date",
            },
        )
        self.writer.end_tag("office:automatic-styles")
        self.writer.start_tag("office:body", {})
        self.writer.start_tag("office:spreadsheet", {})

    def append_table(self, name, rows):
        self.writer.start_tag("table:table", {"table:name": name})
        self.writer.simple_tag("table:table-column", {})
        for row in rows:
            self.writer.start_tag("table:table-row", {})
            cells = []
            for val in row:
                atts = {}
                contents = None
                if isinstance(val, Datetime):
                    atts["office:value-type"] = "date"
                    atts["office:date-value"] = val.strftime("%Y-%m-%dT%H:%M:%S")
                    atts["table:style-name"] = "cell_date"
                elif isinstance(val, str):
                    atts["office:value-type"] = "string"
                    contents = val
                    # atts['office:string-value'] = val
                elif isinstance(val, bool):
                    atts["office:value-type"] = "boolean"
                    atts["office:boolean-value"] = "true" if val else "false"
                elif isinstance(val, (float, int, Decimal)):
                    atts["office:value-type"] = "float"
                    atts["office:value"] = str(val)
                elif isinstance(val, odio.Formula):
                    atts["table:formula"] = "of:" + str(val)
                elif val is None:
                    pass
                else:
                    atts["office:value-type"] = "string"
                    atts["office:string-value"] = str(val)

                if (
                    len(cells) > 0
                    and cells[-1]["atts"] == atts
                    and cells[-1]["contents"] == contents
                ):
                    cells[-1]["count"] += 1
                else:
                    cells.append({"count": 1, "atts": atts, "contents": contents})

            for cell in cells:
                atts = cell["atts"]
                contents = cell["contents"]
                if cell["count"] > 1:
                    atts["table:number-columns-repeated"] = str(cell["count"])
                if contents is None:
                    self.writer.simple_tag("table:table-cell", atts)
                else:
                    self.writer.start_tag("table:table-cell", atts)
                    self.writer.simple_tag("text:p", {}, contents=contents)
                    self.writer.end_tag("table:table-cell")
            self.writer.end_tag("table:table-row")

        self.writer.end_tag("table:table")

    def close(self):
        self.writer.end_tag("office:spreadsheet")
        self.writer.end_tag("office:body")
        self.writer.end_tag("office:document-content")
        self.tmp.flush()
        self.tmp.seek(0)
        self.z.write(self.tmp.name, "content.xml")
        self.z.close()
        self.tmp.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class SpreadsheetReader:
    def __init__(self, spreadsheet_elem):
        self.tables = []
        for table_elem in spreadsheet_elem.getElementsByTagName("table:table"):
            self.tables.append(TableReader(table_elem))


def _get_text(node):
    txt = [""]
    for child in node.childNodes:
        if child.nodeType == Node.TEXT_NODE:
            txt.append(child.nodeValue.strip())
        else:
            txt.append(_get_text(child))
    return "".join(txt)


class TableReader:
    def __init__(self, table_elem):
        self.name = table_elem.getAttribute("table:name")
        self.rows = []
        for row_elem in table_elem.getElementsByTagName("table:table-row"):
            row = []
            self.rows.append(row)
            for cell_elem in row_elem.getElementsByTagName("table:table-cell"):
                if cell_elem.hasAttribute("table:formula"):
                    formula = cell_elem.getAttribute("table:formula")
                    eq_idx = formula.index("=")
                    val = odio.Formula(formula[eq_idx:])
                elif cell_elem.hasAttribute(OFFICE_VALUE_TYPE):
                    val_type = cell_elem.getAttribute(OFFICE_VALUE_TYPE)
                    if val_type == "date":
                        val = Datetime.strptime(
                            cell_elem.getAttribute("office:date-value"),
                            "%Y-%m-%dT%H:%M:%S",
                        )
                    elif val_type == "string":
                        if cell_elem.hasAttribute("office:string-value"):
                            val = cell_elem.getAttribute("office:string-value")
                        else:
                            val = _get_text(cell_elem)
                    elif val_type == "float":
                        val = float(cell_elem.getAttribute("office:value"))
                    elif val_type == "boolean":
                        val = cell_elem.getAttribute("office:boolean-value") == "true"
                else:
                    val = None

                if cell_elem.hasAttribute("table:number-columns-repeated"):
                    count = int(cell_elem.getAttribute("table:number-columns-repeated"))
                else:
                    count = 1

                for i in range(count):
                    row.append(val)


class TextWriter:
    def __init__(self, f):
        self.f = f
        self.z = zipfile.ZipFile(f, "w")
        self.z.writestr("mimetype", "application/vnd.oasis.opendocument.text")
        self.z.writestr(
            "META-INF/manifest.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest
    manifest:version="1.2"
    xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
  <manifest:file-entry
      manifest:full-path="/"
      manifest:media-type="application/vnd.oasis.opendocument.text"/>
  <manifest:file-entry
      manifest:full-path="settings.xml" manifest:media-type="text/xml"/>
  <manifest:file-entry
      manifest:full-path="content.xml" manifest:media-type="text/xml"/>
  <manifest:file-entry
      manifest:full-path="meta.xml" manifest:media-type="text/xml"/>
  <manifest:file-entry
      manifest:full-path="styles.xml" manifest:media-type="text/xml"/>
</manifest:manifest>
""",
        )
        self.z.writestr(
            "meta.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<office:document-meta
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
    xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"
    office:version="1.2">
  <office:meta>
      <meta:generator>Odio</meta:generator>
  </office:meta>
</office:document-meta>
""",
        )

        self.z.writestr(
            "settings.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<office:document-settings
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0"
    xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"
    office:version="1.2">
</office:document-settings>
""",
        )

        self.z.writestr(
            "styles.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
    xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
    xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
    xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
    xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0"
    xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"
    xmlns:math="http://www.w3.org/1998/Math/MathML"
    xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0"
    xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0"
    xmlns:dom="http://www.w3.org/2001/xml-events"
    xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"
    xmlns:xhtml="http://www.w3.org/1999/xhtml"
    xmlns:css3t="http://www.w3.org/TR/css3-text/"
    office:version="1.2">
</office:document-styles>
""",
        )
        self.doc = xml.dom.minidom.parseString(
            """<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
    xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
    xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
    xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
    xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0"
    xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"
    xmlns:math="http://www.w3.org/1998/Math/MathML"
    xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0"
    xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0"
    xmlns:dom="http://www.w3.org/2001/xml-events"
    xmlns:xforms="http://www.w3.org/2002/xforms"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"
    xmlns:xhtml="http://www.w3.org/1999/xhtml"
    xmlns:css3t="http://www.w3.org/TR/css3-text/"
    office:version="1.2">
  <office:scripts/>
  <office:automatic-styles>
    <number:date-style style:name="date">
      <number:year number:style="long"/>
      <number:text>-</number:text>
      <number:month number:style="long"/>
      <number:text>-</number:text>
      <number:day number:style="long"/>
      <number:text> </number:text>
      <number:hours number:style="long"/>
      <number:text>:</number:text>
      <number:minutes number:style="long"/>
    </number:date-style>
    <style:style style:name="cell_date" style:family="table-cell"
      style:parent-style-name="Default" style:data-style-name="date"/>
  </office:automatic-styles>
  <office:body>
    <office:text>
    </office:text>
  </office:body>
</office:document-content>"""
        )
        self.text_elem = self.doc.getElementsByTagName("office:text")[0]

    def append(self, *subnodes):
        for node in subnodes:
            node.attach(self.doc, self.text_elem)

    def close(self):
        self.z.writestr("content.xml", self.doc.toprettyxml(encoding="utf-8"))
        self.z.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class TextReader:
    def __init__(self, text_elem):
        self.nodes = []
        self.attributes = {}
        for node_elem in text_elem.childNodes:
            self._parse_node(self, node_elem)

    def _parse_node(self, parent_node, node_dom):
        node_type = node_dom.nodeType
        if node_type == Node.ELEMENT_NODE:
            name = node_dom.tagName
            if name == "text:p":
                node = P()
            elif name == "text:h":
                node = H()
            elif name == "text:span":
                node = Span()
            else:
                raise Exception(f"Node name {name} not recognized.")
            if node_dom.hasAttributes():
                attrs = node_dom.attributes
                for i in range(len(attrs)):
                    attr = attrs.item(i)
                    attr_name = attr.name.replace(":", "_").replace("-", "_")
                    node.attributes[attr_name] = attr.value
            for subnode_dom in node_dom.childNodes:
                self._parse_node(node, subnode_dom)
        elif node_type == Node.TEXT_NODE:
            fnode = node_dom.nodeValue
            snode = fnode.strip()
            if len(snode) == 0:
                return
            node = snode
            rnode = node.rstrip()
            if len(rnode) < len(fnode):
                node += " "
            lnode = node.lstrip()
            if len(lnode) < len(fnode):
                node = " " + node
        else:
            raise Exception(f"Node type {node_type} not recognized.")
        parent_node.nodes.append(node)
