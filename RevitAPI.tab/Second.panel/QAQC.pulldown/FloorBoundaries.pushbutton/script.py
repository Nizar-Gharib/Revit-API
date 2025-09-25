# -*- coding: utf-8 -*-
__title__ = "Split Floor Boundaries"
__doc__ = """Splits multi-boundary floor into individual floor elements."""

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
from pyrevit import forms
import clr
clr.AddReference("System")
from System.Collections.Generic import List

# Revit document context
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
selection = uidoc.Selection

# Selection filter for Floors with multiple boundary loops
class FloorSelectionFilter(ISelectionFilter):
    def AllowElement(self, element):
        if element.Category.Id.IntegerValue == int(BuiltInCategory.OST_Floors):
            options = Options()
            geo = element.get_Geometry(options)
            for obj in geo:
                if isinstance(obj, Solid):
                    loops = []
                    for face in obj.Faces:
                        edgeLoops = face.GetEdgesAsCurveLoops()
                        if edgeLoops.Count > 1:
                            return True
        return False

    def AllowReference(self, reference, position):
        return True

# Ask user to pick a floor
with forms.WarningBar(title='Pick Floor with multiple boundary loops'):
    try:
        ref_picked = selection.PickObject(ObjectType.Element, FloorSelectionFilter(), "Select a Floor")
        floor = doc.GetElement(ref_picked)
    except:
        forms.alert("No valid Floor selected.", exitscript=True)

# Get geometry and extract curve loops only from the top face
options = Options()
geometry = floor.get_Geometry(options)

boundary_loops = []

for obj in geometry:
    if isinstance(obj, Solid):
        for face in obj.Faces:
            normal = face.ComputeNormal(UV(0.5, 0.5))  # sample midpoint
            # Only include horizontal top face (normal pointing up)
            if abs(normal.Z - 1.0) < 0.01:
                loops = face.GetEdgesAsCurveLoops()
                for loop in loops:
                    # Avoid duplicate loops by checking for uniqueness (optional, but safe)
                    if loop not in boundary_loops:
                        boundary_loops.append(loop)
        break  # we only need one solid


if len(boundary_loops) <= 1:
    forms.alert("Selected floor has only one boundary. Nothing to split.", exitscript=True)

# Start transaction
t = Transaction(doc, "Split Floor Boundaries")
t.Start()

# Get properties to recreate floors
floor_type_id = floor.GetTypeId()
level_id = floor.LevelId

# Create a new floor for each loop
for loop in boundary_loops:
    try:
        new_loops = List[CurveLoop]()
        new_loops.Add(loop)
        Floor.Create(doc, new_loops, floor_type_id, level_id)
    except Exception as e:
        print("Error creating floor:", e)

# Optional: Delete original floor
doc.Delete(floor.Id)

t.Commit()
