"""Rebuild self-contained engine and script without third-party dependencies."""
import ast
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DEV=ROOT/'development'
MODULES=['i18n','preferences','quad_fit','segment_index','roots_unit','geometry_fit','search_core','chain_fit','tangent_constraints','options_fit','fast_fit','merge_fit','native_probe','glyphs_adapter']
chunks=[]
for name in MODULES:
    text=(DEV/(name+'.py')).read_text(encoding='utf-8')
    lines=text.splitlines()
    remove=set()
    for node in ast.walk(ast.parse(text)):
        if isinstance(node,ast.ImportFrom) and node.module in MODULES:
            remove.update(range(node.lineno-1,node.end_lineno))
    chunks.append('\n'.join(line for i,line in enumerate(lines) if i not in remove))
engine='# -*- coding: utf-8 -*-\n# Copyright 2026 Zonz\n'+('\n\n'.join(chunks))+'\n'
(ROOT/'CubicToCompactQuadratic.glyphsPlugin/Contents/Resources/Zonz_quad_engine.py').write_text(engine,encoding='utf-8')
header='#MenuTitle: Cubic To Compact Quadratic\n# -*- coding: utf-8 -*-\n# Author: Zonz\n\nMAX_OUTLINE_DEVIATION = 1.0\nMAX_CONTROL_POINTS = 3\nCENTER_CONTROL_LIMIT = 7.0\nCONNECTION_ANGLE_LIMIT = 5.0\nKEEP_LINE_TANGENT = True\nKEEP_CURVE_TANGENT = True\nINTEGER_COORDINATES = True\nADD_MIDPOINT = False\nMERGE_ADJACENT_CURVES = True\n\n'
(ROOT/'CubicToCompactQuadratic.py').write_text(header+engine+\
    '\nif __name__ == "__main__":\n    glyphs_main(MAX_OUTLINE_DEVIATION,MAX_CONTROL_POINTS,ADD_MIDPOINT,MERGE_ADJACENT_CURVES,CENTER_CONTROL_LIMIT,INTEGER_COORDINATES,CONNECTION_ANGLE_LIMIT,KEEP_LINE_TANGENT,KEEP_CURVE_TANGENT)\n',encoding='utf-8')
