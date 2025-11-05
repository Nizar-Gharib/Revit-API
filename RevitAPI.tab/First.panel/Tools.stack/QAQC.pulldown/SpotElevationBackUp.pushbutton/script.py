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


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
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
    """Function to get Elements by Type Name."""

    # CREATE RULE
    param_id    = ElementId(BuiltInParameter.ALL_MODEL_TYPE_NAME)
    f_param     = ParameterValueProvider(param_id)
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
                           
# Get Elements                           
elements = get_elements_by_type_name('Spot Elevation Backup')

# Get the user to select linked topography elements


# Get the user to select linked topography elements
selection = uidoc.Selection

#linked
picked_ref = selection.PickObject(ObjectType.LinkedElement, "Select linked topography elements")
# Get the elements from the picked references
link_model = doc.GetElement(picked_ref)
surface_topo = link_model.GetLinkDocument().GetElement(picked_ref.LinkedElementId)
# get the topo as a face to use for projection


ref = Reference(surface_topo)
topo_face = surface_topo.GetGeometryObjectFromReference(ref)

# local
# picked_ref_local = selection.PickObject(ObjectType.Element, "Select local topography elements")
# local_topography = doc.GetElement(picked_ref_local)

# # local_topo_as_ref = local_topography.GetDocument().GetElement(picked_ref_local.ElementId)
# ref_local = Reference(local_topography)


print("Linked Topography Element name: {}".format(picked_ref))
print("Linked Topography surface name: {}".format(surface_topo.Name))
print("Linked model: {}".format(link_model.Name))
# print("Linked Topography Element name: {}".format(ref))
# current view
current_view = doc.ActiveView

#create transaction
t = Transaction(doc, "Create Spot Elevations")
try:
    t.Start()

        # get the center points of the elements
    for el in elements:
        loc = el.Location
        if isinstance(loc, LocationPoint):
            point = loc.Point
            print("Element ID: {}, Location: ({}, {}, {})".format(el.Id, point.X, point.Y, point.Z))
            #project the point onto the topography
            

    # create spot elevations at those points
            try:
                projected_point = topo_face.Project(point).XYZPoint
                spot_elev = doc.Create.NewSpotElevation(current_view, ref, projected_point, point, point, projected_point, False)
                print("Created Spot Elevation ID: {}".format(spot_elev.Id))
            except Exception as inner_e:
                print("❌ Failed for element {}: {}".format(el.Id, inner_e))
    t.Commit()
    print("Script completed successfully.")
    #create exception
except Exception as e:
    print("An error occurred: {}".format(e))