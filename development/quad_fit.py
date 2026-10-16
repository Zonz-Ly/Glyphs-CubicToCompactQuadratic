# -*- coding: utf-8 -*-
"""Bezier primitives and algebraic seeds; geometric fitting is in fast_fit."""
import math
VERSION = '1.0'

def dot(a, b):
    return (a.conjugate() * b).real

def cross(a, b):
    return (a.conjugate() * b).imag

def cubic(p, t):
    u = 1.0 - t
    return u*u*u*p[0] + 3*u*u*t*p[1] + 3*u*t*t*p[2] + t*t*t*p[3]

def quadratic(q, t):
    u = 1.0 - t
    return u*u*q[0] + 2*u*t*q[1] + t*t*q[2]

def split(p, t=0.5):
    a, b, c = [(1-t)*p[i]+t*p[i+1] for i in range(3)]
    d, e = (1-t)*a+t*b, (1-t)*b+t*c
    m = (1-t)*d+t*e
    return (p[0], a, d, m), (m, e, c, p[3])

def single_l2(p):
    return (p[0], (3*p[1]+3*p[2]-p[0]-p[3])/4.0, p[3])

def solve(a, b):
    """Small positive-definite systems, with partial pivoting."""
    n = len(b)
    m = [list(row)+[v] for row, v in zip(a, b)]
    scale = max(abs(v) for row in a for v in row)
    for col in range(n):
        pivot = max(range(col, n), key=lambda j: abs(m[j][col]))
        if abs(m[pivot][col]) <= 1e-13*max(scale, 1e-300):
            raise ValueError('Singular fitting system')
        m[col], m[pivot] = m[pivot], m[col]
        div = m[col][col]
        m[col] = [v/div for v in m[col]]
        for j in range(n):
            if j != col:
                f = m[j][col]
                m[j] = [x-f*y for x, y in zip(m[j], m[col])]
    return [row[-1] for row in m]

def tangent(p, end=False):
    anchor = p[-1] if end else p[0]
    seq = (p[2], p[1], p[0]) if end else (p[1], p[2], p[3])
    for point in seq:
        v = point-anchor
        if abs(v) > 1e-12:
            return v/abs(v)
    return None

def weights(p, power=2.0):
    lengths = (abs(p[1]-p[0]), abs(p[2]-p[3]))
    top = max(lengths)
    return tuple((v/top)**power if top and v else 0.0 for v in lengths)

def single_weighted(p, strength=1.0, power=2.0):
    q = single_l2(p)[1]
    mat = [[1.0, 0.0], [0.0, 1.0]]
    rhs = [q.real, q.imag]
    for end, w in zip((False, True), weights(p, power)):
        u = tangent(p, end)
        if u is None or not w:
            continue
        n = 1j*u
        anchor = p[3] if end else p[0]
        v = (n.real, n.imag)
        amount = strength*w
        for i in range(2):
            rhs[i] += amount*v[i]*dot(n, anchor)
            for j in range(2):
                mat[i][j] += amount*v[i]*v[j]
    x, y = solve(mat, rhs)
    return (p[0], complex(x, y), p[3])

def intersection(p):
    u, v = tangent(p), tangent(p, True)
    if u is None or v is None:
        return None
    den = cross(u, v)
    if abs(den) < 1e-10:
        return None
    d = p[3]-p[0]
    a, b = cross(d, v)/den, cross(d, u)/den
    if a <= 1e-12 or b <= 1e-12:
        return None
    return (p[0], p[0]+a*u, p[3])

def pair_basis(s, half):
    """Q = base + b0*q0 + b1*q1, M=(q0+q1)/2."""
    if half == 0:
        return (2*s-1.5*s*s, 0.5*s*s, (1-s)**2, 0.0)
    return (0.5*(1-s)**2, 0.5*(1-s)**2+2*s*(1-s), 0.0, s*s)

def pair_l2(p):
    a, b = split(p)
    return [single_l2(a), single_l2(b)]

def angle(a, b):
    if abs(a) <= 1e-12 or abs(b) <= 1e-12:
        return None
    return math.degrees(math.atan2(cross(a, b), dot(a, b)))

def diagnostics(p, parts):
    return (angle(p[1]-p[0], parts[0][1]-parts[0][0]),
            angle(p[2]-p[3], parts[-1][1]-parts[-1][2]))
