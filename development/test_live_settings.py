# -*- coding: utf-8 -*-
import sys,unittest
from types import SimpleNamespace
from unittest.mock import patch
from mock_glyphs import Font,glyph,Node,Point,CONSTANTS
from test_entrypoints import modules,plugin_files,load
from test_merge import elevated,pieces,joined_font
from test_settings import finish
from glyphs_adapter import conversion_steps
from geometry_fit import geometric_bounds
from preferences import DEFAULT_SETTINGS,load_settings,save_settings

class Editor:
    def __init__(self,text,marked=False):self.text=text;self.marked=marked;self.changes=0
    def string(self):return self.text
    def hasMarkedText(self):return self.marked
    def setString_(self,text):self.text=text
    def didChangeText(self):self.changes+=1
    def setSelectedRange_(self,selection):self.selection=selection

def notification(control,editor=None):
    return SimpleNamespace(object=lambda:control,userInfo=lambda:{'NSFieldEditor':editor} if editor is not None else {})

class LiveSettingsTests(unittest.TestCase):
    def setUp(self):
        self.env=modules(Font([glyph()]));self.app=self.env['GlyphsApp'].Glyphs
        root,res=plugin_files();engine=load(res/'Zonz_quad_engine.py','Zonz_quad_engine')
        context=patch.dict(sys.modules,dict(self.env,Zonz_quad_engine=engine));context.start();self.addCleanup(context.stop)
        self.module=load(res/'plugin.py','live_settings');self.plugin=self.module.ZonzCubicToQuadraticPlugin()
        self.plugin.settings();self.plugin.openSettings_(None)

    def type_value(self,field,text):
        field.setStringValue_(text);self.plugin.controlTextDidChange_(notification(field))

    def step(self,field,text,command='moveUp:',marked=False):
        field.setStringValue_(text);editor=Editor(text,marked)
        handled=self.plugin.control_textView_doCommandBySelector_(field,editor,command)
        return handled,editor

    def test_square_fields_centered_rows_and_complete_key_loop(self):
        p=self.plugin;window=p._settings_panel
        controls=[getattr(p,attribute) for key,attribute in self.module.SETTING_CONTROLS]
        labels=[child for child in window.children if child not in controls]
        for index,(label,control) in enumerate(zip(labels,controls)):
            control_frame=control.calls['initWithFrame_'][0]
            label_frame=label.calls['initWithFrame_'][0]
            original_y=318-44.5-32*index
            self.assertEqual(label_frame[1],original_y+1)
            self.assertEqual(label_frame[3],22)
            self.assertEqual(control_frame[1]+control_frame[3]/2,original_y+14.5)
            self.assertIs(control.calls['setNextKeyView_'][0],controls[(index+1)%len(controls)])
            if index<4:
                self.assertEqual(control_frame[2:],(22,22))
                self.assertEqual(control.calls['setScrollable_'],(True,))
            else:
                self.assertTrue(control.acceptsFirstResponder());self.assertTrue(control.canBecomeKeyView())
                control.setEnabled_(False);self.assertFalse(control.canBecomeKeyView());control.setEnabled_(True)
        self.assertEqual(window.calls['setAutorecalculatesKeyViewLoop_'],(False,))
        self.assertIs(window.calls['setInitialFirstResponder_'][0],controls[0])

    def test_fixed_control_offset_keeps_original_text_positions_and_uniform_gap(self):
        p=self.plugin;controls=[control for control,frame in p._settings_control_frames]
        labels=[child for child in p._settings_panel.children if child not in controls]
        before=[label.calls['initWithFrame_'] for label in labels]
        for scale in (2.,1.,2.):
            with patch.object(p._settings_panel,'backingScaleFactor',return_value=scale) as backing:
                p.openSettings_(None)
                backing.assert_not_called()
            for control,(x,y,width,height) in p._settings_control_frames:
                self.assertEqual(control.calls['setFrame_'][0],(x,y-1,width,height))
            self.assertEqual([label.calls['initWithFrame_'] for label in labels],before)
        ys=[label.calls['initWithFrame_'][0][1] for label in labels]
        self.assertEqual([a-b for a,b in zip(ys,ys[1:])],[32]*8)
        self.assertTrue(all('setFrame_' not in label.calls for label in labels))

    def test_release_defaults(self):
        self.assertEqual(DEFAULT_SETTINGS,dict(deviation=1,max_controls=3,center_limit=7.,angle_limit=5.,
            keep_line_tangent=True,keep_curve_tangent=True,merge_curves=True,integer_coords=True,add_midpoint=False))
        self.assertEqual(load_settings(self.app),DEFAULT_SETTINGS)

    def test_existing_custom_values_survive_opening(self):
        saved=save_settings(self.app,deviation=.05,max_controls=7,center_limit=0,angle_limit=1,
            keep_line_tangent=False,merge_curves=False,integer_coords=False,add_midpoint=True)
        self.plugin.openSettings_(None)
        self.assertEqual(load_settings(self.app),saved);self.assertEqual(self.plugin._count_field.stringValue(),'7')

    def test_close_button_only_and_compact_opaque_background(self):
        p=self.plugin;window=p._settings_panel;view=window.contentView();m=self.module
        self.assertEqual(len(view.children),18)
        self.assertTrue(window.calls['initWithContentRect_styleMask_backing_defer_'][1]&m.NSWindowStyleMaskFullSizeContentView)
        self.assertEqual(window.calls['setTitleVisibility_'],(m.NSWindowTitleHidden,))
        self.assertEqual(window.calls['setTitlebarAppearsTransparent_'],(True,))
        self.assertEqual(window.calls['setMovableByWindowBackground_'],(True,))
        for kind in (m.NSWindowMiniaturizeButton,m.NSWindowZoomButton):
            self.assertEqual(window.window_buttons[kind].calls['setHidden_'],(True,))
        close=window.window_buttons[m.NSWindowCloseButton]
        origin=close.calls['setFrameOrigin_'][0]
        self.assertEqual((origin.x,origin.y),(9,5))
        self.assertEqual(window.calls['setOpaque_'],(True,))
        self.assertEqual(window.calls['setBackgroundColor_'],('window background',))
        self.assertNotIn('setContentView_',window.calls)
        height=window.calls['initWithContentRect_styleMask_backing_defer_'][0][3]
        self.assertEqual(height,318)
        frames=[x.calls.get('setFrame_',x.calls['initWithFrame_'])[0] for x in view.children]
        self.assertGreaterEqual(min(r[1] for r in frames),18.5)
        self.assertGreaterEqual(height-max(r[1]+r[3] for r in frames),20)
        self.assertFalse(hasattr(p,'saveSettings_'));self.assertFalse(hasattr(p,'closeSettings_'))

    def test_valid_typing_saves_immediately_and_survives_closing(self):
        p=self.plugin;self.type_value(p._deviation_field,'0,05')
        self.assertEqual(load_settings(self.app)['deviation'],.05)
        self.assertFalse(p._settings_panel.closed)
        p._settings_panel.close();p.openSettings_(None)
        self.assertEqual(p._deviation_field.stringValue(),'0.05')

    def test_invalid_intermediate_input_does_not_overwrite_valid_value_or_alert(self):
        p=self.plugin;self.type_value(p._deviation_field,'0.05');before=dict(self.app.defaults)
        with patch.object(self.env['GlyphsApp'],'Message') as message:
            for text in ('','-','0','NaN','Infinity','.'):
                self.type_value(p._deviation_field,text);self.assertEqual(self.app.defaults,before)
            message.assert_not_called()
        p.controlTextDidEndEditing_(notification(p._deviation_field))
        self.assertEqual(p._deviation_field.stringValue(),'0.05')

    def test_one_invalid_field_does_not_block_another_setting(self):
        p=self.plugin;self.type_value(p._deviation_field,'-')
        p._merge_check.setState_(0);p.changeSetting_(p._merge_check)
        self.assertFalse(load_settings(self.app)['merge_curves'])
        self.assertEqual(p._deviation_field.stringValue(),'-')
        self.assertEqual(load_settings(self.app)['deviation'],1)

    def test_checkbox_actions_save_each_option_independently(self):
        p=self.plugin
        for key,attribute in self.module.SETTING_CONTROLS[4:]:
            control=getattr(p,attribute);self.assertIs(control.calls['setTarget_'][0],p)
            control.setState_(int(not load_settings(self.app)[key]));control.calls['setAction_'][0](control)
            self.assertEqual(load_settings(self.app)[key],bool(control.state()))

    def test_live_field_editor_and_ime_marked_text(self):
        p=self.plugin;field=p._center_field;field.setStringValue_('3')
        p.controlTextDidChange_(notification(field,Editor('2,5')))
        self.assertEqual(load_settings(self.app)['center_limit'],2.5)
        p.controlTextDidChange_(notification(field,Editor('99',True)))
        self.assertEqual(load_settings(self.app)['center_limit'],2.5)

    def test_arrow_decimal_steps_save_without_float_tails(self):
        p=self.plugin;handled,editor=self.step(p._deviation_field,'0.05')
        self.assertTrue(handled);self.assertEqual(editor.text,'0.15')
        self.assertEqual(load_settings(self.app)['deviation'],.15)
        self.assertTrue(p.control_textView_doCommandBySelector_(p._deviation_field,editor,'moveDown:'))
        self.assertEqual(editor.text,'0.05');self.assertEqual(load_settings(self.app)['deviation'],.05)

    def test_shift_and_large_integer_steps(self):
        p=self.plugin
        for field,text,want in ((p._deviation_field,'0.05','1.05'),(p._count_field,'3','13'),
                (p._center_field,'2.5','12.5'),(p._angle_field,'3','13')):
            handled,editor=self.step(field,text,'moveUpAndModifySelection:')
            self.assertTrue(handled);self.assertEqual(editor.text,want)
            self.assertTrue(p.control_textView_doCommandBySelector_(field,editor,'moveDownAndModifySelection:'))
            self.assertEqual(editor.text,text)
        with patch.object(self.module.NSEvent,'modifierFlags',return_value=self.module.NSEventModifierFlagShift):
            self.assertEqual(self.step(p._deviation_field,'1')[1].text,'2')
        number=10**40;self.assertEqual(self.step(p._count_field,str(number))[1].text,str(number+1))

    def test_numeric_boundaries_and_native_editing(self):
        p=self.plugin
        for field,text,command,want in ((p._deviation_field,'0.05','moveDown:','0.05'),
                (p._count_field,'1','moveDown:','1'),(p._center_field,'0.1','moveDown:','0'),
                (p._angle_field,'175','moveUpAndModifySelection:','180')):
            handled,editor=self.step(field,text,command);self.assertTrue(handled);self.assertEqual(editor.text,want)
        for command in ('moveLeft:','insertTab:','insertNewline:','cancelOperation:'):
            self.assertFalse(self.step(p._center_field,'2',command)[0])
        self.assertFalse(self.step(p._center_field,'2',marked=True)[0])
        for text in ('','bad','NaN','Infinity'):
            self.assertFalse(self.step(p._center_field,text)[0])

    def test_duplicate_notifications_do_not_repeat_preference_writes(self):
        p=self.plugin
        with patch.object(self.module,'save_settings',wraps=self.module.save_settings) as saved:
            self.type_value(p._deviation_field,'0.05');self.type_value(p._deviation_field,'0.050')
            self.assertEqual(saved.call_count,1)

    def test_ordinary_and_merged_centering_use_half_tolerance_at_each_upm(self):
        q=(0j,20+5j,100+0j);source=elevated(q)
        for scale in (1.,2.,2.048):
            for merged in (False,True):
                with self.subTest(scale=scale,merged=merged):
                    chain=pieces(source) if merged else (source,)
                    chain=tuple(tuple(z*scale for z in p) for p in chain)
                    f,g=joined_font((chain,));f.upm=scale*1000
                    finish(conversion_steps(f,Node,Point,CONSTANTS,tolerance=.8,max_controls=2,
                        center_limit=6,merge_curves=merged))
                    nodes=g.layers[0].paths[0].nodes;self.assertEqual(len(nodes),3)
                    fitted=tuple(complex(n.position.x,n.position.y) for n in nodes)
                    self.assertGreater(fitted[1].real,20*scale)
                    bounds=geometric_bounds(chain[0],[fitted],.4*scale,source_curves=chain if merged else None)
                    self.assertLessEqual(bounds[1],.4*scale)

if __name__=='__main__':unittest.main(verbosity=2)
