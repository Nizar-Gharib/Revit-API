# pyRevit script: Match floor subelement points to Toposolid surface
# Requires Revit 2024+ for Toposolid API

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ObjectType

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument


# -------------------------------------------------------------
# Extract triangulated points from Toposolid geometry
# -------------------------------------------------------------
def get_toposolid_points(toposolid):
    opts = Options()
    opts.ComputeReferences = True
    opts.IncludeNonVisibleObjects = True
    geo_elem = toposolid.get_Geometry(opts)

    points = []
    for geo_obj in geo_elem:
        solid = geo_obj if isinstance(geo_obj, Solid) else None
        if not solid or solid.Faces.Size == 0:
            continue

        for face in solid.Faces:
            mesh = face.Triangulate()
            for i in range(mesh.Vertices.Count):
                pt = mesh.Vertices[i]
                points.append(pt)

    if not points:
        raise Exception("No triangulated geometry found on Toposolid")

    return points


# -------------------------------------------------------------
# Find nearest Z from triangulated Toposolid vertices
# -------------------------------------------------------------
def get_nearest_z_from_points(points, x, y):
    min_dist = float('inf')
    nearest_z = None
    for pt in points:
        dist = ((pt.X - x)**2 + (pt.Y - y)**2)**0.5
        if dist < min_dist:
            min_dist = dist
            nearest_z = pt.Z
    return nearest_z


# -------------------------------------------------------------
# Match floor subelements to Toposolid surface
# -------------------------------------------------------------
def match_floor_subelements_to_toposolid(floor, points):
    for subelem_id in floor.SlabShapeEditor():
        subelem = doc.GetElement(subelem_id)
        if hasattr(subelem, "GetPoints") and hasattr(subelem, "SetPoints"):
            pts = subelem.GetPoints()
            new_pts = []
            for pt in pts:
                x, y = pt.X, pt.Y
                new_z = get_nearest_z_from_points(points, x, y)
                new_pts.append(XYZ(x, y, new_z))
            subelem.SetPoints(new_pts)


# -------------------------------------------------------------
# Helper: Pick multiple Floors
# -------------------------------------------------------------
def pick_multiple_floors():
    sel_refs = uidoc.Selection.PickObjects(ObjectType.Element, "Select Floors")
    floors = []
    for r in sel_refs:
        el = doc.GetElement(r.ElementId)
        if el.Category.Id.IntegerValue == int(BuiltInCategory.OST_Floors):
            floors.append(el)
    return floors


# -------------------------------------------------------------
# Main execution
# -------------------------------------------------------------
def main():
    # Pick Toposolid
    toposolid_ref = uidoc.Selection.PickObject(ObjectType.Element, "Pick Toposolid")
    toposolid = doc.GetElement(toposolid_ref)
    points = get_toposolid_points(toposolid)

    # Pick Floors
    floors = pick_multiple_floors()

    with Transaction(doc, "Match Floor Subelements to Toposolid") as t:
        t.Start()
        for floor in floors:
            match_floor_subelements_to_toposolid(floor, points)
        t.Commit()


if __name__ == "__main__":
    main()
