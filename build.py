"""Build the standalone script and optional plug-in engine from development modules."""
import ast
from pathlib import Path

ROOT=Path(__file__).resolve().parent
MODULES=('i18n', 'preferences', 'quad_fit', 'segment_index', 'roots_unit', 'geometry_fit', 'search_core', 'chain_fit', 'tangent_constraints', 'options_fit', 'fast_fit', 'merge_fit', 'native_probe', 'glyphs_adapter')
HEADER='#MenuTitle: Cubic To Compact Quadratic\n# -*- coding: utf-8 -*-\n# Author: Zonz\n\nMAX_OUTLINE_DEVIATION = 1.0\nMAX_CONTROL_POINTS = 3\nCENTER_CONTROL_LIMIT = 7.0\nCONNECTION_ANGLE_LIMIT = 5.0\nKEEP_LINE_TANGENT = True\nKEEP_CURVE_TANGENT = True\nINTEGER_COORDINATES = True\nADD_MIDPOINT = False\nMERGE_ADJACENT_CURVES = True\n\n'
ENTRY_POINT='\nif __name__ == "__main__":\n    glyphs_main(MAX_OUTLINE_DEVIATION,MAX_CONTROL_POINTS,ADD_MIDPOINT,MERGE_ADJACENT_CURVES,CENTER_CONTROL_LIMIT,INTEGER_COORDINATES,CONNECTION_ANGLE_LIMIT,KEEP_LINE_TANGENT,KEEP_CURVE_TANGENT)\n'


def render_engine(development,modules=MODULES):
    """Assemble source without importing it or writing generated artifacts."""
    chunks=[]
    for name in modules:
        text=(Path(development)/(name+'.py')).read_text(encoding='utf-8')
        lines=text.splitlines();remove=set()
        for node in ast.walk(ast.parse(text)):
            if isinstance(node,ast.ImportFrom) and node.module in modules:
                remove.update(range(node.lineno-1,node.end_lineno))
        chunks.append('\n'.join(line for i,line in enumerate(lines) if i not in remove))
    return '# -*- coding: utf-8 -*-\n# Copyright 2026 Zonz\n'+'\n\n'.join(chunks)+'\n'


def render_artifacts(root=ROOT,modules=MODULES):
    """Render and validate every output before starting any writes."""
    root=Path(root);engine=render_engine(root/'development',modules)
    resources=root/'CubicToCompactQuadratic.glyphsPlugin/Contents/Resources'
    artifacts={}
    # Source-only checkouts can build the standalone script independently.
    if resources.is_dir():artifacts[resources/'Zonz_quad_engine.py']=engine
    artifacts[root/'CubicToCompactQuadratic.py']=HEADER+engine+ENTRY_POINT
    for path,text in artifacts.items():compile(text,str(path),'exec')
    return artifacts


def build(root=ROOT,modules=MODULES):
    artifacts=render_artifacts(root,modules)
    for path,text in artifacts.items():path.write_text(text,encoding='utf-8')
    return tuple(artifacts)


def main():
    build()


if __name__=='__main__':main()
