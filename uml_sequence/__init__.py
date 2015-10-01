# -*- coding: iso-8859-1 -*-
"""
Standalone UML sequence diagram genetator. This program passes its
input to [[http://www.spinellis.gr/sw/umlgraph/|umlgraph]], producing
an UML sequence diagram image.

There is also a more "visual" alternate syntax.

$Revision: 184 $
$Id: umlsequence.py 184 2009-11-23 19:12:15Z pascal $

-------------------------------------------------------------------------------

Copyright (C) 2012 by Pascal Bauermeister <pascal.bauermeister@gmail.com>

This module is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2, or (at your option)
any later version.

-------------------------------------------------------------------------------

Usage:
 do: umlsequence -h

Procedural syntax (a.k.a. Spinellis syntax) see:
  http://www.spinellis.gr/sw/umlgraph/doc/index.html
  http://www.spinellis.gr/sw/umlgraph/doc/seq-ops.html

  Examples:
    http://www.spinellis.gr/sw/umlgraph/doc/uml-appa.html (then click next)

Alternate ("easy") syntax:
  See http://moinmoin.wikiwikiweb.de/UmlSequence

See also:
  Umlgraph: http://www.spinellis.gr/sw/umlgraph/

-------------------------------------------------------------------------------

ChangeLog:

Pascal Bauermeister <pascal DOT bauermeister AT gmail DOT com> 2012-06-20
  * Made a standalone command-line utility

Pascal Bauermeister <pascal DOT bauermeister AT gmail DOT com> 2009-01-09
  * Compatibility for MoinMoin 1.7 and above

Pascal Bauermeister <pascal DOT bauermeister AT gmail DOT com> 2008-03-18:
  * Use subprocess.Popen() instead of os.system()

Pascal Bauermeister <pascal DOT bauermeister AT gmail DOT com> 2007-05-13:
  * Initial version

"""

import os
import re
import sha
import StringIO
import string
import sys

try:
    from __version__ import VERSION
except ImportError:
    VERSION = "unknown"


