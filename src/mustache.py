#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from html import escape as html_escape

DEFAULT_DELIMITERS = ('{{', '}}')
EMPTYSTRING = ""

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

#==============================================================================
# Compilation
# To compile a template into a tree of tokens, using the given delimiters.
re_delimiters = {}

def delimiters_to_re(delimiters):
    """convert delimiters to corresponding regular expressions"""

    # caching
    if delimiters in re_delimiters:
        re_tag = re_delimiters[delimiters]
    else:
        open_tag, close_tag = delimiters

        # escape
        open_tag = ''.join([c if c.isalnum() else '\\' + c for c in open_tag])
        close_tag = ''.join([c if c.isalnum() else '\\' + c for c in close_tag])

        re_tag = re.compile(open_tag + r'([#^>&{/!=]?)\s*(.*?)\s*([}=]?)' + close_tag, re.DOTALL)
        re_delimiters[delimiters] = re_tag

    return re_tag

class SyntaxError(Exception):
    pass


def compiled(template, delimiters):
    """Compile a template into token tree

    :template: TODO
    :delimiters: TODO
    :returns: the root token

    """
    re_tag = delimiters_to_re(delimiters)

    # variable to save states
    tokens = []
    index = 0
    sections = []
    tokens_stack = []

    m = re_tag.search(template, index)

    while m is not None:
        if m.start() > index:
            tokens.append(Token('str', Token.LITERAL, template[index:m.start()]))
        # parse token
        prefix, name, suffix = m.groups()
        token = None

        if prefix == '=' and postfix == '=':
            # {{=| |=}} to change delimiters
            delimiters = re.split(r'\s+', name)
            if len(delimiters) != 2:
                raise SyntaxError('Invalid new delimiter definition: ' + m.group())
            re_tag = delimiters_to_re(delimiters)

        elif prefix == '{' and suffix == '}':
            # {{{ variable }}}
            token = Token(name, Token.VARIABLE, name)
            token.escape = True

        elif prefix == '' and suffix == '':
            # {{ name }}
            token = Token(name, Token.VARIABLE, name)

        elif suffix != '' and suffix != None:
            raise SyntaxError('Invalid token: ' + m.group())

        elif prefix == '&':
            # {{& escaped variable }}
            token = Token(name, Token.VARIABLE, name)
            token.escape = True

        elif prefix == '!':
            # {{! comment }}
            token = Token(name, Token.COMMENT)

        elif prefix == '>':
            # {{> partial}}
            token = Token(name, Token.PARTIAL, name)

        elif prefix == '#' or prefix == '^':
            # {{# section }} or # {{^ inverted }}
            token = Token(name, Token.SECTION if prefix == '#' else Token.INVERTED, name)
            tokens.append(token)

            # save the tokens onto stack
            token = None
            tokens_stack.append(tokens)
            tokens = []

            sections.append((name, prefix, m.end()))

        elif prefix == '/':
            tag_name, sec_type, text_end = sections.pop()
            if tag_name != name:
                raise SyntaxError("unclosed tag: '" + name + "' Got:" + m.group())

            children = tokens
            tokens = tokens_stack.pop()

            tokens[-1].text = template[text_end:m.start()]
            tokens[-1].children = children

        else:
            raise SyntaxError('Unknown tag: ' + m.group())

        if token is not None:
            tokens.append(token)

        index = m.end()
        m = re_tag.search(template, index)

    tokens.append(Token('str', Token.LITERAL, template[index:]))
    return Token('root', Token.ROOT, children=tokens)

def render(template, contexts, partials=[], delimiters=None):
    """TODO: Docstring for render.

    :template: TODO
    :contexts: TODO
    :partials: TODO
    :delimiters: TODO
    :returns: A parsed string

    """
    delimiters = DEFAULT_DELIMITERS if delimiters is None else delimiters
    parent_token = compiled(template, delimiters)
    return parent_token.render(contexts, partials)

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

    def __init__(self, name, type=LITERAL, value=None, text='', children=None):
        self.name = name
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
            raise SyntaxError('partial not found: ' + self.value)

        return render(partial, contexts, partials, self.delimiter)

    def render(self, contexts, partials):
        """Run the current token with contexts and partials

        :contexts: the context stack, (context1, context2, ...)
        :partials: a dict of partials {'name': token, ...}
        :returns: A string contains the rendered result

        """
        if self.type == self.LITERAL:
            return self._render_literal(contexts, partials)
        elif self.type == self.VARIABLE:
            return self._render_variable(contexts, partials)
        elif self.type == self.SECTION:
            return self._render_section(contexts, partials)
        elif self.type == self.INVERTED:
            return self._render_inverted(contexts, partials)
        elif self.type == self.COMMENT:
            return self._render_comments(contexts, partials)
        elif self.type == self.PARTIAL:
            return self._render_partials(contexts, partials)
        elif self.type == self.ROOT:
            return self._render_children(contexts, partials)
        else:
            raise TypeError('Invalid Token Type')

    def _type_string(self):
        if self.type == self.LITERAL:
            return 'L'
        elif self.type == self.VARIABLE:
            return 'V'
        elif self.type == self.COMMENT:
            return 'C'
        elif self.type == self.SECTION:
            return 'S'
        elif self.type == self.INVERTED:
            return 'I'
        elif self.type == self.PARTIAL:
            return 'P'
        elif self.type == self.ROOT:
            return 'R'
        else:
            return 'Unknown'

    def _get_str(self, indent):
        ret = []
        ret.append(' '*indent + '[(')
        ret.append(self._type_string())
        ret.append(',')
        ret.append(self.name)
        if self.value:
            ret.append(',')
            ret.append(repr(self.value))
        ret.append(')')
        if self.children:
            for c in self.children:
                ret.append('\n')
                ret.append(c._get_str(indent+4))
        ret.append(']')
        return ''.join(ret)

    def __str__(self):
        return self._get_str(0)