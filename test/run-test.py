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
        'delimiters.json']

for filename in test_files:
    with open(os.path.join('./spec/specs/', filename)) as fp:
        data = json.load(fp)['tests']

    for test in data:
        context = test['data']
        template = test['template']
        expected = test['expected']
        result = mustache.render(template, [context])
        if result != expected:
            print('>>>>>>>>> Error >>>>>>>>>>>>')
            print('template:', template)
            print('expected:', expected)
            print('result  :', result)


