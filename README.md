pymustache is an template engine for Mustache
[v1.1.3+λ](https://github.com/mustache/spec/releases/tag/v1.1.3).
[Mustache](https://mustache.github.io/) is a logic-less template. It is simple
and elegant.

pymustache is intended to be simple and fast, it supports both Python 2 and
Python 3.

# Install

```
pip install pymustache
```

Quick Example:

```
>>> import pymustache

>>> pymustache.render('Hello {{name}}!', {'name': 'World'})
'Hellow World!'
```

# Demo Usage

Taken from https://mustache.github.io/#demo:

```
>>> import json, pymustache
>>> template_text = """
<h1>{{header}}</h1>
{{#bug}}
{{/bug}}

{{#items}}
  {{#first}}
    <li><strong>{{name}}</strong></li>
  {{/first}}
  {{#link}}
    <li><a href="{{url}}">{{name}}</a></li>
  {{/link}}
{{/items}}

{{#empty}}
  <p>The list is empty.</p>
{{/empty}}
"""

>>> context_text = """
{
  "header": "Colors",
  "items": [
      {"name": "red", "first": true, "url": "#Red"},
      {"name": "green", "link": true, "url": "#Green"},
      {"name": "blue", "link": true, "url": "#Blue"}
  ],
  "empty": false
}
"""

>>> context = json.loads(context_text)

>>> print pymustache.render(template_text, context)

<h1>Colors</h1>

    <li><strong>red</strong></li>
    <li><a href="#Green">green</a></li>
    <li><a href="#Blue">blue</a></li>

>>> compiled_tempalte = pymustache.compiled(template_text)

>>> print compiled_tempalte.render(context)

<h1>Colors</h1>

    <li><strong>red</strong></li>
    <li><a href="#Green">green</a></li>
    <li><a href="#Blue">blue</a></li>

```

# Extension

Native mustache are limited in some ways, for example, it is hard to retrieve
list index while iterate over one. Thus pymustach add some extention syntax,
which is simple and still be compatible with mustache.

## Path

Mustache alreadly support paths like `{{a.b.c}}` for quick reference to sub
contexts. However it had no support for accessing parent contexts, so the
following example will not work(taken form [Mustache 2.0 and the Future of
Mustache.js](http://writing.jan.io/mustache-2.0.html)).

```
view = {
  'foo': {
    'bar': {
      'baz': 1
    },
    'qux': 2
  }
};

{{#foo}}
  {{#bar}}
    {{baz}}
    {{qux}} # uh-oh!
  {{/bar}}
  {{qux}} # this would work, but isn’t what we want
{{/foo}}
```

So we add [handlebar.js](http://handlebarsjs.com/) like path navigation, so
that we can use the following template to achieve it.

```
{{#foo}}
  {{#bar}}
  {{baz}}
  {{../qux}} # ah-ha!
  {{/bar}}
{{/foo}}
```

## Accessing List Element by Index

As we said, we can access items by dot notion like `{{x.y}}`. In javascript,
we can use string index to access list, for example:

```js
var x = [0,1,2,3];
console.log(x['1']); // => 1
```

In python however, we cannot do that. Mustache's spec do not say anything
about this behaviour, for convenience we add similar feature.

```
>>> pymustache.render('Hello {{name.1}}!', {'name': [0,1,2,3]})
Hello 1
```

Note that such function will not work on map, because map keys in python can
be either number or string. So currently there is not way to access number
indices, mainly because it will be invalid JSON.

```
>>> mustache.render('Hello {{name.1}}!', {'name': {1:1, '1': 'string 1'}})
'Hello string 1!'
```

## Filters

pymustache support filters, filters are separated with `|` character:

```
>>> mustache.render('Hello {{name | upper}}!', {'name': 'World'})
'Hello WORLD!'
```

So now you can get the index of list by:

```
>>> mustache.render('{{#list | enum}} {{.0}}: {{.1}},{{/list}}', {'list': [1,2,3] )
' 0: 1, 1: 2, 2: 3,'
```

or iterate over map:

```
>>> mustache.render('{{#list | items}} {{.0}}: {{.1}},{{/list}}', {'list': {'a': 10, 'b': 20}})
' a: 10, b: 20,'
```

You can add your own filter:

```
>>> mustache.filters['strip'] = lambda string: string.strip()
>>> mustache.render('Hello {{name}}!', {'name': '        World  '})
'Hello         World  !'

>>> mustache.render('Hello {{name | strip}}!', {'name': '        World  '})
'Hello World!'
```

So, enjoy!

## Buildin Filters

Currently there are only 4 filters, later I will add more. They are:

- `items`: turn a dict `{'a': 1, 'b': 2}` into `[('a', 1), ('b', 2)]` for
    iteration. Not that do not rely it for output, inside it is not actually a
    list.
- `enum`: turn a list `[1,2,3]` into `[(0,1), (1,2), (1,3)]` for accessing the
    actual index. Note that do not use it for output, cause it does not
    actually output a list
- `upper`: turn a string into upper case.
- `lower`: turn a string into lower case.

# About Musatche

[Mustache](https://mustache.github.io/) is a logic-less templating system.

You can check its syntax here: [mustache(5)](https://mustache.github.io/mustache.5.html)

# Alternatives

- [pystache](https://github.com/defunkt/pystache) a Python implementation of Mustache.
