from cattrs.preconf.json import make_converter

JSON_CONVERTER = make_converter(prefer_attrib_converters=True)
