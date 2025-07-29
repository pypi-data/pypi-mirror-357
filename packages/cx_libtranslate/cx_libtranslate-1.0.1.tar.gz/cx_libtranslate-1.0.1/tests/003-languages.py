import pathlib

current = pathlib.Path(__file__).parent
root = current.parent
package = root / pathlib.Path("source")

import sys
sys.path.append(str(package))

import cx_libtranslate

lang = cx_libtranslate.languages(current)
lang.load(pathlib.Path("./sample_index.json"))

objects = lang.select("en_US")
phrases = lang.select("pl_PL")

print("Objects:")
print("a.b: " + objects.tr("a.b").text)
print("for example: " + objects.tr("for example").text)
print()

print("Phrases:")
print("for example: " + phrases.tr("for example").text)
print("example: " + phrases.tr("example").text)
print()

print("Avairable languages:")
print(lang.avairable)
print("Default language:")
print(lang.default)
print()

phrases.set_as_default()

print("Set as default:")
print(_("sample"))
print()