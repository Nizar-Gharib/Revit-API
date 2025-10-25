# -*- coding: utf-8 -*-
__title__   = "Split Floors with Line"
__doc__ = """Version = 1.0
Date    = 25.08.2025
_____________________________________________________________________
Description:
Split Selected Floors with a Detail Line.

💡 The selected Detail Line defines an infinite vertical cutting plane.
The script cuts each floor's solid and creates two new floors from the
resulting top faces, preserving FloorType and Level.

_____________________________________________________________________
How-to:

-> Click on the button
-> Select Floors
-> Select Detail Line
_____________________________________________________________________
To-Do?:
- Copy instance parameters from original floor to new floors
- Handle sloped floors with non-planar top faces
_____________________________________________________________________
Author: (based on Erik Frits' original FR splitter idea)
"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
from pyrevit import forms

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document  # type: Document
app   = __revit__.Application
selection = uidoc.Selection                  # type: Selection



# ╔═╗╦ ╦╔═╗╔╗╔╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║  ║║║ ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╚═╝╝╚╝ ╩ ╩╚═╝╝╚╝╚═╝ HELPERS
#==================================================
# -*- coding: utf-8 -*-

# Get the active view
view = doc.ActiveView
# red override
ogs = OverrideGraphicSettings()
ogs.SetProjectionLineColor(Color(255, 0, 0))

# collect all CurveElements in the active view
collector = FilteredElementCollector(doc, view.Id).OfClass(CurveElement).ToElements()
lines = [e for e in collector if isinstance(e, CurveElement)]

# find colinear + touching pairs and collect their ElementIds
to_override = set()
for i in range(len(lines)):
    l1 = lines[i]
    c1 = l1.GeometryCurve
    if c1 is None: 
        continue
    try:
        dir1 = (c1.GetEndPoint(1) - c1.GetEndPoint(0)).Normalize()
    except:
        continue

    for j in range(i + 1, len(lines)):
        l2 = lines[j]
        c2 = l2.GeometryCurve
        if c2 is None:
            continue
        try:
            dir2 = (c2.GetEndPoint(1) - c2.GetEndPoint(0)).Normalize()
        except:
            continue

        # colinear (same or opposite direction)
        if dir1.IsAlmostEqualTo(dir2) or dir1.IsAlmostEqualTo(dir2.Negate()):
            touching = (
                c1.GetEndPoint(0).IsAlmostEqualTo(c2.GetEndPoint(0)) or
                c1.GetEndPoint(0).IsAlmostEqualTo(c2.GetEndPoint(1)) or
                c1.GetEndPoint(1).IsAlmostEqualTo(c2.GetEndPoint(0)) or
                c1.GetEndPoint(1).IsAlmostEqualTo(c2.GetEndPoint(1))
            )
            if touching:
                to_override.add(l1.Id)
                to_override.add(l2.Id)

if not to_override:
    forms.alert("No touching colinear lines found in the active view.", exitscript=True)

# ...existing code...
# apply overrides in a single transaction
def _colinear_and_touching(c1, c2):
    if c1 is None or c2 is None:
        return False
    try:
        a0 = c1.GetEndPoint(0); a1 = c1.GetEndPoint(1)
        b0 = c2.GetEndPoint(0); b1 = c2.GetEndPoint(1)
    except:
        return False
    v1 = a1 - a0; v2 = b1 - b0
    if v1.IsZeroLength() or v2.IsZeroLength():
        return False
    u1 = v1.Normalize(); u2 = v2.Normalize()
    if not (u1.IsAlmostEqualTo(u2) or u1.IsAlmostEqualTo(u2.Negate())):
        return False
    return (a0.IsAlmostEqualTo(b0) or a0.IsAlmostEqualTo(b1) or a1.IsAlmostEqualTo(b0) or a1.IsAlmostEqualTo(b1))

# map ids -> elements for the set we collected earlier
proc_lines = [doc.GetElement(eid) for eid in to_override]
if not proc_lines:
    forms.alert("No touching colinear lines found in the active view.", exitscript=True)

# build adjacency for connected components
n = len(proc_lines)
adj = [[] for _ in range(n)]
for i in range(n):
    for j in range(i + 1, n):
        if _colinear_and_touching(proc_lines[i].GeometryCurve, proc_lines[j].GeometryCurve):
            adj[i].append(j); adj[j].append(i)

# find groups (connected components)
visited = [False] * n
groups = []
for i in range(n):
    if visited[i]:
        continue
    stack = [i]; group_idx = []
    while stack:
        cur = stack.pop()
        if visited[cur]:
            continue
        visited[cur] = True
        group_idx.append(cur)
        for nb in adj[cur]:
            if not visited[nb]:
                stack.append(nb)
    if len(group_idx) > 0:
        groups.append([proc_lines[k] for k in group_idx])

t = Transaction(doc, "Merge Colinear Touching Lines")
t.Start()
try:
    new_ids = []
    for grp in groups:
        # collect endpoints from all curves in the group
        pts = []
        for el in grp:
            c = el.GeometryCurve
            if c is None: 
                continue
            pts.append(c.GetEndPoint(0)); pts.append(c.GetEndPoint(1))

        if not pts:
            continue

        # choose a reference direction (first non-zero)
        ref_dir = None; ref_origin = pts[0]
        for el in grp:
            c = el.GeometryCurve
            if c is None:
                continue
            v = c.GetEndPoint(1) - c.GetEndPoint(0)
            if not v.IsZeroLength():
                ref_dir = v.Normalize()
                ref_origin = c.GetEndPoint(0)
                break
        if ref_dir is None:
            continue

        # project endpoints onto ref_dir to find extremities
        projections = [(p, (p - ref_origin).DotProduct(ref_dir)) for p in pts]
        min_pt = min(projections, key=lambda x: x[1])[0]
        max_pt = max(projections, key=lambda x: x[1])[0]

        # skip degenerate
        if min_pt.IsAlmostEqualTo(max_pt):
            continue

        new_line = Line.CreateBound(min_pt, max_pt)

        # create a new detail curve in the active view (preferred)
        created = None
        first = grp[0]
        try:
            created = doc.Create.NewDetailCurve(view, new_line)
        except Exception:
            # fallback: try model curve if sketch plane is available
            try:
                sketch = getattr(first, "SketchPlane", None) or getattr(view, "SketchPlane", None)
                if sketch is not None:
                    created = doc.Create.NewModelCurve(new_line, sketch)
                else:
                    created = doc.Create.NewDetailCurve(view, new_line)
            except Exception:
                created = None

        # copy line style from first segment (best effort)
        try:
            if created is not None and hasattr(created, "LineStyle") and hasattr(first, "LineStyle"):
                created.LineStyle = first.LineStyle
        except:
            pass

        if created is not None:
            new_ids.append(created.Id)
            # apply the same graphic override to the new merged line
            try:
                view.SetElementOverrides(created.Id, ogs)
            except:
                pass

        # delete originals
        try:
            doc.Delete([el.Id for el in grp])
        except:
            for el in grp:
                try:
                    doc.Delete(el.Id)
                except:
                    pass

    t.Commit()
except Exception as ex:
    t.Rollback()
    raise
# ...existing code...