# -*- coding: utf-8 -*-
"""Compact quadratic conversion and native settings panel. Copyright 2026 Zonz."""
import objc
import math
import time
from decimal import Decimal,InvalidOperation,localcontext
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from GlyphsApp import Glyphs,PATH_MENU
from GlyphsApp.plugins import GeneralPlugin
from AppKit import (NSMenuItem,NSPanel,NSTextField,NSProgressIndicator,NSButton,NSFont,NSEvent,NSColor,
                    NSWindowStyleMaskTitled,NSWindowStyleMaskClosable,NSWindowStyleMaskFullSizeContentView,NSBackingStoreBuffered,
                    NSWindowTitleHidden,NSWindowCloseButton,NSWindowMiniaturizeButton,NSWindowZoomButton,
                    NSTextAlignmentRight,NSEventModifierFlagCommand,NSEventModifierFlagShift,NSButtonTypeSwitch,NSLineBreakByWordWrapping,NSLineBreakByClipping,NSFontAttributeName,NSEventModifierFlagOption)
from Foundation import NSTimer,NSMakeRect,NSMakePoint,NSString
from Zonz_quad_engine import make_job,fit_corresponding,fit_run_corresponding,show_message,tr,load_settings,save_settings,validated_settings


SETTING_CONTROLS=(('deviation','_deviation_field'),('max_controls','_count_field'),
                  ('center_limit','_center_field'),('angle_limit','_angle_field'),
                  ('keep_line_tangent','_tangent_check'),('keep_curve_tangent','_curve_tangent_check'),('merge_curves','_merge_check'),
                  ('add_midpoint','_midpoint_check'),('integer_coords','_integer_check'))

class ZonzSettingsCheckbox(NSButton):
    def acceptsFirstResponder(self):return True

    def canBecomeKeyView(self):return self.isEnabled() and not self.isHidden()


