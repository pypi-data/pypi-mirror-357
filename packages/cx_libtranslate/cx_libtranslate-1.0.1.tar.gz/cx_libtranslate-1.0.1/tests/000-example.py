import pathlib

current = pathlib.Path(__file__).parent
root = current.parent
package = root / pathlib.Path("source")

import sys
sys.path.append(str(package))

import cx_libtranslate

