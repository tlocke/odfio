# Odio

A pure-Python library for the import / export of
[ODF](http://en.wikipedia.org/wiki/OpenDocument) (`.ods` and `.odt`) documents.


# Installation

- Create a virtual environment: `python3 -m venv venv`
- Activate the virtual environment: `source venv/bin/activate`
- Install: `pip install odio`


# Quickstart

Create a spreadsheet:

```python
>>> import odio
>>> import datetime
>>> 
>>>
>>> # Create the spreadsheet.
>>> # Version is ODF version. Can be '1.1' or '1.2'. The default is '1.2'.
>>> # Default for 'compressed' is True.
>>> with open('test.ods', 'wb') as f, odio.create_spreadsheet(
...         f, version='1.2', compressed=True) as sheet:
...	
...	# Add a table (tab) to the spreadsheet
... 	sheet.append_table(
...         'Plan',
...         [
...             [
...                 "veni, vidi, vici", 0.3, 5, odio.Formula('=B1 + C1'),
...                 datetime.datetime(2015, 6, 30, 16, 38),
...             ],
...         ]
...     )
```


import the spreadsheet:

```python
>>> import odio
>>>
>>>
>>> # Parse the document we just created.
>>> # Version is ODF version. Can be '1.1' or '1.2'. The default is '1.2'.
>>> with open('test.ods', 'rb') as f:
...     sheet = odio.parse_spreadsheet(f)
>>>
>>> table = sheet.tables[0]
>>> print(table.name)
Plan
>>> for row in table.rows:
...     print(row)
['veni, vidi, vici', 0.3, 5.0, odio.Formula('=B1 + C1'), datetime.datetime(2015, 6, 30, 16, 38)]
```


Create a text document:

```python
>>> from odio import create_text, P, H, Span
>>> 
>>>
>>> # Create the text document. The ODF version string can be '1.2' or '1.1'
>>> with open('test.odt', 'wb') as f, create_text(f, '1.2') as txt:
...	
...     txt.append(
...         P("The Meditations", text_style_name='Title'),
...         H("Book One", text_style_name='Heading 1'),
...         P(
...             "From my grandfather ",
...             Span("Verus", text_style_name='Strong Emphasis'),
...             " I learned good morals and the government of my temper."
...         ),
...         P(
...             "From the reputation and remembrance of my father, "
...             "modesty and a ", Span("manly", text_style_name='Emphasis'),
...             " character."
...         )
...      )
```

parse the text document:

```python
>>> import odio
>>>
>>>
>>> # Parse the text document we just created. Can be ODF 1.1 or 1.2 format.
>>> txt = odio.parse_text(open('test.odt', "rb"))
>>> 
>>> # Find a subnode
>>> subnode = txt.nodes[2] 
>>> print(subnode.name)
text:p
>>> print(subnode.attributes['text_style_name'])
Text Body
>>> print(subnode)
odio.P(' From my grandfather ', odio.Span('Verus', text_style_name='Strong Emphasis'), ' I learned good morals and the government of my temper. ')
```

# Regression Tests

- Install `tox`: `pip install tox`
- Run `tox`: `tox`


# Doing A Release Of Odio

Run ``tox`` make sure all tests pass, then update the release notes and then do::

- `git tag -a x.y.z -m "version x.y.z"`
- `rm -r build; rm -r dist`
- `python -m build`
-  `twine upload --sign dist/*`


# Release Notes


## Version 0.0.22, 2021-02-08

- Substitute `<text:line-break/>` for line breaks.


## Version 0.0.21, 2021-02-05

- Finding text should never result in a `None`.


## Version 0.0.20, 2021-02-04

- Text should appear in the content of a `<text:p>` element within a cell.


## Version 0.0.19, 2021-02-04

- Where line breaks appear in a text element's content, they are now replaced by a
  `<text:line-break/>` element. This means that line breaks appear in the
  spreadsheet, whereas before they didn't.


## Version 0.0.18, 2019-11-29

- Performance improvement: rather than use the `xml.sax.saxutils` versions of
  `escape` and `quoteattr` I've copied them into the source of Odio, but removing
  the code for entities that aren't needed.


## Version 0.0.17, 2018-08-19

- When parsing a spreadsheet cell of text type, if the value isn't contained in the
  attribute, recursively use the next nodes in the element contents.