UMLGRAPH_PIC = u"""
#/usr/bin/pic2plot -Tps
#
# Pic macros for drawing UML sequence diagrams
#
# (C) Copyright 2004-2005 Diomidis Spinellis.
#
# Permission to use, copy, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation.
#
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTIES OF
# MERCHANTIBILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#
# $_Id_: sequence.pic,v 1.10 2005/10/19 18:36:08 dds Exp $
#


# Default parameters (can be redefined)

# Spacing between messages
spacing = 0.25;
# Active box width
awid = .1;
# Box height
boxht = 0.3;
# Commend folding
corner_fold=awid
# Comment distance
define comment_default_move {up 0.25 right 0.25};
# Comment height
comment_default_ht=0.5;
# Comment width
comment_default_wid=1;


# Create a new object(name,label)
define object {
 $1: box $2; move;
 # Could also underline text with \\mk\\ul\\ul\\ul...\\rt
 {
  line from $1.w + (.1, -.07) to $1.e + (-.1, -.07);
 }
 move to $1.e;
 move right;
 # Active is the level of activations of the object
 # 0 : inactive : draw thin line swimlane
 # 1 : active : draw thick swimlane
 # > 1: nested : draw nested swimlane
 active_$1 = 0;
 lifestart_$1 = $1.s.y;
}

# Create a new external actor(name,label)
define actor {
 $1: [
  XSEQC: circle rad 0.06;
  XSEQL: line from XSEQC.s down .12;
  line from XSEQL.start - (.15,.02) to XSEQL.start + (.15,-.02);
  XSEQL1: line from XSEQL.end left .08 down .15;
  XSEQL2: line from XSEQL.end right .08 down .15;
  line at XSEQC.n invis "" "" "" $2;
 ]
 move to $1.e;
 move right;
 active_$1 = 0;
 lifestart_$1 = $1.s.y - .05;
}

# Create a new placeholder object(name)
define placeholder_object {
 $1: box invisible;
 move;
 move to $1.e;
 move right;
 active_$1 = 0;
 lifestart_$1 = $1.s.y;
}

define pobject {
 placeholder_object($1);
}

define extend_lifeline {
 if (active_$1 > 0) then {
  # draw the left edges of the boxes
  move to ($1.x - awid/2, Here.y);
  for level = 1 to active_$1 do {
   line from (Here.x, lifestart_$1) to Here;
   move right awid/2
  }

  # draw the right edge of the innermost box
  move right awid/2;
  line from (Here.x, lifestart_$1) to Here;
 } else {
  line from ($1.x, lifestart_$1) to ($1.x, Here.y) dashed thickness 0;
 }
 lifestart_$1 = Here.y;
}

# complete(name)
# Complete the lifeline of the object with the given name
define complete {
 extend_lifeline($1)
 if (active_$1) then {
  # draw bottom of all active boxes
  line right ((active_$1 + 1) * awid/2) from ($1.x - awid/2, Here.y);
 }
}

# Draw a message(from_object,to_object,label)
define message {
 down;
 move spacing;
 # Adjust so that lines and arrows do not fall into the
 # active box.  Should be .5, but the arrow heads tend to
 # overshoot.
 if ($1.x <= $2.x) then {
  off_from = awid * .6;
  off_to = -awid * .6;
 } else {
  off_from = -awid * .6;
  off_to = awid * .6;
 }

 # add half a box width for each level of nesting
 if (active_$1 > 1) then {
  off_from = off_from + (active_$1 - 1) * awid/2;
 }

 # add half a box width for each level of nesting
 if (active_$2 > 1) then {
  off_to = off_to + (active_$2 - 1) * awid/2;
 }

 if ($1.x == $2.x) then {
  arrow from ($1.x + off_from, Here.y) right then \
    down .25 then left $3 ljust " " " " " " ;
 } else {
  arrow from ($1.x + off_from, Here.y) to ($2.x + off_to, Here.y) $3 " ";
 }
}

# Display a lifeline constraint(object,label)
define lifeline_constraint {
 off_from = awid;
 # add half a box width for each level of nesting
 if (active_$1 > 1) then {
  off_from = off_from + (active_$1 - 1) * awid/2;
 }

 box at ($1.x + off_from, Here.y) invis $2 ljust " " ;
}

define lconstraint {
 lifeline_constraint($1,$2);
}

# Display an object constraint(label)
# for the last object drawn
define object_constraint {
 { box invis with .s at last box .nw $1 ljust; }
}

define oconstraint {
 object_constraint($1);
}

# Draw a creation message(from_object,to_object,object_label)
define create_message {
 down;
 move spacing;
 if ($1.x <= $2.x) then {
  off_from = awid * .6;
  off_to = -boxwid * .51;
 } else {
  off_from = -awid * .6;
  off_to = boxwid * .51;
 }

 # add half a box width for each level of nesting
 if (active_$1 > 1) then {
  off_from = off_from + (active_$1 - 1) * awid/2;
 }

 # See comment in destroy_message
 XSEQA: arrow from ($1.x + off_from, Here.y) to \
  ($2.x + off_to, Here.y) "«create»" " ";
 if ($1.x <= $2.x) then {
  { XSEQB: box $3 with .w at XSEQA.end; }
 } else {
  { XSEQB: box $3 with .e at XSEQA.end; }
 }
 {
  line from XSEQB.w + (.1, -.07) to XSEQB.e + (-.1, -.07);
 }
 lifestart_$2 = XSEQB.s.y;
 move (spacing + boxht) / 2;
}

define cmessage {
 create_message($1,$2,$3);
}

# Draw an X for a given object
define drawx {
 {
  line from($1.x - awid, lifestart_$1 - awid) to \
   ($1.x + awid, lifestart_$1 + awid);
  line from($1.x - awid, lifestart_$1 + awid) to \
   ($1.x + awid, lifestart_$1 - awid);
 }
}

# Draw a destroy message(from_object,to_object)
define destroy_message {
 down;
 move spacing;
 # The troff code is \\(Fo \\(Fc
 # The groff code is also \\[Fo] \\[Fc]
 # The pic2plot code is \\Fo \\Fc
 # See http://www.delorie.com/gnu/docs/plotutils/plotutils_71.html
 # To stay compatible with all we have to hardcode the characters
 message($1,$2,"«destroy»");
 complete($2);
 drawx($2);
}

define dmessage {
 destroy_message($1,$2);
}

# An object deletes itself: delete(object)
define delete {
 complete($1);
 lifestart_$1 = lifestart_$1 - awid;
 drawx($1);
}

# Draw a message return(from_object,to_object,label)
define return_message {
 down;
 move spacing;
 # See comment in message
 if ($1.x <= $2.x) then {
  off_from = awid * .6;
  off_to = -awid * .6;
 } else {
  off_from = -awid * .6;
  off_to = awid * .6;
 }

 # add half a box width for each level of nesting
 if (active_$1 > 1) then {
  off_from = off_from + (active_$1 - 1) * awid/2;
 }

 # add half a box width for each level of nesting
 if (active_$2 > 1) then {
  off_to = off_to + (active_$2 - 1) * awid/2;
 }

 arrow from  ($1.x + off_from, Here.y) to \
  ($2.x + off_to, Here.y) dashed $3 " ";
}

define rmessage {
 return_message($1,$2,$3);
}

# Object becomes active
# Can be nested to show recursion
define active {
 extend_lifeline($1);
 # draw top of new active box
 line right awid from ($1.x + (active_$1 - 1) * awid/2, Here.y);
 active_$1 = active_$1 + 1;
}

# Object becomes inactive
# Can be nested to show recursion
define inactive {
 extend_lifeline($1);
 active_$1 = active_$1 - 1;
 # draw bottom of innermost active box
 line right awid from ($1.x + (active_$1 - 1) * awid/2, Here.y);
}

# Time step
# Useful at the beginning and the end
# to show object states
define step {
 down;
 move spacing;
}

# Switch to asynchronous messages
define async {
 arrowhead = 0;
 arrowwid = arrowwid * 2;
}

# Switch to synchronous messages
define sync {
 arrowhead = 1;
 arrowwid = arrowwid / 2;
}

# same as lifeline_constraint, but Text and empty string are exchanged.
define lconstraint_below{
 off_from = awid;
 # add half a box width for each level of nesting
 if (active_$1 > 1) then {
  off_from = off_from + (active_$1 - 1) * awid/2;
 }

 box at ($1.x + off_from, Here.y) invis "" $2 ljust;
}

# begin_frame(left_object,name,label_text);
define begin_frame {
 # The lifeline will be cut here
 extend_lifeline($1);
 # draw the frame-label
 $2: box $3 invis with .n at ($1.x, Here.y);
 d = $2.e.y - $2.se.y;
 line thickness 0 from $2.ne to $2.e then down d left d then to $2.sw;
 # continue the lifeline below the frame-label
 move to $2.s;
 lifestart_$1 = Here.y;
}

# end_frame(right_object,name);
define end_frame {
 # dummy-box for the lower right corner:
 box invis "" with .s at ($1.x, Here.y);
 # draw the frame
 frame_wid = last box.se.x - $2.nw.x
 frame_ht = - last box.se.y + $2.nw.y
 box thickness 0 with .nw at $2.nw wid frame_wid ht frame_ht;
 # restore Here.y
 move to last box.s;
}

# comment(object,[name],[line_movement], [box_size] text);
define comment {
 old_y = Here.y
 # draw the first connecting line, at which's end the box wil be positioned
 move to ($1.x, Here.y)
 if "$3" == "" then {
  line thickness 0 comment_default_move() dashed;
 } else {
  line thickness 0 $3 dashed;
 }

 # draw the box, use comment_default_xx if no explicit
 # size is given together with the text in parameter 4
 old_boxht=boxht;
 old_boxwid=boxwid;
 boxht=comment_default_ht;
 boxwid=comment_default_wid;
 if "$2" == "" then {
  box $4 invis;
 } else {
  $2: box $4 invis;
 }
 boxht=old_boxht;
 boxwid=old_boxwid;

 # draw the frame of the comment
 line thickness 0 from last box.nw \\
  to     last box.ne - (corner_fold, 0) \\
  then to last box.ne - (0, corner_fold) \\
  then to last box.se \\
  then to last box.sw \\
  then to last box.nw ;
 line thickness 0 from last box.ne - (corner_fold, 0) \\
  to     last box.ne - (corner_fold, corner_fold) \\
  then to last box.ne - (0, corner_fold) ;

 # restore Here.y
 move to ($1.x, old_y)
}

# connect_to_comment(object,name);
define connect_to_comment {
 old_y = Here.y
 # start at the object
 move to ($1.x, Here.y)
 # find the best connection-point of the comment to use as line-end
 if $1.x < $2.w.x then {
  line to $2.w dashed thickness 0;
 } else {
  if $1.x > $2.e.x then {
   line to $2.e dashed thickness 0;
  } else {
   if Here.y < $2.s.y then {
    line to $2.s dashed thickness 0;
   } else {
    if Here.y > $2.n.y then {
     line to $2.n dashed thickness 0;
    }
   }
  }
 }
 # restore Here.y
 move to ($1.x, old_y)
}

"""

