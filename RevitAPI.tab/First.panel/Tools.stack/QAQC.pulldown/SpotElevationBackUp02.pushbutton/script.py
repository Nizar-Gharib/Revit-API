# -*- coding: utf-8 -*-
__title__ = "Imported Category"
__doc__ = """Version = 1.0
Date    = 20.09.2025
_____________________________________________________________________
Description:
Override the graphics of the listed DWGs as per an external csv file
_____________________________________________________________________
How-to:
-> Ensure the csv file path is listed below
-> Ensure the dwg files are listed below (with .dwg at the end of their names)
-> Just run the script within pyRevit environment and it will do the job
_____________________________________________________________________
Last update:
- [21.10.2025] - 1.0 RELEASE
_____________________________________________________________________
Author: Nizar Gharib"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
# Regular + Autodesk
from Autodesk.Revit.DB import *
# pyRevit
# from pyrevit import forms
from Autodesk.Revit.DB import Categories
from Autodesk.Revit.DB import Element
from Autodesk.Revit.DB import CategoryNameMap
from Autodesk.Revit.DB import APIObject
from Autodesk.Revit.UI.Selection import ObjectType
from Autodesk.Revit.UI.Selection import PickBoxStyle
from Autodesk.Revit.DB import FilteredElementCollector
from Autodesk.Revit.DB import LocationPoint


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#==================================================


rvt_year = int(app.VersionNumber)

def get_elements_by_type_name(type_name):
    # ... (Function definition remains the same) ...
    # CREATE RULE
    param_id = ElementId(BuiltInParameter.ALL_MODEL_TYPE_NAME)
    f_param = ParameterValueProvider(param_id)
    f_evaluator = FilterStringEquals()

    # Revit API has changes
    if rvt_year < 2023:
        f_rule = FilterStringRule(f_param, FilterStringEquals(), type_name,True)
    else:
        f_rule = FilterStringRule(f_param, FilterStringEquals(), type_name)

    # CREATE FILTER
    filter_type_name = ElementParameterFilter(f_rule)

    # GET ELEMENTS
    return FilteredElementCollector(doc).WherePasses(filter_type_name)\
                              .WhereElementIsNotElementType().ToElements()
                                
current_view = doc.ActiveView
# Get Elements                           
elements = get_elements_by_type_name('Spot Elevation Backup')

loc = []
for el in elements:
    loc_point = el.Location
    if isinstance(loc_point, LocationPoint):
        point = loc_point.Point
        loc.append(point)
        print("Detail Item: {} at Location: X={}, Y={}, Z={}".format(el.Name, point.X, point.Y, point.Z))
    else:
        print("Element {} does not have a valid location point.".format(el.Name))

# Get the user to select linked topography elements
selection = uidoc.Selection

#linked
picked_ref = selection.PickObject(ObjectType.LinkedElement, "Select linked topography elements")
# Get the elements from the picked references
link_model = doc.GetElement(picked_ref)
link_doc = link_model.GetLinkDocument()
surface_topo = link_doc.GetElement(picked_ref.LinkedElementId)

# --- Geometry setup: Use the reference and the linked element.
# The `picked_ref` is the necessary reference for NewSpotElevation.
topo_ref = picked_ref 

print("Linked Topography Element Name (Reference): {}".format(picked_ref))
print("Linked Topography Surface Name: {}".format(surface_topo.Name))
print("Linked model: {}".format(link_model.Name))
print('the detail items are: {}'.format([e.Name for e in elements]))

#get view 3D by name
view_3d = FilteredElementCollector(doc).OfClass(View3D).WhereElementIsNotElementType().ToElements()
# get view 3D which name is {3D - nizarg}
print([v.Name for v in view_3d])
target_view = next((v for v in view_3d if v.Name == '{3D - nizarg}'), None)
nizar_view = [n for n in view_3d if n.Name == '{3D - nizarg}']
print('nizar_view: {}'.format([n.Name for n in nizar_view]))
link_instance = None
linked_doc = None

if isinstance(link_model, RevitLinkInstance):
    link_instance = link_model
    linked_doc = link_instance.GetLinkDocument()
    topo_filter = ElementCategoryFilter(BuiltInCategory.OST_Topography)
    intersector = ReferenceIntersector(topo_filter, FindReferenceTarget.Face, nizar_view[0])
    print("🌍 Using linked topography: {}".format(link_instance.Name))
else:
    topo_filter = ElementCategoryFilter(BuiltInCategory.OST_Topography)
    intersector = ReferenceIntersector(topo_filter, FindReferenceTarget.Face, nizar_view[0])
    print("🌄 Using local topography: {}".format(link_model.Name))

print('intersector: {}'.format(intersector))
# shoot ray
direction = XYZ(0, 0, -10000000000)
for point in loc:
    base_point = XYZ(point.X, point.Y, point.Z) 
    ref_result = intersector.FindNearest(base_point, direction)

    if ref_result:
        hit_ref = ref_result.GetReference()
        hit_point = ref_result.GetReference().GlobalPoint
        print("✅ Projected point found at Z = {:.2f}".format(hit_point.Z))
    # else:
    #     raise Exception("❌ No intersection found with the topography below the detail item.")
print('ref_result: {}'.format(ref_result))

# current view

t = Transaction(doc, "Project Point onto Topography")
t.Start()

try:
    # # Create a model reference point at the intersection
    # new_point = doc.FamilyCreate.NewReferencePoint(hit_point)
    # print("📌 Created ReferencePoint ID: {}".format(new_point.Id))

    # Optionally, create a spot elevation
    # current_view = doc.ActiveView
# try:
    spot = doc.Create.NewSpotElevation(current_view, hit_ref, base_point, base_point, base_point, hit_point, False)
    print("📍 Created Spot Elevation ID: {}".format(spot.Id))
# except Exception as se:
#     print("⚠️ Could not create spot elevation: {}".format(se))

    t.Commit()
    print("🎯 Projection completed successfully.")

except Exception as e:
    print("❌ Error: {}".format(e))
    t.RollBack()