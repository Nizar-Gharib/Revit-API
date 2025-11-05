# -*- coding: utf-8 -*-
__title__   = "Split Floors with Line"
__doc__ = """Version = 1.1
Date    = 30.10.2025
_____________________________________________________________________
Split selected Floors with a Detail Line (infinite vertical plane).
Creates two new floors (same type & level) from the bottom faces.
"""

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
from pyrevit import forms

uidoc = __revit__.ActiveUIDocument
doc   = uidoc.Document
sel   = uidoc.Selection

# ---------------------------- Helpers ----------------------------
def create_vertical_plane_from_detail_line(dline):
    crv = dline.GeometryCurve
    p0  = crv.GetEndPoint(0)
    p1  = crv.GetEndPoint(1)
    mid = (p0 + p1) / 2.0
    p2  = XYZ(mid.X, mid.Y, mid.Z + 10.0)  # force vertical plane
    return Plane.CreateByThreePoints(p0, p1, p2)

def mirror_plane(plane):
    n = plane.Normal
    return Plane.CreateByNormalAndOrigin(XYZ(-n.X, -n.Y, -n.Z), plane.Origin)

def get_main_solid(geom_elem):
    maxvol, best = 0.0, None
    for g in geom_elem:
        if isinstance(g, GeometryInstance):
            gi = g.GetInstanceGeometry()
            for sg in gi:
                if isinstance(sg, Solid) and sg.Volume > maxvol:
                    maxvol, best = sg.Volume, sg
        elif isinstance(g, Solid) and g.Volume > maxvol:
            maxvol, best = g.Volume, g
    return best

def find_planar_face_by_normal(solid, target):
    if not solid: return None
    for face in solid.Faces:
        pf = face if isinstance(face, PlanarFace) else None
        if pf and pf.FaceNormal.IsAlmostEqualTo(target):
            return pf
    return None

# ------------------------ Selection filters -----------------------
class FloorFilter(ISelectionFilter):
    def AllowElement(self, e): return isinstance(e, Floor)
class DLineFilter(ISelectionFilter):
    def AllowElement(self, e): return isinstance(e, DetailLine)

# ---------------------------- Select ------------------------------
floors = []
try:
    refs = sel.PickObjects(ObjectType.Element, FloorFilter(), "Select one or more floors to split")
    floors = [doc.GetElement(r) for r in refs]
except:
    forms.alert("No floors selected. Try again.", exitscript=True)

try:
    r = sel.PickObject(ObjectType.Element, DLineFilter(), "Select the cutting detail line")
    dline = doc.GetElement(r)
except:
    forms.alert("No detail line selected. Try again.", exitscript=True)

# ------------------------ Build cutting planes ---------------------
cut_plane      = create_vertical_plane_from_detail_line(dline)
cut_plane_mirr = mirror_plane(cut_plane)

# ------------------------ Main transaction ------------------------
skipped = []
t = Transaction(doc, "Split Floors with Line")
t.Start()
try:
    for fl in floors:
        try:
            # 1) Get a usable solid
            opt = Options()
            opt.DetailLevel = ViewDetailLevel.Fine
            opt.IncludeNonVisibleObjects = True
            geom = fl.get_Geometry(opt)
            solid = get_main_solid(geom)
            if not solid:
                skipped.append((fl, "No solid geometry."))
                continue

            # 2) Cut with half-spaces
            half1 = BooleanOperationsUtils.CutWithHalfSpace(solid, cut_plane)
            half2 = BooleanOperationsUtils.CutWithHalfSpace(solid, cut_plane_mirr)

            # 3) Use BOTTOM faces (normal ≈ -Z) for proper sketch elevation
            bottom1 = find_planar_face_by_normal(half1, XYZ.BasisZ.Negate())
            bottom2 = find_planar_face_by_normal(half2, XYZ.BasisZ.Negate())
            if not (bottom1 and bottom2):
                skipped.append((fl, "Could not find planar bottom faces (sloped/shape-edited floor?)."))
                continue

            loops1 = list(bottom1.GetEdgesAsCurveLoops())
            loops2 = list(bottom2.GetEdgesAsCurveLoops())
            if not loops1 or not loops2:
                skipped.append((fl, "No CurveLoops from bottom faces."))
                continue

            # 4) Recreate floors (same type & level)
            ftype_id = fl.FloorType.Id
            lvl_id   = fl.LevelId

            new1 = Floor.Create(doc, loops1, ftype_id, lvl_id)
            new2 = Floor.Create(doc, loops2, ftype_id, lvl_id)

            # Optional: copy a few simple instance params (safe whitelist)
            # for pname in ["Comments", "Mark"]:
            #     p_src = fl.LookupParameter(pname)
            #     if p_src and not p_src.IsReadOnly:
            #         val = p_src.AsString()
            #         for nf in (new1, new2):
                #             p_dst = nf.LookupParameter(pname)
                #             if p_dst and not p_dst.IsReadOnly and val is not None:
                #                 p_dst.Set(val)

            # 5) Delete original
            if new1 and new2:
                doc.Delete(fl.Id)

        except Exception as ex:
            skipped.append((fl, str(ex)))
            continue
    t.Commit()
except:
    t.RollBack()
    raise

# ------------------------ Feedback --------------------------------
if skipped:
    lines = ["Some floors were skipped:"]
    for fl, why in skipped:
        try:
            name = fl.Name
        except:
            name = "Floor id {}".format(fl.Id.IntegerValue)
        lines.append("- {}: {}".format(name, why))
    forms.alert("\n".join(lines))
