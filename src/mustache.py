#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#==============================================================================
# Context lookup.
# Mustache uses javascript's prototype like lookup for variables.

# A context is just a dict, and we use a list of contexts to represent the
# stack, the lookup order is in reversed order

# lookup('x', ({'x': 10, 'y': 20}, {'y': 30, 'z':40}) => 10
# lookup('y', ({'x': 10, 'y': 20}, {'y': 30, 'z':40}) => 20
# lookup('z', ({'x': 10, 'y': 20}, {'y': 30, 'z':40}) => 40
def lookup(var_name, contexts=()):
    """lookup the value of the var_name on the stack of contexts

    :var_name: TODO
    :contexts: TODO
    :returns: None if not found

    """
    for context in reversed(contexts):
        try:
            if var_name in context:
                return context[var_name]
        except TypeError as te:
            # we may put variable on the context, skip it
            continue
    return None

def compiled(template, delimiters):
    """Compile a template into token tree

    :template: TODO
    :delimiters: TODO
    :returns: the root token

    """
    return None

def render(template, context, partials, delimiters=None):
    """TODO: Docstring for render.

    :template: TODO
    :contexts: TODO
    :partials: TODO
    :delimiters: TODO
    :returns: A parsed string

    """
    delimiters = DEFAULT_DELIMITERS if delimiters is not None else delimiters
    parent_token = compiled(template, delimiters)
    return parent_token.render(context, partials)

#==============================================================================
# Token
# We'll parse the template into a tree of tokens, so a Token is actually a
# node of the tree.
# We'll save the all the information about the node here.

class Token():
    """The node of a parse tree"""
    LITERAL   = 0
    VARIABLE  = 1
    SECTION   = 2
    INVERTED  = 3
    COMMENT   = 4
    PARTIAL   = 5
    ROOT      = 6
    EMPTYSTRING = ""

    def __init__(self, type=LITERAL, value=None, text='', children=None):
        self.type = type
        self.value = value
        self.text = text
        self.children = children
        self.escape = False
        self.delimiter = None # used for section

    def _escape(self, text):
        """Escape text according to self.escape"""
        if self.escape:
            return EMPTYSTRING if text is None else html_escape(text)
        else:
            return EMPTYSTRING if text is None else text

    def _render_children(self, contexts, partials):
        """Render the children tokens"""
        ret = []
        for child in self.children:
            ret.append(child.render(contexts, partials))
        return EMPTYSTRING.join(ret)

    def _render_literal(self, contexts, partials):
        """render simple literals"""
        return self.value

    def _render_variable(self, contexts, partials):
        """render variable"""
        if self.value == '.':
            # refer to itself `{{.}}`
            value = str(contexts[0])
        else:
            value = lookup(self.value, contexts)

        # lambda
        if callable(value):
            value = render(value(), contexts, partials)

        return self._escape(str(value))

    def _render_section(self, contexts, partials):
        """render section"""
        val = lookup(self.value, contexts)
        if not val:
            # false value
            return EMPTYSTRING

        if isinstance(val, (list, tuple)):
            if len(val) <= 0:
                # empty lists
                return EMPTYSTRING

            # non-empty lists
            ret = []
            for item in val:
                contexts.append(item)
                ret.append(self._render_children(contexts, partials))
                contexts.pop()
            return self._escape(''.join(ret))

        if callable(val):
            # lambdas
            new_template = val(self.text)
            value = render(new_template, contexts, partials, self.delimiter)
        else:
            # context
            contexts.append(val)
            value = self._render_children(contexts, partials)
            contexts.pop()

        return self._escape(str(value))

    def _render_inverted(self, contexts, partials):
        """render inverted section"""
        val = lookup(self.value, contexts)
        if val:
            return EMPTYSTRING
        self._render_children(contexts, partials)

    def _render_comments(self, contexts, partials):
        """render comments, just skip it"""
        return EMPTYSTRING

    def _render_partials(self, contexts, partials):
        """render partials"""
        try:
            partial = partials[self.value]
        except KeyError as e:
            raise ValueError('partial not found: ' + self.value)

        return render(partial, contexts, partials, self.delimiter)

    def render(self, contexts, partials):
        """Run the current token with contexts and partials

        :contexts: the context stack, (context1, context2, ...)
        :partials: a dict of partials {'name': token, ...}
        :returns: A string contains the rendered result

        """
        if self.type == LITERAL:
            return self._render_literal(contexts, partials)
        elif self.type == VARIABLE:
            return self._render_variable(contexts, partials)
        elif self.type == SECTION:
            return self._render_section(contexts, partials)
        elif self.type == INVERTED:
            return self._render_inverted(contexts, partials)
        elif self.type == COMMENT:
            return self._render_comments(contexts, partials)
        elif self.type == PARTIAL:
            return self._render_partials(contexts, partials)
        elif self.type == ROOT:
            return self._render_children(contexts, partials)
        else:
            raise TypeError('Invalid Token Type')
