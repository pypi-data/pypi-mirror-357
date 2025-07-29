import pathlib

current = pathlib.Path(__file__).parent
root = current.parent
package = root / pathlib.Path("source")

import sys
sys.path.append(str(package))

import cx_libtranslate

sample = cx_libtranslate.translation("This is #{ sample } with #{ number } but this #{ not_exists } and that is #{ bad } type of } } #{ format }} what is it. Number: #{ number }.")

print("Testing...")
print("Result: " + str(sample))
print("Formated: " + sample.format({
    "sample": "example", 
    "number": 10
})  )