import contextlib,importlib.util,io,sys,types,unittest
from pathlib import Path as FilePath
from unittest.mock import patch
from mock_glyphs import *

ROOT=FilePath(__file__).parent
class UI:
    def __init__(self):self.calls={};self.children=[];self.closed=False
    @classmethod
    def alloc(cls):return cls()
    def __getattr__(self,key):
        if key.startswith('init'):
            def init(*args):self.calls[key]=args;return self
            return init
        if key=='setContentView_':
            def content(value):self.view=value;self.calls[key]=(value,)
            return content
        if key=='standardWindowButton_':
            def window_button(kind):
                if 'window_buttons' not in self.__dict__:self.window_buttons={}
                return self.window_buttons.setdefault(kind,UI())
            return window_button
        if key.startswith('set'):
            def set_value(*args):self.calls[key]=args
            return set_value
        if key=='stringValue':return lambda:self.calls.get('setStringValue_',('',))[0]
        if key=='state':return lambda:self.calls.get('setState_',(0,))[0]
        if key=='makeFirstResponder_':return lambda *args:True
        if key=='cellSize':return lambda:types.SimpleNamespace(height=17)
        if key=='isEnabled':return lambda:self.calls.get('setEnabled_',(True,))[0]
        if key=='isHidden':return lambda:self.calls.get('setHidden_',(False,))[0]
        if key=='backingScaleFactor':return lambda:2.0
        if key=='frame':return lambda:types.SimpleNamespace(origin=types.SimpleNamespace(x=7,y=7))
        if key=='superview':return lambda:self
        if key=='isFlipped':return lambda:False
        if key=='contentView':return lambda:self.__dict__.get('view',self)
        if key=='cell':return lambda:self
        if key=='addSubview_':return lambda x:self.children.append(x)
        if key=='close':return lambda:setattr(self,'closed',True)
        if key in ('center','makeKeyAndOrderFront_','orderFront_'):return lambda *args:None
        raise AttributeError(key)
class ImmediateFuture:
    def __init__(self,fn,args,kwargs):self.value=fn(*args,**kwargs)
    def done(self):return True
    def result(self):return self.value
    def cancel(self):return False

class ImmediateExecutor:
    def __init__(self,**kwargs):pass
    def submit(self,fn,*args,**kwargs):return ImmediateFuture(fn,args,kwargs)

class NSString:
    def __init__(self,text):self.text=text
    @classmethod
    def stringWithString_(cls,text):return cls(text)
    def sizeWithAttributes_(self,attrs):
        return types.SimpleNamespace(width=sum(13 if ord(c)>255 else 6.5 for c in self.text))

class Timer:
    def __init__(self):self.invalidated=False
    def invalidate(self):self.invalidated=True
    @classmethod
    def scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(cls,*args):return cls()

def modules(font):
    app=types.SimpleNamespace(font=font,menu={7:[]},localize=lambda x:x['zh'],
        redraw=lambda:font.events.append('redraw'),showNotification=lambda *x:None)
    glyphs=types.ModuleType('GlyphsApp');glyphs.Glyphs=app
    glyphs.GSNode,glyphs.GSPath=Node,Path;glyphs.OFFCURVE,glyphs.CURVE,glyphs.QCURVE=CONSTANTS
    glyphs.INSTANCETYPEVARIABLE=1;glyphs.PATH_MENU=7;glyphs.Message=lambda **kw:None
    plugins=types.ModuleType('GlyphsApp.plugins');plugins.GeneralPlugin=object
    objc=types.ModuleType('objc');objc.python_method=lambda f:f
    foundation=types.ModuleType('Foundation');foundation.NSMakePoint=Point;foundation.NSTimer=Timer
    foundation.NSMakeRect=lambda *v:v
    foundation.NSString=NSString
    appkit=types.ModuleType('AppKit')
    for name in ['NSMenuItem','NSPanel','NSTextField','NSProgressIndicator','NSButton','NSFont']:setattr(appkit,name,UI)
    appkit.NSEvent=types.SimpleNamespace(modifierFlags=lambda:0)
    appkit.NSColor=types.SimpleNamespace(windowBackgroundColor=lambda:'window background')
    for name,value in [('NSWindowStyleMaskTitled',1),('NSBackingStoreBuffered',2),
        ('NSEventModifierFlagCommand',1),('NSEventModifierFlagOption',2),('NSEventModifierFlagControl',4),('NSEventModifierFlagShift',8),('NSWindowStyleMaskClosable',2),('NSButtonTypeSwitch',3),('NSLineBreakByWordWrapping',0),('NSLineBreakByClipping',2),('NSFontAttributeName','font'),('NSTextAlignmentRight',1),('NSWindowStyleMaskFullSizeContentView',32768),('NSWindowTitleHidden',1),('NSWindowCloseButton',0),('NSWindowMiniaturizeButton',1),('NSWindowZoomButton',2)]:
        setattr(appkit,name,value)
    app.defaults={'AppleLanguages':['zh-Hans']}
    app.registerDefaults=lambda values:[app.defaults.setdefault(k,v) for k,v in values.items()]
    def font_of_size(cls,size):
        font=cls();font.calls['size']=size;return font
    appkit.NSFont.systemFontOfSize_=classmethod(font_of_size)
    appkit.NSFont.systemFontSize=classmethod(lambda cls:13)
    return dict(GlyphsApp=glyphs,**{'GlyphsApp.plugins':plugins,'objc':objc,
                                  'Foundation':foundation,'AppKit':appkit})

