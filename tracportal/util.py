# -*- coding: utf-8 -*-
#
# Utility methods
#
# (C) 2011 Internet Initiative Japan Inc.
# All rights reserved.
#
# Created on 2011/06/20
# @author: yosinobu@iij.ad.jp


def to_tractime(t):
    """Convert time to trac time format.
    Type of t needs float, str or int."""

    st = ''
    if isinstance(t, str):
        st = t
    else:
        st = repr(t)
    st = ''.join(st.split('.'))
    if len(st) > 16:
        st = st[0:16]
    elif len(st) < 16:
        st = st + '0' * (16 - len(st))
    return int(st)


def to_unixtime(t):
    """Convert time to unixtime.
    Type of t needs float, str or int."""

    st = str(to_tractime(t))
    return int(st[0:10])
