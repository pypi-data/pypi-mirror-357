import pathlib

current = pathlib.Path(__file__).parent
root = current.parent
package = root / pathlib.Path("source")

import sys
sys.path.append(str(package))

import cx_libtranslate

phrases = {
    "sample": "Przyklad",
    "For example.": "Na przyklad."
}

objects = {
    "a": {
        "b": {
            "c": "result"
        }
    }
}

phrasebook = cx_libtranslate.phrasebook(phrases, objects)
print(phrasebook.translate("sample"))
print(phrasebook.translate("For example."))
print(phrasebook.translate("This not exists."))
print(phrasebook.translate("a.b.c"))