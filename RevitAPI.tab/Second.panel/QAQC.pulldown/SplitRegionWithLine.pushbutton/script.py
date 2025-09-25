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




# Get the current document


# Function to split the floor
def split_floor_with_line(floor, detail_line):
    # Get the boundary/profile of the floor
    floor_profile = []
    if hasattr(floor, 'Sketch') and floor.Sketch:
        # Use the sketch profile if available
        for curve_array in floor.Sketch.Profile:
            for curve in curve_array:
                floor_profile.append(curve)
    else:
        # Fallback: extract from geometry (top face)
        options = Options()
        geometry = floor.get_Geometry(options)
        for geomObj in geometry:
            if isinstance(geomObj, Solid):
                top_face = None
                max_z = None
                for face in geomObj.Faces:
                    bbox = face.GetBoundingBox()
                    if bbox:
                        z = bbox.Max.Z
                        if max_z is None or z > max_z:
                            max_z = z
                            top_face = face
                if top_face:
                    for curve_loop in top_face.GetEdgesAsCurveLoops():
                        for curve in curve_loop:
                            floor_profile.append(curve)
                break
    # Get the geometry of the detail line
    line_curve = detail_line.GeometryCurve

    # Find the intersection points between the floor profile and the detail line
    intersection_points = []
    for curve in floor_profile:
        result = curve.Intersect(line_curve)
        if result == SetComparisonResult.Overlap:
            intersection_points.append(result.GetCurveSegment(0).GetEndPoint(0))

    if len(intersection_points) != 2:
        forms.alert("The detail line must intersect the floor at exactly two points.", exitscript=True)

    # Create two new profiles by splitting the original profile
    new_profiles = []
    for i in range(2):
        new_profile = []
        for curve in floor_profile:
            if curve.GetEndPoint(0) in intersection_points or curve.GetEndPoint(1) in intersection_points:
                new_profile.append(curve)
        new_profiles.append(new_profile)

    # Create new floors with the original type
    new_floors = []
    for profile in new_profiles:
        new_floor = doc.Create.NewFloor(profile, floor.FloorType, floor.LevelId, floor.Structural)
        new_floors.append(new_floor)

    # Delete the original floor
    doc.Delete(floor.Id)

    return new_floors

floor = None
detail_line = None

# Prompt the user to select a floor
floor_ref = selection.PickObject(ObjectType.Element, "Select a floor")
floor = doc.GetElement(floor_ref)
if not isinstance(floor, Floor):
    forms.alert("You must select a floor.", exitscript=True)

# Prompt the user to select a detail line
detail_line_ref = selection.PickObject(ObjectType.Element, "Select a detail line")
detail_line = doc.GetElement(detail_line_ref)
if not isinstance(detail_line, DetailLine):
    forms.alert("You must select a detail line.", exitscript=True)


# Start a transaction and ensure it is always closed
t = Transaction(doc, "Split Floor with Detail Line")
try:
    t.Start()
    split_floor_with_line(floor, detail_line)
    t.Commit()
except Exception as e:
    if t.HasStarted() and not t.HasEnded():
        t.RollBack()
    raise