class ZonzCubicToQuadraticPlugin(GeneralPlugin):
    @objc.python_method
    def settings(self):
        self.name='Compact Quadratic Curves'
        self._busy=False;self._timer=None;self._job=None;self._panel=None
        self._settings_panel=None;self._settings_close_origin=None;self._settings_control_frames=[];self._started_at=0
        self._executor=ThreadPoolExecutor(max_workers=1)
        load_settings(Glyphs)

    @objc.python_method
    def start(self):
        self._item=NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(tr('title'),self.convert_,'2')
        self._item.setTarget_(self)
        self._item.setKeyEquivalentModifierMask_(NSEventModifierFlagCommand|NSEventModifierFlagShift)
        Glyphs.menu[PATH_MENU].append(self._item)
        self._settings_item=NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(tr('settings'),self.openSettings_,'2')
        self._settings_item.setTarget_(self)
        self._settings_item.setKeyEquivalentModifierMask_(NSEventModifierFlagCommand|NSEventModifierFlagShift|NSEventModifierFlagOption)
        self._settings_item.setAlternate_(True)
        Glyphs.menu[PATH_MENU].append(self._settings_item)

    @objc.python_method
    def label(self,view,text,rect,single_line=False):
        field=NSTextField.alloc().initWithFrame_(NSMakeRect(*rect))
        field.setEditable_(False);field.setSelectable_(False)
        field.setBezeled_(False);field.setDrawsBackground_(False)
        field.setStringValue_(text)
        field.cell().setUsesSingleLineMode_(single_line)
        field.cell().setWraps_(not single_line);field.cell().setScrollable_(False)
        field.cell().setLineBreakMode_(NSLineBreakByClipping if single_line else NSLineBreakByWordWrapping)
        field.setFont_(NSFont.systemFontOfSize_(NSFont.systemFontSize()))
        view.addSubview_(field);return field

    @objc.python_method
    def button(self,view,title,rect,action,key=''):
        button=NSButton.alloc().initWithFrame_(NSMakeRect(*rect))
        button.setTitle_(title);button.setBezelStyle_(1);button.setTarget_(self)
        button.setFont_(NSFont.systemFontOfSize_(NSFont.systemFontSize()))
        button.setAction_(action);button.setKeyEquivalent_(key)
        view.addSubview_(button);return button

    @objc.python_method
    def checkbox(self,view,title,rect):
        button=ZonzSettingsCheckbox.alloc().initWithFrame_(NSMakeRect(*rect))
        button.setButtonType_(NSButtonTypeSwitch);button.setTitle_(title)
        button.setFont_(NSFont.systemFontOfSize_(NSFont.systemFontSize()))
        view.addSubview_(button);return button

    def openSettings_(self,sender):
        if self._busy:
            if self._panel is not None:self._panel.orderFront_(None)
            return
        if self._settings_panel is None:
            font=NSFont.systemFontOfSize_(NSFont.systemFontSize())
            labels=('deviation','max_controls','center_limit','angle_limit','keep_line_tangent','keep_curve_tangent','merge_curves','midpoint','integer_coords')
            measure=lambda text:NSString.stringWithString_(text).sizeWithAttributes_({NSFontAttributeName:font}).width
            margin=22;gap=12;number_width=22;check_width=20;label_padding=8;height=318
            width=math.ceil(max(max(measure(tr(k))+label_padding+2*margin+gap+number_width for k in labels[:4]),
                               max(measure(tr(k))+label_padding+2*margin+gap+check_width for k in labels[4:])))
            panel=NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
                NSMakeRect(0,0,width,height),NSWindowStyleMaskTitled|NSWindowStyleMaskClosable|NSWindowStyleMaskFullSizeContentView,
                NSBackingStoreBuffered,False)
            panel.setReleasedWhenClosed_(False);panel.setTitle_(tr('settings'));panel.setFloatingPanel_(True)
            panel.setTitleVisibility_(NSWindowTitleHidden);panel.setTitlebarAppearsTransparent_(True)
            panel.setMovableByWindowBackground_(True);panel.setOpaque_(True);panel.setBackgroundColor_(NSColor.windowBackgroundColor())
            for kind in (NSWindowMiniaturizeButton,NSWindowZoomButton):
                button=panel.standardWindowButton_(kind)
                if button is not None:button.setHidden_(True)
            view=panel.contentView()
            self._settings_panel=panel;right=width-margin
            for index,((key,attribute),label) in enumerate(zip(SETTING_CONTROLS,labels)):
                y=height-44.5-32*index;numeric=index<4;control_width=number_width if numeric else check_width
                self.label(view,tr(label),(margin,y+1,width-2*margin-gap-control_width,22),single_line=True)
                frame=(right-control_width,y+3.5 if numeric else y+2.5,control_width,22 if numeric else 24)
                if numeric:
                    control=NSTextField.alloc().initWithFrame_(NSMakeRect(*frame))
                    control.setFont_(font);control.setAlignment_(NSTextAlignmentRight);control.setDelegate_(self)
                    control.cell().setUsesSingleLineMode_(True);control.cell().setScrollable_(True);view.addSubview_(control)
                else:
                    control=self.checkbox(view,'',frame)
                    control.setTarget_(self);control.setAction_(self.changeSetting_)
                control.setAccessibilityLabel_(tr(label));setattr(self,attribute,control)
                self._settings_control_frames.append((control,frame))
            controls=[getattr(self,attribute) for key,attribute in SETTING_CONTROLS]
            panel.setAutorecalculatesKeyViewLoop_(False)
            panel.setInitialFirstResponder_(controls[0])
            for current,following in zip(controls,controls[1:]+controls[:1]):current.setNextKeyView_(following)
        self.fill_settings(load_settings(Glyphs))
        self._settings_panel.center();self._settings_panel.makeKeyAndOrderFront_(None)
        offset=1.0
        for control,(x,y,width,height) in self._settings_control_frames:
            control.setFrame_(NSMakeRect(x,y-offset,width,height))
        close=self._settings_panel.standardWindowButton_(NSWindowCloseButton)
        if close is not None:
            if self._settings_close_origin is None:
                origin=close.frame().origin;parent=close.superview()
                self._settings_close_origin=NSMakePoint(origin.x+2,origin.y+(2 if parent is not None and parent.isFlipped() else -2))
            close.setFrameOrigin_(self._settings_close_origin)
        self._settings_panel.makeFirstResponder_(self._deviation_field)

    @objc.python_method
    def fill_control(self,key,control,value):
        if key in ('deviation','center_limit','angle_limit'):
            control.setStringValue_(str(int(value)) if value.is_integer() else repr(value))
        elif key=='max_controls':control.setStringValue_(str(value))
        else:control.setState_(int(value))

    @objc.python_method
    def fill_settings(self,values):
        self._settings_values=dict(values)
        for key,attribute in SETTING_CONTROLS:self.fill_control(key,getattr(self,attribute),values[key])

    @objc.python_method
    def setting_key(self,control):
        return next((key for key,attribute in SETTING_CONTROLS if control==getattr(self,attribute)),None)

    @objc.python_method
    def persist_control(self,control,text=None):
        key=self.setting_key(control)
        if key is None:return False
        values=dict(self._settings_values)
        values[key]=(control.stringValue() if text is None else text).strip().replace(',','.') if key in ('deviation','max_controls','center_limit','angle_limit') else bool(control.state())
        try:values=validated_settings(**values)
        except ValueError:return False
        if values!=self._settings_values:self._settings_values=save_settings(Glyphs,**values)
        return True

    def changeSetting_(self,sender):
        self.persist_control(sender)

    def controlTextDidChange_(self,notification):
        control=notification.object();info=notification.userInfo() or {};editor=info.get('NSFieldEditor')
        if editor is not None and editor.hasMarkedText():return
        self.persist_control(control,editor.string() if editor is not None else None)

    def controlTextDidEndEditing_(self,notification):
        control=notification.object();key=self.setting_key(control)
        if key is not None and not self.persist_control(control):self.fill_control(key,control,self._settings_values[key])

    def control_textView_doCommandBySelector_(self,control,textView,command):
        up=('moveUp:','moveUpAndModifySelection:');down=('moveDown:','moveDownAndModifySelection:')
        if command not in up+down or textView.hasMarkedText():return False
        if self.setting_key(control) not in ('deviation','max_controls','center_limit','angle_limit'):return False
        shifted=command.endswith('AndModifySelection:') or bool(NSEvent.modifierFlags()&NSEventModifierFlagShift)
        step=(1 if command in up else -1)*(10 if shifted else 1)
        source=textView.string().strip().replace(',','.')
        try:
            if control==self._count_field:text=str(max(1,int(source)+step))
            else:
                value=Decimal(source)
                if not value.is_finite() or not math.isfinite(float(value)):return False
                increment=Decimal('0.1') if control==self._deviation_field else Decimal(1)
                with localcontext() as context:
                    context.prec=max(28,len(value.as_tuple().digits)+1,value.adjusted()+2,1-value.as_tuple().exponent)
                    value+=increment*step
                if control==self._deviation_field:
                    if value<=0 or not math.isfinite(float(value)):return True
                else:
                    value=max(Decimal(0),value)
                    if control==self._angle_field:value=min(Decimal(180),value)
                text=format(value,'f')
                if '.' in text:text=text.rstrip('0').rstrip('.')
        except (ValueError,InvalidOperation,OverflowError):return False
        if text!=source:
            textView.setString_(text);control.setStringValue_(text);textView.didChangeText()
            textView.setSelectedRange_((len(text),0));self.persist_control(control,text)
        return True

    @objc.python_method
    def open_progress(self):
        self._panel=NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0,0,440,128),NSWindowStyleMaskTitled,NSBackingStoreBuffered,False)
        self._panel.setTitle_(tr('title'));self._panel.setReleasedWhenClosed_(False)
        self._panel.setFloatingPanel_(True);self._panel.setBecomesKeyOnlyIfNeeded_(True)
        view=self._panel.contentView()
        self._label=self.label(view,tr('preparing'),(20,80,400,24))
        self._progress=NSProgressIndicator.alloc().initWithFrame_(NSMakeRect(20,55,400,16))
        self._progress.setIndeterminate_(False);self._progress.setMinValue_(0)
        self._progress.setMaxValue_(1);self._progress.setDoubleValue_(0)
        view.addSubview_(self._progress)
        self.button(view,tr('cancel'),(330,12,90,28),self.cancel_,'\x1b')
        self._panel.center();self._panel.makeKeyAndOrderFront_(None)

    @objc.python_method
    def fit_async(self,curves,tolerance,max_controls,progress,merge=False,cyclic=False,center_limit=0.0,integer_step=0.0,explicit_midpoint=False,**geometry_options):
        cancelled=Event()
        function=fit_run_corresponding if merge else fit_corresponding
        options=dict(cancel=cancelled.is_set,**geometry_options)
        if center_limit or integer_step:options.update(center_limit=center_limit,integer_step=integer_step,explicit_midpoint=explicit_midpoint)
        if merge:options['cyclic']=cyclic
        future=self._executor.submit(function,curves,tolerance,max_controls,**options)
        try:
            while not future.done():yield progress
            return future.result()
        finally:
            cancelled.set();future.cancel()

    def convert_(self,sender):
        if self._busy:
            if self._panel is not None:self._panel.orderFront_(None)
            return
        try:
            values=load_settings(Glyphs)
            self._job=make_job(tolerance=values['deviation'],max_controls=values['max_controls'],
                               add_midpoint=values['add_midpoint'],fit_runner=self.fit_async,merge_curves=values['merge_curves'],
                               center_limit=values['center_limit'],integer_coords=values['integer_coords'],
                               angle_limit=values['angle_limit'],keep_line_tangent=values['keep_line_tangent'],keep_curve_tangent=values['keep_curve_tangent'])
            self._busy=True;self._started_at=time.monotonic()
            self._timer=NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
                .01,self,'advance:',None,True)
        except Exception as exc:
            self.finish();show_message(str(exc))

    def advance_(self,timer):
        try:
            progress=next(self._job)
            if progress['done']>=progress['total']:
                next(self._job)
            if self._panel is None and time.monotonic()-self._started_at>=1:
                self.open_progress()
            if self._panel is not None:
                self._label.setStringValue_('{}  {}/{}'.format(progress['glyph'],progress['done'],progress['total']))
                self._progress.setMaxValue_(max(1,progress['total']));self._progress.setDoubleValue_(progress['done'])
        except StopIteration as done:
            self.finish()
            if done.value:Glyphs.redraw()
        except Exception as exc:
            import traceback
            traceback.print_exc();self.finish();show_message(str(exc))

    def cancel_(self,sender):
        if self._job is not None:self._job.close()
        self.finish()

    @objc.python_method
    def finish(self):
        if self._timer is not None:self._timer.invalidate()
        if self._panel is not None:self._panel.close()
        self._timer=None;self._job=None;self._panel=None;self._busy=False

    @objc.python_method
    def __file__(self):
        return __file__
