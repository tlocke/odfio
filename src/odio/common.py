from itertools import chain


class Node:
    def __init__(self, name, default_attrs, *nodes, **attributes):
        self.default_attrs = default_attrs
        self.nodes = list(nodes)
        real_attrs = default_attrs.copy()
        real_attrs.update(attributes)
        self.attributes = real_attrs
        self.name = name

    def __repr__(self):
        attrs = self.attributes.copy()
        for k, v in self.default_attrs.items():
            if k in attrs and attrs[k] == v:
                del attrs[k]
        arg_str = ", ".join(
            chain(
                (repr(node) for node in self.nodes),
                (k + "=" + repr(v) for k, v in attrs.items()),
            )
        )
        return f"odio.{self.__class__.__name__}({arg_str})"

    def __eq__(self, other):
        return (
            isinstance(other, Node)
            and self.name == other.name
            and self.nodes == other.nodes
            and self.attrs == other.attrs
        )

    def attach(self, doc, parent_elem):
        node_elem = doc.createElement(self.name)
        parent_elem.appendChild(node_elem)
        for k, v in self.attributes.items():
            try:
                i = k.index("_")
            except ValueError:
                raise Exception(
                    f"Problem with the attribute '{k}'. Attributes must have a "
                    f"namespace prefix, eg. 'text_'."
                )
            node_elem.setAttribute(k[:i] + ":" + k[i + 1 :], v)
        if isinstance(self, H):
            node_elem.setAttribute("text:outline-level", self.name[-1])
        for node in self.nodes:
            if isinstance(node, str):
                node_elem.appendChild(doc.createTextNode(node))
            else:
                node.attach(doc, node_elem)


class H(Node):
    def __init__(self, *nodes, **attrs):
        Node.__init__(self, "text:h", {"text_style_name": "Heading 1"}, *nodes, **attrs)


class P(Node):
    def __init__(self, *nodes, **attrs):
        Node.__init__(self, "text:p", {"text_style_name": "Text Body"}, *nodes, **attrs)


class Span(Node):
    def __init__(self, *nodes, **attrs):
        Node.__init__(
            self, "text:span", {"text_style_name": "Text Body"}, *nodes, **attrs
        )
