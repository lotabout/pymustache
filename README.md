[Mustache](https://mustache.github.io/) is a logic-less template. It is simple
and elegant. I am not trying to reinventing the wheel, I'm just re-creating
it in python.

Note that I build this as a test for myself only, no optimization is made. If
you need a template tool for product,
[pystache](https://github.com/defunkt/pystache) might be a good choise.

# Install
pymustache supports both Python 2 and Python 3.

```
pip install pymustache
```

Quick Example:

```
>>> import pymustache

>>> pymustache.render('Hellow {{name}}!', {'name': 'World'})
'Hellow World!'
```


# Demo Usage

Taken from https://mustache.github.io/#demo: They are typed in [IPython](http://ipython.org/)

```
In [1]: import json, pymustache

In [2]: template_text = """
   ...: <h1>{{header}}</h1>
   ...: {{#bug}}
   ...: {{/bug}}
   ...:
   ...: {{#items}}
   ...:   {{#first}}
   ...:     <li><strong>{{name}}</strong></li>
   ...:   {{/first}}
   ...:   {{#link}}
   ...:     <li><a href="{{url}}">{{name}}</a></li>
   ...:   {{/link}}
   ...: {{/items}}
   ...:
   ...: {{#empty}}
   ...:   <p>The list is empty.</p>
   ...: {{/empty}}
   ...: """

In [3]: context_text = """
   ...: {
   ...:   "header": "Colors",
   ...:   "items": [
   ...:       {"name": "red", "first": true, "url": "#Red"},
   ...:       {"name": "green", "link": true, "url": "#Green"},
   ...:       {"name": "blue", "link": true, "url": "#Blue"}
   ...:   ],
   ...:   "empty": false
   ...: }
   ...: """

In [4]: context = json.loads(context_text)

In [5]: print pymustache.render(template_text, context)

<h1>Colors</h1>

    <li><strong>red</strong></li>
    <li><a href="#Green">green</a></li>
    <li><a href="#Blue">blue</a></li>

In [6]: compiled_tempalte = pymustache.compiled(template_text)

In [7]: print compiled_tempalte.render(context)

<h1>Colors</h1>

    <li><strong>red</strong></li>
    <li><a href="#Green">green</a></li>
    <li><a href="#Blue">blue</a></li>

```

# About Musatche

[Mustache](https://mustache.github.io/) is a logic-less templating system.

You can check its syntax here: [mustache(5)](https://mustache.github.io/mustache.5.html)
