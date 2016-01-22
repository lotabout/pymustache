import imp
import json
import os
mustache = imp.load_source('mustache', '../src/mustache.py')

#test_files = ['comments.json',
    #'delimiters.json',
    #'interpolation.json',
    #'inverted.json',
    #'~lambdas.json',
    #'partials.json',
    #'sections.json']

test_files = ['interpolation.json',
        'delimiters.json',
        'comments.json',
        'sections.json']

for filename in test_files:
    with open(os.path.join('./spec/specs/', filename)) as fp:
        data = json.load(fp)['tests']

    for test in data:
        context = test['data']
        template = test['template']
        expected = test['expected']
        partials = test['partials'] if 'partials' in test else {}
        result = mustache.render(template, [context], partials)
        if result != expected:
            print('>>>>>>> ERROR >>>>>>>>>>>>>>')
            print('name:', test['name'])
            print('template:', template)
            print('expected:', repr(expected))
            print('result  :', repr(result))


