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
def mirror_plane(plane):
    """Returns a plane mirrored by flipping its normal."""
    n = plane.Normal
    mirrored_normal = XYZ(-n.X, -n.Y, -n.Z)
    return Plane.CreateByNormalAndOrigin(mirrored_normal, plane.Origin)

def create_plane_from_line(detail_line):
    """Create an infinite vertical plane from a detail line (by three points)."""
    crv = detail_line.Location.Curve
    p0  = crv.GetEndPoint(0)
    p1  = crv.GetEndPoint(1)
    pm  = (p0 + p1) / 2.0
    # Lift mid point in +Z to ensure non-collinearity
    pm  = XYZ(pm.X, pm.Y, pm.Z + 10.0)
    return Plane.CreateByThreePoints(p0, p1, pm)

def get_first_solid(elem):
    """Extract the first non-empty solid from an element's geometry."""
    opt = Options()
    opt.ComputeReferences = True
    opt.IncludeNonVisibleObjects = False
    ge = elem.get_Geometry(opt)
    if not ge:
        return None
    for g in ge:
        solid = None
        if isinstance(g, Solid) and g.Volume > 1e-9:
            return g
        # Some geometry comes wrapped in GeometryInstance
        if isinstance(g, GeometryInstance):
            inst_ge = g.GetInstanceGeometry()
            for ig in inst_ge:
                if isinstance(ig, Solid) and ig.Volume > 1e-9:
                    return ig
    return None

def find_top_planar_face(solid):
    """
    Find the 'top' planar face suitable for deriving plan boundaries.
    Preference: PlanarFace with upward normal (Z>0) and highest origin.Z
    Fallback: largest-area upward PlanarFace.
    """
    top_face = None
    top_z = float('-inf')
    fallback = None
    fallback_area = 0.0

    for f in solid.Faces:
        pf = f if isinstance(f, PlanarFace) else None
        if not pf:
            continue
        n = pf.FaceNormal
        # Upward-ish?
        if n.Z > 0.7071:  # cos(45deg) tolerance
            z = pf.Origin.Z
            if z > top_z:
                top_z = z
                top_face = pf
            if pf.Area > fallback_area:
                fallback_area = pf.Area
                fallback = pf

    return top_face if top_face else fallback

def curve_loops_are_valid(curve_loops):
    """Basic sanity checks for CurveLoops."""
    if not curve_loops or len(curve_loops) == 0:
        return False
    for cl in curve_loops:
        try:
            if not CurveLoop.IsClosed(cl):
                return False
            # Planarity is enforced by Floor.Create; this is a pre-check
            _ = cl.GetPlane()  # may throw if non-planar
        except:
            return False
    return True

def clone_floor_params(src_floor, dst_floors):
    """
    Optional: copy non-readonly instance parameters.
    Skips elements with storage type None and parameters that are read-only or built-in that shouldn't be copied.
    """
    try:
        for dst in dst_floors:
            for p in src_floor.Parameters:
                if p.IsReadOnly:
                    continue
                defname = p.Definition.Name
                dstp = dst.LookupParameter(defname)
                if not dstp or dstp.IsReadOnly:
                    continue
                st = p.StorageType
                if st == StorageType.String:
                    dstp.Set(p.AsString())
                elif st == StorageType.Integer:
                    dstp.Set(p.AsInteger())
                elif st == StorageType.Double:
                    dstp.Set(p.AsDouble())
                elif st == StorageType.ElementId:
                    dstp.Set(p.AsElementId())
    except:
        pass

# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝ SELECTION FILTERS
#==================================================
class ISelectionFilter_Floors(ISelectionFilter):
    def AllowElement(self, e):
        return isinstance(e, Floor)

class ISelectionFilter_DetailLine(ISelectionFilter):
    def AllowElement(self, e):
        return isinstance(e, DetailLine)

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ SELECTION
#==================================================
selected_line    = None
selected_floors  = []

# 1️⃣ Get Floors
with forms.WarningBar(title='Pick Floors:'):
    try:
        refs = selection.PickObjects(ObjectType.Element, ISelectionFilter_Floors())
        selected_floors = [doc.GetElement(r) for r in refs]
    except:
        pass

# 2️⃣ Get Detail Line
with forms.WarningBar(title='Pick Detail Line:'):
    try:
        ref_line = selection.PickObject(ObjectType.Element, ISelectionFilter_DetailLine())
        selected_line = doc.GetElement(ref_line)
    except:
        pass

if not selected_floors:
    forms.alert("No Floors selected. Please try again.", exitscript=True)

if not selected_line:
    forms.alert("No Detail Line selected. Please try again.", exitscript=True)

# 3️⃣ Create infinite plane from line
plane = create_plane_from_line(selected_line)

# ✅ Ensure Elements
if not selected_line or not selected_floors:
    forms.alert('Select Floors and a Detail Line.', exitscript=True)

# ╔╦╗╦╔═╗╔╗╔╔═╗╦ ╦╦═╗╔═╗
#  ║ ║║ ║║║║║  ║ ║╠╦╝║╣
#  ╩ ╩╚═╝╝╚╝╚═╝╚═╝╩╚═╚═╝ MAIN
#==================================================
t = Transaction(doc, 'Split Floors with Line')
t.Start()

for floor in selected_floors:
    try:
        # --- get original info ---
        floor_type_id = floor.GetTypeId()
        level_id      = floor.LevelId

        # --- get solid geometry ---
        solid = get_first_solid(floor)
        if not solid:
            continue

        # --- split the solid with half-spaces (plane and its mirror) ---
        new_shape_1 = BooleanOperationsUtils.CutWithHalfSpace(solid, plane)
        new_shape_2 = BooleanOperationsUtils.CutWithHalfSpace(solid, mirror_plane(plane))

        # --- obtain top faces from both halves ---
        top_face_1 = find_top_planar_face(new_shape_1)
        top_face_2 = find_top_planar_face(new_shape_2)
        if not top_face_1 or not top_face_2:
            # Couldn’t derive a usable top face (e.g., highly sloped or non-planar)
            continue

        # --- outlines as CurveLoops ---
        outline_1 = top_face_1.GetEdgesAsCurveLoops()  # IList<CurveLoop>
        outline_2 = top_face_2.GetEdgesAsCurveLoops()

        # --- validate loops ---
        if not (curve_loops_are_valid(outline_1) and curve_loops_are_valid(outline_2)):
            continue

        # --- create new floors (uses IList<CurveLoop> overload) ---
        new_floor1 = Floor.Create(doc, outline_1, floor_type_id, level_id)
        new_floor2 = Floor.Create(doc, outline_2, floor_type_id, level_id)

        # --- optional: copy instance parameters from original ---
        clone_floor_params(floor, [new_floor1, new_floor2])

        # --- delete old floor if both succeeded ---
        if new_floor1 and new_floor2:
            doc.Delete(floor.Id)

        # # Debug visualization (DirectShape) — optional:
        # cat_id = ElementId(BuiltInCategory.OST_GenericModel)
        # ds1 = DirectShape.CreateElement(doc, cat_id); ds1.SetShape([new_shape_1])
        # ds2 = DirectShape.CreateElement(doc, cat_id); ds2.SetShape([new_shape_2])

    except Exception as e:
        # Print to pyRevit console; avoid killing the whole run on one failure
        print("Failed splitting floor {}: {}".format(floor.Id, e))

t.Commit()
