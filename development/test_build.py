"""The builder renders independently and validates before overwriting outputs."""
import importlib.util
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parent.parent
SPEC=importlib.util.spec_from_file_location('project_build',ROOT/'build.py')
builder=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(builder)


class BuildTests(unittest.TestCase):
    def test_import_does_not_rebuild_or_write_files(self):
        with patch.object(Path,'write_text') as write:
            runpy.run_path(str(ROOT/'build.py'),run_name='build_library')
        write.assert_not_called()

    def test_rendered_project_matches_checked_in_artifacts_without_writes(self):
        with patch.object(Path,'write_text') as write:artifacts=builder.render_artifacts(ROOT)
        write.assert_not_called()
        self.assertEqual(len(artifacts),2)
        for path,text in artifacts.items():self.assertEqual(text,path.read_text(encoding='utf-8'))

    def test_source_only_project_builds_a_runnable_standalone_script(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'development').mkdir()
            (root/'development/mini.py').write_text('VALUE=7\ndef glyphs_main(*args):pass\n')
            self.assertEqual(builder.build(root,('mini',)),(root/'CubicToCompactQuadratic.py',))
            self.assertFalse((root/'CubicToCompactQuadratic.glyphsPlugin').exists())
            subprocess.run([sys.executable,'-B',str(root/'CubicToCompactQuadratic.py')],check=True)

    def test_invalid_combined_source_leaves_both_existing_outputs_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);dev=root/'development';dev.mkdir()
            resources=root/'CubicToCompactQuadratic.glyphsPlugin/Contents/Resources';resources.mkdir(parents=True)
            (dev/'first.py').write_text('VALUE=1\n')
            (dev/'second.py').write_text('from __future__ import annotations\n')
            engine=resources/'Zonz_quad_engine.py';script=root/'CubicToCompactQuadratic.py'
            engine.write_text('old engine');script.write_text('old script')
            # Each module parses alone; their concatenation has a misplaced
            # future import. Both artifacts must be validated before writing.
            with self.assertRaises(SyntaxError):builder.build(root,('first','second'))
            self.assertEqual(engine.read_text(),'old engine');self.assertEqual(script.read_text(),'old script')


if __name__=='__main__':unittest.main()
