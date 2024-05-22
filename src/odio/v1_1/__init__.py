import xml.dom.minidom
import zipfile
from datetime import datetime as Datetime


OFFICE_VALUE_TYPE = "office:value-type"


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
</manifest:manifest>""",
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
    office:version="1.1">
  <office:meta>
      <meta:generator>ODFIO</meta:generator>
  </office:meta>
</office:document-meta>""",
        )

        self.z.writestr(
            "settings.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<office:document-settings
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0"
    xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"
    office:version="1.1">
</office:document-settings>""",
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
    office:version="1.1">
</office:document-styles>""",
        )

        impl = xml.dom.minidom.getDOMImplementation()
        self.doc = impl.createDocument(
            "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
            "office:document-content",
            None,
        )
        document_content = self.doc.documentElement
        for name, value in (
            ("office:version", "1.1"),
            ("xmlns:chart", "urn:oasis:names:tc:opendocument:xmlns:chart:1.0"),
            ("xmlns:css3t", "http://www.w3.org/TR/css3-text/"),
            ("xmlns:dc", "http://purl.org/dc/elements/1.1/"),
            ("xmlns:dom", "http://www.w3.org/2001/xml-events"),
            ("xmlns:dr3d", "urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"),
            ("xmlns:draw", "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"),
            (
                "xmlns:fo",
                "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:" "1.0",
            ),
            ("xmlns:form", "urn:oasis:names:tc:opendocument:xmlns:form:1.0"),
            ("xmlns:math", "http://www.w3.org/1998/Math/MathML"),
            ("xmlns:meta", "urn:oasis:names:tc:opendocument:xmlns:meta:1.0"),
            ("xmlns:number", "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"),
            ("xmlns:of", "urn:oasis:names:tc:opendocument:xmlns:of:1.2"),
            ("xmlns:office", "urn:oasis:names:tc:opendocument:xmlns:office:1.0"),
            (
                "xmlns:presentation",
                "urn:oasis:names:tc:opendocument:xmlns:presentation:1.0",
            ),
            ("xmlns:script", "urn:oasis:names:tc:opendocument:xmlns:script:1.0"),
            ("xmlns:style", "urn:oasis:names:tc:opendocument:xmlns:style:1.0"),
            ("xmlns:svg", "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"),
            ("xmlns:table", "urn:oasis:names:tc:opendocument:xmlns:table:1.0"),
            ("xmlns:text", "urn:oasis:names:tc:opendocument:xmlns:text:1.0"),
            ("xmlns:xforms", "http://www.w3.org/2002/xforms"),
            ("xmlns:xhtml", "http://www.w3.org/1999/xhtml"),
            ("xmlns:xlink", "http://www.w3.org/1999/xlink"),
            ("xmlns:xsd", "http://www.w3.org/2001/XMLSchema"),
            ("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance"),
        ):
            document_content.setAttribute(name, value)
        scripts = self.doc.createElement("office:scripts")
        document_content.appendChild(scripts)

        automatic_styles = self.doc.createElement("office:automatic-styles")
        document_content.appendChild(automatic_styles)

        date_style = self.doc.createElement("number:date-style")
        automatic_styles.appendChild(date_style)

        date_style.setAttribute("style:name", "date")

        year = self.doc.createElement("number:year")
        date_style.appendChild(year)

        year.setAttribute("number:style", "long")
        text = self.doc.createElement("number:text")
        date_style.appendChild(text)

        text_node = self.doc.createTextNode("-")
        text.appendChild(text_node)

        month = self.doc.createElement("number:month")
        date_style.appendChild(month)

        month.setAttribute("number:style", "long")
        text = self.doc.createElement("number:text")
        date_style.appendChild(text)

        text_node = self.doc.createTextNode("-")
        text.appendChild(text_node)

        day = self.doc.createElement("number:day")
        date_style.appendChild(day)

        day.setAttribute("number:style", "long")
        text = self.doc.createElement("number:text")
        date_style.appendChild(text)

        text_node = self.doc.createTextNode(" ")
        text.appendChild(text_node)

        hours = self.doc.createElement("number:hours")
        date_style.appendChild(hours)

        hours.setAttribute("number:style", "long")
        text = self.doc.createElement("number:text")
        date_style.appendChild(text)

        text_node = self.doc.createTextNode(":")
        text.appendChild(text_node)

        minutes = self.doc.createElement("number:minutes")
        date_style.appendChild(minutes)

        minutes.setAttribute("number:style", "long")

        style = self.doc.createElement("style:style")
        automatic_styles.appendChild(style)

        style.setAttribute("style:data-style-name", "date")
        style.setAttribute("style:family", "table-cell")
        style.setAttribute("style:name", "cell_date")
        style.setAttribute("style:parent-style-name", "Default")

        body = self.doc.createElement("office:body")
        document_content.appendChild(body)
        self.spreadsheet_elem = self.doc.createElement("office:spreadsheet")
        body.appendChild(self.spreadsheet_elem)

    def append_table(self, name):
        table_elem = self.spreadsheet_elem.appendChild(
            self.doc.createElement("table:table")
        )
        table_elem.setAttribute("table:name", name)
        table_elem.appendChild(self.doc.createElement("table:table-column"))
        return Table(self.doc, table_elem)

    def close(self):
        self.z.writestr("content.xml", self.doc.toprettyxml(encoding="utf-8"))
        self.z.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class Table:
    def __init__(self, doc, table_elem):
        self.doc = doc
        self.table_elem = table_elem

    def append_row(self, vals):
        row_elem = self.table_elem.appendChild(
            self.doc.createElement("table:table-row")
        )
        for val in vals:
            cell_elem = row_elem.appendChild(self.doc.createElement("table:table-cell"))
            if isinstance(val, Datetime):
                cell_elem.setAttribute(
                    "office:date-value", val.strftime("%Y-%m-%dT%H:%M:%S")
                )
                cell_elem.setAttribute("office:value-type", "date")
                cell_elem.setAttribute("table:style-name", "cell_date")
            elif isinstance(val, str):
                cell_elem.setAttribute("office:string-value", val)
                cell_elem.setAttribute("office:value-type", "string")
            elif isinstance(val, (float, int)):
                cell_elem.setAttribute("office:value", str(val))
                cell_elem.setAttribute("office:value-type", "float")
            elif val is None:
                pass
            else:
                raise Exception(f"Type of '{val}' not recognized.")


class SpreadsheetReader:
    def __init__(self, spreadsheet_elem):
        self.tables = []
        for table_elem in spreadsheet_elem.getElementsByTagName("table:table"):
            self.tables.append(TableReader(table_elem))


class TableReader:
    def __init__(self, table_elem):
        self.name = table_elem.getAttribute("table:name")
        self.rows = []
        for row_elem in table_elem.getElementsByTagName("table:table-row"):
            row = []
            self.rows.append(row)
            for cell_elem in row_elem.getElementsByTagName("table:table-cell"):
                if cell_elem.hasAttribute(OFFICE_VALUE_TYPE):
                    val_type = cell_elem.getAttribute(OFFICE_VALUE_TYPE)
                    if val_type == "date":
                        val = Datetime.strptime(
                            cell_elem.getAttribute("office:date-value"),
                            "%Y-%m-%dT%H:%M:%S",
                        )
                    elif val_type == "string":
                        val = cell_elem.getAttribute("office:string-value")
                    elif val_type == "float":
                        val = float(cell_elem.getAttribute("office:value"))
                else:
                    val = None
                row.append(val)
