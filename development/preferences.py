# -*- coding: utf-8 -*-
"""Validated settings; deviation and distances are units on the UPM 1000 scale."""
import math
import struct
from i18n import tr

PREFERENCE_PREFIX='com.Zonz.CubicToQuadratic.'
DEFAULT_SETTINGS=dict(deviation=1.0,max_controls=3,add_midpoint=False,merge_curves=True,center_limit=7.0,integer_coords=True,angle_limit=5.0,keep_line_tangent=True,keep_curve_tangent=True)

def validated_settings(deviation=1.0,max_controls=2,add_midpoint=False,merge_curves=False,center_limit=0.0,integer_coords=False,angle_limit=2.0,keep_line_tangent=False,keep_curve_tangent=False):
    try:
        deviation=float(deviation)
        if deviation<=0 or not math.isfinite(deviation):raise ValueError()
    except (ValueError,TypeError,OverflowError):raise ValueError(tr('invalid'))
    try:
        center_limit=float(center_limit)
        if center_limit<0 or not math.isfinite(center_limit):raise ValueError()
    except (ValueError,TypeError,OverflowError):raise ValueError(tr('invalid_center'))
    try:
        angle_limit=float(angle_limit)
        if not math.isfinite(angle_limit) or not 0<=angle_limit<=180:raise ValueError()
    except (ValueError,TypeError,OverflowError):raise ValueError(tr('invalid_angle'))
    try:
        if isinstance(max_controls,bool):raise ValueError()
        count=int(max_controls)
        if count<1 or (not isinstance(max_controls,(int,str)) and count!=max_controls):raise ValueError()
    except (ValueError,TypeError,OverflowError):raise ValueError(tr('invalid_count'))
    return dict(deviation=deviation,max_controls=count,add_midpoint=bool(add_midpoint),
                merge_curves=bool(merge_curves),
                center_limit=center_limit,integer_coords=bool(integer_coords),angle_limit=angle_limit,keep_line_tangent=bool(keep_line_tangent),keep_curve_tangent=bool(keep_curve_tangent))

def stored(app,key):
    try:return app.defaults[PREFERENCE_PREFIX+key]
    except KeyError:return None

def decimal_preference(value):
    if not isinstance(value,float) or not math.isfinite(value):return value
    try:
        packed=struct.pack('f',value)
        if struct.unpack('f',packed)[0]!=value:return value
        for precision in range(1,10):
            text=format(value,'.'+str(precision)+'g')
            if struct.pack('f',float(text))==packed:return text
    except (OverflowError,struct.error):pass
    return value

def encoded_settings(values):
    return {PREFERENCE_PREFIX+k:str(v) if k in ('deviation','max_controls','center_limit','angle_limit') else v for k,v in values.items()}

def load_settings(app):
    values={k:stored(app,k) for k in DEFAULT_SETTINGS}
    if values['deviation'] is not None:values['deviation']=decimal_preference(values['deviation'])
    values={k:DEFAULT_SETTINGS[k] if v is None else v for k,v in values.items()}
    try:values=validated_settings(**values)
    except ValueError:values=dict(DEFAULT_SETTINGS)
    # Persist validated text values instead of binary32 numeric preferences.
    for key,value in encoded_settings(values).items():app.defaults[key]=value
    return values

def save_settings(app,**values):
    settings=validated_settings(**values)
    for key,value in encoded_settings(settings).items():app.defaults[key]=value
    return settings
