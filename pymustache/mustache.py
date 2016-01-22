#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

try:
    from html import escape as html_escape
except:
    # python 2
    import cgi
    def html_escape(text):
        return cgi.escape(text, quote=True)

DEFAULT_DELIMITERS = ('{{', '}}')
EMPTYSTRING = ""
spaces_not_newline = ' \t\r\b\f'
re_space = re.compile(r'[' + spaces_not_newline + r']*(\n|$)')
re_insert_indent = re.compile(r'(^|\n)(?=.|\n)', re.DOTALL)

#==============================================================================
# Context lookup.
# Mustache uses javascript's prototype like lookup for variables.

# A context is just a dict, and we use a list of contexts to represent the
# stack, the lookup order is in reversed order

# lookup('x', ({'y': 30, 'z':40}, {'x': 10, 'y': 20}) => 10
# lookup('y', ({'y': 30, 'z':40}, {'x': 10, 'y': 20}) => 20
# lookup('z', ({'y': 30, 'z':40}, {'x': 10, 'y': 20}) => 40
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
    delimiters = tuple(delimiters)
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

def is_standalone(text, start, end):
    """check if the string text[start:end] is standalone by checking forwards
    and backwards for blankspaces
    :text: TODO
    :(start, end): TODO
    :returns: the start of next index after text[start:end]

    """
    left = False
    start -= 1
    while start >= 0 and text[start] in spaces_not_newline:
        start -= 1

    if start < 0 or text[start] == '\n':
        left = True

    right = re_space.match(text, end)
    return (start+1, right.end()) if left and right else None

class Mustache():
    """Mustache template object"""
    def __init__(self, template):
        self.template = template


def compiled(template, delimiters=DEFAULT_DELIMITERS):
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
        token = None
        last_literal = None
        strip_space = False

        if m.start() > index:
            last_literal = Token('str', Token.LITERAL, template[index:m.start()])
            tokens.append(last_literal)

        # parse token
        prefix, name, suffix = m.groups()

        if prefix == '=' and suffix == '=':
            # {{=| |=}} to change delimiters
            delimiters = re.split(r'\s+', name)
            if len(delimiters) != 2:
                raise SyntaxError('Invalid new delimiter definition: ' + m.group())
            re_tag = delimiters_to_re(delimiters)
            strip_space = True

        elif prefix == '{' and suffix == '}':
            # {{{ variable }}}
            token = Token(name, Token.VARIABLE, name)

        elif prefix == '' and suffix == '':
            # {{ name }}
            token = Token(name, Token.VARIABLE, name)
            token.escape = True

        elif suffix != '' and suffix != None:
            raise SyntaxError('Invalid token: ' + m.group())

        elif prefix == '&':
            # {{& escaped variable }}
            token = Token(name, Token.VARIABLE, name)

        elif prefix == '!':
            # {{! comment }}
            token = Token(name, Token.COMMENT)
            if len(sections) <= 0:
                # considered as standalone only outside sections
                strip_space = True

        elif prefix == '>':
            # {{> partial}}
            token = Token(name, Token.PARTIAL, name)
            strip_space = True

            pos = is_standalone(template, m.start(), m.end())
            if pos:
                token.indent = len(template[pos[0]:m.start()])

        elif prefix == '#' or prefix == '^':
            # {{# section }} or # {{^ inverted }}
            token = Token(name, Token.SECTION if prefix == '#' else Token.INVERTED, name)
            token.delimiter = delimiters
            tokens.append(token)

            # save the tokens onto stack
            token = None
            tokens_stack.append(tokens)
            tokens = []

            sections.append((name, prefix, m.end()))
            strip_space = True

        elif prefix == '/':
            tag_name, sec_type, text_end = sections.pop()
            if tag_name != name:
                raise SyntaxError("unclosed tag: '" + name + "' Got:" + m.group())

            children = tokens
            tokens = tokens_stack.pop()

            tokens[-1].text = template[text_end:m.start()]
            tokens[-1].children = children
            strip_space = True

        else:
            raise SyntaxError('Unknown tag: ' + m.group())

        if token is not None:
            tokens.append(token)

        index = m.end()
        if strip_space:
            pos = is_standalone(template, m.start(), m.end())
            if pos:
                index = pos[1]
                if last_literal: last_literal.value = last_literal.value.rstrip(spaces_not_newline)

        m = re_tag.search(template, index)

    tokens.append(Token('str', Token.LITERAL, template[index:]))
    return Token('root', Token.ROOT, children=tokens)

def render(template, contexts, partials={}, delimiters=None):
    """TODO: Docstring for render.

    :template: TODO
    :contexts: TODO
    :partials: TODO
    :delimiters: TODO
    :returns: A parsed string

    """
    if not isinstance(contexts, (list, tuple)):
        contexts = [contexts]

    if not isinstance(partials, dict):
        raise TypeError('partials should be dict, but got ' + type(partials))

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
        self.indent = 0 # used for partial

    def _escape(self, text):
        """Escape text according to self.escape"""
        ret = EMPTYSTRING if not text else str(text)
        if self.escape:
            return html_escape(ret)
        else:
            return ret

    def _lookup(self, dot_name, contexts):
        """lookup value for names like 'a.b.c'

        :dot_name: TODO
        :contexts: TODO
        :returns: None if not found

        """
        if dot_name == '.':
            value = contexts[-1]
        else:
            names = dot_name.split('.')
            value = lookup(names[0], contexts)
            # support {{a.b.c.d.e}} like lookup
            for name in names[1:]:
                try:
                    value = value[name]
                except:
                    # not found
                    break;
        return value

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
        value = self._lookup(self.value, contexts)

        # lambda
        if callable(value):
            value = render(str(value()), contexts, partials)

        return self._escape(value)

    def _render_section(self, contexts, partials):
        """render section"""
        val = self._lookup(self.value, contexts)
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
        elif callable(val):
            # lambdas
            new_template = val(self.text)
            value = render(new_template, contexts, partials, self.delimiter)
        else:
            # context
            contexts.append(val)
            value = self._render_children(contexts, partials)
            contexts.pop()

        return self._escape(value)

    def _render_inverted(self, contexts, partials):
        """render inverted section"""
        val = self._lookup(self.value, contexts)
        if val:
            return EMPTYSTRING
        return self._render_children(contexts, partials)

    def _render_comments(self, contexts, partials):
        """render comments, just skip it"""
        return EMPTYSTRING

    def _render_partials(self, contexts, partials):
        """render partials"""
        try:
            partial = partials[self.value]
        except KeyError as e:
            return self._escape(EMPTYSTRING)

        partial = re_insert_indent.sub(r'\1' + ' '*self.indent, partial)

        return render(partial, contexts, partials, self.delimiter)

    def render(self, contexts, partials={}):
        """Run the current token with contexts and partials

        :contexts: the context stack, (context1, context2, ...)
        :partials: a dict of partials {'name': token, ...}
        :returns: A string contains the rendered result

        """
        if not isinstance(contexts, (list, tuple)):
            contexts = [contexts]

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
