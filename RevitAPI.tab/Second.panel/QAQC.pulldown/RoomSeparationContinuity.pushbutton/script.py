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
from Autodesk.Revit.Creation import ItemFactoryBase
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
from pyrevit import forms
from Autodesk.Revit.DB import APIObject
from Autodesk.Revit.DB import CurveArray

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
# collect only Room Separation model lines (no detail lines, no other types)
room_sep_lines = FilteredElementCollector(doc, view.Id) \
    .OfCategory(BuiltInCategory.OST_RoomSeparationLines) \
    .WhereElementIsNotElementType() \
    .ToElements()

# keep only ModelCurve instances (safest) and dedupe by Id
lines_by_id = {}
for e in room_sep_lines:
    if e is None:
        continue
    # prefer ModelCurve; sometimes the element class can be different in some API contexts,
    # so also allow any CurveElement that belongs to the RoomSeparation category
    if isinstance(e, ModelCurve) or (hasattr(e, "Category") and e.Category and e.Category.Id.IntegerValue == int(BuiltInCategory.OST_RoomSeparationLines)):
        lines_by_id[e.Id.IntegerValue] = e
lines = list(lines_by_id.values())

# find colinear + touching pairs among room separation lines
to_process = set()
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
                to_process.add(l1.Id)
                to_process.add(l2.Id)

if not to_process:
    forms.alert("No touching Room Separation lines found in the active view.", exitscript=True)

# map ids -> elements for the set we collected earlier
colinear_lines = [doc.GetElement(eid) for eid in to_process]
# ...existing code continues (adjacency, grouping, transaction, create ModelCurve, delete originals) ...
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
colinear_lines = [doc.GetElement(eid) for eid in to_process]
if not colinear_lines:
    forms.alert("No touching colinear lines found in the active view.", exitscript=True)

# build adjacency for connected components
n = len(colinear_lines)
adj = [[] for _ in range(n)]
for i in range(n):
    for j in range(i + 1, n):
        if _colinear_and_touching(colinear_lines[i].GeometryCurve, colinear_lines[j].GeometryCurve):
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
        groups.append([colinear_lines[k] for k in group_idx])



t = Transaction(doc, "Merge Colinear Room Separation Lines")
t.Start()

view = doc.ActiveView

# Ensure view is plan-type where room separation lines are allowed
# (This is a helpful early check; remove if you know view is correct)
try:
    from Autodesk.Revit.DB import ViewPlan
    if not isinstance(view, ViewPlan):
        # still attempt, but warn (you said root causes don't apply, keep optional)
        print("Warning: active view is not a ViewPlan. Creation may still fail.")
except:
    pass

# Get or create a sketch plane that exists in the document and assign to view if needed
sketch_plane = getattr(view, "SketchPlane", None)
if sketch_plane is None:
    level = view.GenLevel
    if level is None:
        t.Rollback()
        forms.alert("Active view must have an associated level.", exitscript=True)
    plane = Plane.CreateByNormalAndOrigin(XYZ.BasisZ, XYZ(0, 0, level.Elevation))
    sketch_plane = SketchPlane.Create(doc, plane)
    try:
        view.SketchPlane = sketch_plane
    except Exception as e:
        # assignment may fail in some contexts; proceed but keep the instance
        print("Note: could not assign SketchPlane to view:", e)

created_ids = []
failed_groups = []

for grp_idx, grp in enumerate(groups):
    # collect endpoints
    pts = []
    for el in grp:
        c = el.GeometryCurve
        if c:
            pts.append(c.GetEndPoint(0)); pts.append(c.GetEndPoint(1))
    if not pts:
        continue

    # find direction and origin
    ref_dir = None; ref_origin = pts[0]
    for el in grp:
        c = el.GeometryCurve
        if c:
            v = c.GetEndPoint(1) - c.GetEndPoint(0)
            if not v.IsZeroLength():
                ref_dir = v.Normalize()
                ref_origin = c.GetEndPoint(0)
                break
    if ref_dir is None:
        print("Group {}: no non-degenerate segment found, skipping".format(grp_idx))
        continue

    # project endpoints along ref_dir to get min/max points
    projections = [(p, (p - ref_origin).DotProduct(ref_dir)) for p in pts]
    min_pt = min(projections, key=lambda x: x[1])[0]
    max_pt = max(projections, key=lambda x: x[1])[0]

    if min_pt.IsAlmostEqualTo(max_pt):
        print("Group {}: degenerate merged line (min==max), skipping".format(grp_idx))
        continue

    # ensure endpoints are at view level elevation to avoid tiny Z mismatches
    level_elev = view.GenLevel.Elevation if view.GenLevel is not None else None
    if level_elev is not None:
        if abs(min_pt.Z - level_elev) > 1e-6 or abs(max_pt.Z - level_elev) > 1e-6:
            # small tolerance projection - keeps geometry planar
            print("Group {}: projecting Z to level elevation {:.6f}".format(grp_idx, level_elev))
            min_pt = XYZ(min_pt.X, min_pt.Y, level_elev)
            max_pt = XYZ(max_pt.X, max_pt.Y, level_elev)

    new_line = Line.CreateBound(min_pt, max_pt)

    # Build a CurveArray (even if only one curve) and call the plural API
    ca = CurveArray()
    ca.Append(new_line)

    try:
        # Note: use the document creation API that returns ModelCurveArray
        # Many doc.Create.NewRoomBoundaryLines(...) wrappers exist in different versions
        # Try the Creation.NewRoomBoundaryLines variant if available on doc.Create
        created_array = None
        try:
            # This is the canonical documented call: Document.Create.NewRoomBoundaryLines(SketchPlane, CurveArray, View)
            created_array = doc.Create.NewRoomBoundaryLines(sketch_plane, ca, view)
            print("Group {}: NewRoomBoundaryLines returned {} items".format(grp_idx, len(created_array)))
        except Exception as ex1:
            # Fallback: some API wrappers expose Creation via doc.Application or doc.Creation
            try:
                created_array = doc.Document.Create.NewRoomBoundaryLines(sketch_plane, ca, view)
                print("Group {}: fallback Document.Create call succeeded".format(grp_idx))
            except Exception as ex2:
                # Most likely the standard doc.Create.NewRoomBoundaryLines will work; if not, report errors
                raise Exception("NewRoomBoundaryLines failed (primary and fallback): {}, {}".format(ex1, ex2))

        # collect created elements and apply overrides
        if created_array is not None:
            this_group_new_ids = []
            # ModelCurveArray is iterable
            for mc in created_array:
                if mc is not None:
                    this_group_new_ids.append(mc.Id)
                    try:
                        view.SetElementOverrides(mc.Id, ogs)
                    except Exception as eov:
                        print("Could not set overrides on created element:", eov)
            # Only delete originals if we actually created something
            if this_group_new_ids:
                for el in grp:
                    try:
                        doc.Delete(el.Id)
                    except Exception as dd:
                        print("Could not delete original element {}: {}".format(el.Id.IntegerValue, dd))
                created_ids.extend(this_group_new_ids)
                print("Group {}: created and cleaned up {} new elements.".format(grp_idx, len(this_group_new_ids)))
            else:
                print("Group {}: NewRoomBoundaryLines returned no elements".format(grp_idx))
                failed_groups.append((grp_idx, "no created elements"))
    except Exception as e:
        print("Group {}: Failed to create room boundary lines: {}".format(grp_idx, e))
        failed_groups.append((grp_idx, str(e)))

t.Commit()

print("Finished. Created {} new elements; {} failed groups.".format(len(created_ids), len(failed_groups)))
for f in failed_groups:
    print(" - failed group:", f)