def plugin_files():
    root=ROOT if (ROOT/'CubicToCompactQuadratic.glyphsPlugin').exists() else ROOT.parent
    resources=root/'CubicToCompactQuadratic.glyphsPlugin/Contents/Resources'
    return root,resources
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,str(path));m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    if path.name=='plugin.py':m.ThreadPoolExecutor=ImmediateExecutor
    return m

class EntryTests(unittest.TestCase):
    def test_complete_standalone_in_font_view(self):
        a,b=glyph('A'),glyph('B');f=Font([a,b],edit=False);f.selection=[a,b]
        root,res=plugin_files()
        with patch.dict(sys.modules,modules(f)),contextlib.redirect_stdout(io.StringIO()):
            exec(compile((root/'CubicToCompactQuadratic.py').read_text(encoding='utf-8'),'CubicToCompactQuadratic.py','exec'),{'__name__':'__main__'})
        self.assertEqual([a.layers[0].paths[0].nodes[-1].type,b.layers[0].paths[0].nodes[-1].type],['qcurve','qcurve'])
        self.assertEqual(f.undo.groups,1);self.assertEqual(f.events,['stop','start','redraw'])

    def test_plugin_menu_shortcut_timer_and_conversion(self):
        g=glyph(sources=(EXACT,PAIR_NEEDED));f=Font([g],2);f.selectedLayers=[g.layers[0]]
        root,res=plugin_files();env=modules(f)
        with patch.dict(sys.modules,env),contextlib.redirect_stdout(io.StringIO()):
            engine=load(res/'Zonz_quad_engine.py','Zonz_quad_engine')
            with patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
                m=load(res/'plugin.py','quad_plugin_test');plugin=m.ZonzCubicToQuadraticPlugin()
                plugin.settings();plugin.start()
                item=env['GlyphsApp'].Glyphs.menu[7][0]
                self.assertEqual(item.calls['initWithTitle_action_keyEquivalent_'][2],'2')
                self.assertEqual(item.calls['setKeyEquivalentModifierMask_'],(9,))
                plugin.convert_(None);timer=plugin._timer;job=plugin._job
                plugin.convert_(None);self.assertIs(plugin._job,job)
                for _ in range(20):
                    if not plugin._busy:break
                    plugin.advance_(timer)
                self.assertFalse(plugin._busy);self.assertTrue(timer.invalidated)
        self.assertTrue(g.mastersCompatible)
        self.assertTrue(all(l.paths[0].nodes[-1].type=='qcurve' for l in g.layers))
        self.assertTrue(all(1<=sum(n.type=='offcurve' for n in l.paths[0].nodes)<=3 for l in g.layers))

    def test_plugin_cancel_leaves_font_untouched(self):
        g=glyph();f=Font([g]);f.selectedLayers=[g.layers[0]];root,res=plugin_files()
        with patch.dict(sys.modules,modules(f)):
            engine=load(res/'Zonz_quad_engine.py','Zonz_quad_engine')
            with patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
                m=load(res/'plugin.py','quad_plugin_cancel');p=m.ZonzCubicToQuadraticPlugin()
                p.settings();p.convert_(None);p.advance_(p._timer);p.cancel_(None)
                self.assertFalse(p._busy)
        self.assertEqual(g.layers[0].paths[0].nodes[-1].type,'curve');self.assertEqual(f.events,[])

if __name__=='__main__':unittest.main(verbosity=2)