###############################################################################

import os
from subprocess import Popen, PIPE


def escape(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def execute(cmd, stdin, enc_in, enc_out):
    try:
        p = Popen(cmd, shell=False, bufsize=0,
                  stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    except OSError:
        raise RuntimeError(
            "Error executing command " \
                "(maybe '%s' is not installed on the system?) : %s" % (
                os.path.split(cmd[0])[-1], ' '.join(cmd)))

    if enc_in:
        stdin = stdin.encode(enc_in)
    stdout, stderr = p.communicate(stdin)
    if enc_out:
        stdout = unicode(stdout, "utf-8")
    stderr = unicode(stderr, "utf-8", "replace")

    return stdout, stderr

###############################################################################


class Parser:
    EXPRE1 = re.compile(
        "([A-Za-z_0-9]+?)([\+\-\#~!]?)"
        " *"
        "(\??-+>"
        "|<-+\??"
        "|\??=+>\??"
        "|\??<=+\??"
        "|\??#+>"
        "|<#+\??"
        "|\??:+>"
        "|<:+\??"
        "|//"
        "|:"
        "|>"
        "|\*"
        "|\["
        "|\]"
        "|\{_?\}"
        ")"
        " *"
        "([#A-Za-z_0-9]*)([\+\-\#~!]?)"
        " *"
        "(.*)")

    EXPRE1_call = re.compile("([A-Za-z_0-9]+) *(=) *(.*)")
    EXPRE1_call = re.compile("(.*?) *(=) *(.*)")

    EXPRE2 = re.compile("([A-Za-z_0-9]+[\+\-\#~!]|:)+")

    EXPRE3 = re.compile("([A-Za-z_0-9]*)([\+\-\#~!]?) *(_?)\{(.*)\}")

    extensions = ['.dot']

    def __init__(self, raw):
        # save call arguments for later use in format()
        self.raw = raw.encode('utf-8')
        self.raw = raw.encode('latin1')
        self.raw = raw

        return

    def _convert_from_alternate_1(self, lines):
        newlines = []

        self.has_first_step = False
        self.objects = []

        def add_obj(name):
            if name not in self.objects:
                self.objects.append(name)

        def rem_obj(name):
            if name in self.objects:
                self.objects.remove(name)

        def add(txt):
            txt = txt.strip()
            if not txt:
                return
            ini = "object", "pobject", "placeholder_object", "actor"
            obj = max([txt.startswith(i) for i in ini])
            if not obj and not self.has_first_step:
                newlines.append("step();")
                self.has_first_step = True
            newlines.append(txt)

        def nl2str(text):
            texts = text.split("\\n")
            texts = [t.strip() for t in texts]
            maxlen = max([len(t) for t in texts])
            text = ' " " '.join(texts)
            nlines = len(texts)
            return text, nlines, maxlen

        def do_line(line, level=0):

            if not line.strip():
                return

            newlines.append('#' * (2 - level) * 40)
            newlines.append('## [%s]' % line)

            oline = line

            line = line.strip()
            if not line:
                return

            if line.startswith("#"):
                newlines.append(line)
                return

            # try to match: [OBJECT[OP]] [_]{CONSTRAINT}
            terms = Parser.EXPRE3.findall(line)
            if terms:
                newlines.append('#' + ' ' * 50 + "##3## " + oline)
                l, lop, below, r = terms[0]
                r, nlines, maxlen = nl2str(r)
                if not l:
                    add('oconstraint(" %s ");' % (r))
                elif not below:
                    add('lconstraint(%s," %s ");' % (l, r))
                    if lop:
                        do_line(l + lop, level + 1)
                else:
                    add('lconstraint_below(%s," %s ");' % (l, r))
                    if lop:
                        do_line(l + lop, level + 1)
                return

            # try to match: OBJECT[OP] OP OBJECT[OP] MORE
            terms = Parser.EXPRE1.findall(line)
            if terms:
                l, lop, op, r, rop, edge = terms[0]
                newlines.append('#' + ' ' * 50 + "##1## " + oline)
                ##newlines.append('#'+' '*50 + "# "+ `(l,op,r,edge)`)

                async_head = False
                async_tail = False

                if len(op) > 1:
                    # trim '?'
                    if op[0] == "?":
                        op = op[1:]
                        if op.startswith("<"):
                            async_head = True
                        else:
                            async_tail = True

                    if op[-1] == "?":
                        op = op[:-1]
                        if op.endswith(">"):
                            async_head = True
                        else:
                            async_tail = True

                    if async_tail:
                        add('async();')

                    # trim long arrows
                    if op[0] == "<":
                        op = op[:2]
                    elif op[-1] == ">":
                        op = op[-2:]

                # transform left arrow to right arrow
                if op[0] == "<":
                    op = op[1:] + ">"
                    l, r = r, l
                    lop, rop = rop, lop
                ##newlines.append('#'+' '*50 + "# "+ `(l,op,r,edge)`)

                r2 = ' '.join((r, edge)).strip()

                # escape quotes
                edge = edge.replace('"', '\\"')
                r2 = r2.replace('"', '\\"')

                # implement primitives
                # http://www.spinellis.gr/sw/umlgraph/doc/seq-ops.html

                if op == ":"  and r2 and not r2.startswith("#"):
                    add('object(%s," %s ");' % (l, r2))
                    add_obj(l)

                elif op == ":":
                    add('pobject(%s);' % (l))

                elif op == "*":
                    if r2.startswith("#"):
                        r2 = ""
                    add('actor(%s," %s ");' % (l, r2))
                    add_obj(l)

                elif op == "->":
                    edge, nlines, maxlen = nl2str(edge)
                    if edge.startswith("<(>"):
                        add('message(%s,%s,"");' % (l, r))
                        edge = edge[3:].strip()
                        add('lconstraint(%s," %s ");' % (l, edge))
                    elif edge.startswith("<)>"):
                        add('message(%s,%s,"");' % (l, r))
                        edge = edge[3:].strip()
                        add('lconstraint(%s," %s ");' % (r, edge))
                    else:
                        add('message(%s,%s," %s ");' % (l, r, edge))
                    if lop:
                        do_line(l + lop, level + 1)
                    if rop:
                        do_line(r + rop, level + 1)

                elif op == ">":
                    r2, nlines, maxlen = nl2str(r2)
                    add('active(%s);' % l)
                    #add('step();')
                    add('message(%s,%s," %s ");' % (l, l, r2))
                    add('inactive(%s);  # >' % l)
                    if lop:
                        do_line(l + lop, level + 1)

                elif op == ":>":
                    add('cmessage(%s,%s," %s "," ");' % (l, r, edge))
                    add_obj(r)
                    if lop:
                        do_line(l + lop, level + 1)
                    if rop:
                        do_line(r + rop, level + 1)

                elif op == "=>":
                    subterms = Parser.EXPRE1_call.findall(edge)
                    if subterms:
                        subterms = subterms[0]

                    # treat case: A => B  result=call(args)
                    if subterms and len(subterms) == 3 and subterms[1] == "=":
                        # short hand for request+result
                        res, op, edge = subterms
                        add('message(%s,%s," %s ");' % (l, r, edge))
                        add('active(%s);' % r)

                        # sync/async for arrow head end:
                        #if async_tail and not async_head:
                        #    add('sync();')
                        #elif not async_tail and async_head:
                        #    add('async();')

                        # return message is always async!
                        add('async();')
                        add('rmessage(%s,%s," %s ");' % (r, l, res))
                        add('sync();')

                        add('inactive(%s);  # =>' % r)

                    # treat case: A => B  result
                    else:
                        # result only
                        add('async();')
                        add('rmessage(%s,%s," %s ");' % (l, r, edge))
                        add('sync();')

                    # post-ops
                    if lop:
                        do_line(l + lop, level + 1)
                    if rop:
                        do_line(r + rop, level + 1)

                elif op == "#>":
                    add('dmessage(%s,%s);' % (l, r))
                    rem_obj(r)
                    if lop:
                        do_line(l + lop, level + 1)
                    if rop:
                        do_line(r + rop, level + 1)

                elif op == "//":
                    r2 = (r + " " + edge).strip()
                    if r2.startswith("["):
                        opts, text = r2[1:].split("]", 1)  # opts passed
                    else:
                        opts, text = "", r2                # no opts passed
                    opts = (opts + ",,").split(",")[:3]    # insure 3 elements
                    text = text.strip()

                    if not text:
                        add('connect_to_comment(%s,%s);' % (l, opts[0]))
                    else:
                        text, nlines, maxlen = nl2str(text)
                        if not opts[1]:  # auto-calculate box pos
                            opts[1] = "down 0 right"
                        if not opts[2]:  # auto-calculate box size
                            w = 0.10 + float(maxlen) / 13.0
                            h = 0.10 + 0.16 * nlines
                            opts[2] = "wid %.2f ht %.2f" % (w, h)
                        opts = ",".join(opts)
                        add('comment(%s,%s "%s");' % (l, opts, text))

                    if lop:
                        do_line(l + lop, level + 1)

                elif op == "[" or op == "]":
                    # Possible syntax:
                    #   frame_name [ object frame_title
                    #           ... activity ...
                    #                object ] frame_name
                    #
                    # Possible syntax:
                    #                object ] frame_name frame_title
                    #           ... activity ...
                    #   frame_name [ object
                    #
                    if edge:
                        if op == "]":
                            r, l = l, r
                        add('begin_frame(%s,%s," %s ");' % (r, l, edge))
                    else:
                        if op == "[":
                            r, l = l, r
                        add('end_frame(%s,%s);' % (l, r))

                if async_head or async_tail:
                    add('sync();')
                return

            # try to match: OBJECT[OP] [OBJECT[OP] ...]
            terms = Parser.EXPRE2.findall(line)
            if terms == line.split():
                newlines.append('#' + ' ' * 50 + "##2## " + oline)
                for term in terms:
                    l, op = term[:-1], term[-1]
                    if op == "+":
                        add('active(%s);' % l)
                    elif op == "-":
                        add('inactive(%s);  # -' % l)
                    elif op == "!":
                        add('active(%s);' % l)
                        add('step();')
                        add('inactive(%s);  # !' % l)
                    elif op == "#":
                        add('complete(%s);' % l)
                        rem_obj(l)
                    elif op == "~":
                        add('delete(%s);' % l)
                        rem_obj(l)
                if ":" in terms:
                    add('step();')
                return

            # all attemps to match by RE failed => output as-is
            newlines.append(line)

        for line in lines:
            do_line(line)

        if self.objects:
            add('step();')
            for o in self.objects:
                add('complete(%s);' % o)
        return newlines

    def format(self, opt_dbg, opt_percent, out, fmt, bgcolor=None):
        """
        The parser's entry point
        """

        raw = self.raw
        # preprocess:
        # - remove tabs
        raw = raw.replace("\t", " ")
        # - join lines ending with '\' with the next one
        #   (lazy way, TODO: use regex)
        while raw.find("\\\n ") >= 0:
            raw = raw.replace("\\\n ", "\\\n")
        while raw.find(" \\\n") >= 0:
            raw = raw.replace(" \\\n", "\\\n")
        raw = raw.replace("\\\n", " ")
        lines = raw.split('\n')

        # alternate syntax support
        lines = self._convert_from_alternate_1(lines)

        # debug ? post-print
        if opt_dbg:
            pic_lines = [l for l in lines if not l.startswith('#')]
            print >>sys.stderr, raw
            print >>sys.stderr, "----------"
            print >>sys.stderr, '\n'.join(pic_lines)

        # go !
        all = '\n'.join(lines).strip()
        seq_pic = UMLGRAPH_PIC
        all = u".PS\n%s\n%s\n.PE" % (seq_pic, all)

        #os.system('pic2plot -T ps "%s" > "%s" 2>"%s"' % (pic, ps, errpath))
        stdout, stderr = execute(["pic2plot",
                                  "-T", "ps",
                                  "--page-size", "a4,xsize=16.8cm,xoffset=-1cm",
                                  ],
                                 all, "latin1", None)

        if stderr:
            # Error handling

            # let us parse the 1st line of the error file, saying:
            #   pic2plot:<PIC_FILENAME>:<LINE_NR>:<ERROR_MESSAGE>
            print >>sys.stderr, stderr
            err = stderr.split('\n')[0].split(":")
            if len(err) == 4:
                lnr, msg = err[2:2 + 2]
                ix = int(lnr) - 1
                snip = [l.rstrip() for l in all.split('\n')]
                snip, context = snip[ix], snip[max(ix - 2, 0):ix + 1 + 2]
                context = "\n".join(context)
            else:  # cannot parse it
                msg = ":".join(err)
                snip = ""

            # print error message
            print >>sys.stderr, "Umlsequence error: ", msg

            # print code snippet
            if snip:
                print >>sys.stderr, "Faulty line:"
                print >>sys.stderr, snip
                print >>sys.stderr
                print >>sys.stderr, "Context:"
                print >>sys.stderr, context
            return 1

        stderr = None
        if fmt <> "ps":
            # Run the postprocessing/conversion chain
            ps = stdout
            cmd = [
                "convert",
                "-density", "%dx%d" % (opt_percent, opt_percent),
                ]

            if bgcolor is not None:
                # add background
                cmd += ["-compose", "over", "-background", bgcolor, "-flatten"]

            cmd += ["ps:-", fmt+":-"]

            stdout, stderr = execute(cmd, ps, None, None)

        if not stderr:
            out.write(stdout)
        else:
            print >>sys.stderr, "Umlsequence error: ", stderr
            return 2

        # Done
        return 0


def run(inp, out, pcent, debug, fmt, bgcolor=None):
    return Parser(inp.read()).format(debug, pcent, out, fmt, bgcolor)
