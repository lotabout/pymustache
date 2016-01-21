#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#==============================================================================
# Context lookup.
# Mustache uses javascript's prototype like lookup for variables.

# A context is just a dict, and we use a list of contexts to represent the
# stack

# lookup('x', ({'x': 10, 'y': 20}, {'y': 30, 'z':40}) => 10
# lookup('y', ({'x': 10, 'y': 20}, {'y': 30, 'z':40}) => 20
# lookup('z', ({'x': 10, 'y': 20}, {'y': 30, 'z':40}) => 40
def lookup(var_name, contexts=()):
    """lookup the value of the var_name on the stack of contexts

    :var_name: TODO
    :contexts: TODO
    :returns: None if not found

    """
    for context in contexts:
        if var_name in context:
            return context[var_name]
    return None

