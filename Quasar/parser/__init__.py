__all__ = ['tokens', 'ast']


def _get_encodings():
    # https://encoding.spec.whatwg.org/encodings.json
    import os
    import json

    encodings = {}
    directory = os.path.dirname(os.path.abspath(__file__))
    css_encodings_json = os.path.join(directory, 'css_encodings.json')
    with open(css_encodings_json, 'r') as css_encodings_file:
        json_data = json.load(css_encodings_file)
        for name, labels in json_data.iteritems():
            for label in labels:
                encodings[label] = name
    return encodings


css_encodings = _get_encodings()