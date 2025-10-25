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
                                
# Get Elements                           
elements = get_elements_by_type_name('Spot Elevation Backup')

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

# Check if the element is indeed a TopographySurface or similar
if not isinstance(surface_topo, Surface):
    print("❌ Selected element is not a TopographySurface. Cannot use Get=ElevationWith*/GetXYZ().")
    exit()

print("Linked Topography Element Name (Reference): {}".format(picked_ref))
print("Linked Topography Surface Name: {}".format(surface_topo.Name))
print("Linked model: {}".format(link_model.Name))

# current view
current_view = doc.ActiveView

#create transaction
t = Transaction(doc, "Create Spot Elevations")
try:
    t.Start()

    # Get the transform from the Link Instance
    link_transform = link_model.GetLinkDocument().ActiveProjectLocation.GetProjectPosition(XYZ.Zero).GlobalPoint
    # In most cases, the link's transform is just the Identity matrix if no positioning is applied,
    # but the correct way to transform the point from host to link coordinate system is vital.
    link_instance_transform = link_model.GetTransform()
    
    # get the center points of the elements
    for el in elements:
        loc = el.Location
        if isinstance(loc, LocationPoint):
            point_base = loc.Point # Point in Host coordinates
            print("Element ID: {}, Location: ({}, {}, {})".format(el.Id, point_base.X, point_base.Y, point_base.Z))
            
            try:
                # 1. Transform the host point to the linked document's coordinates
                # This is crucial for using GetElevationWithCurves or similar methods on the linked TopographySurface.
                point_in_link = link_instance_transform.Inverse.OfPoint(point_base)

                # 2. Get the elevation from the TopographySurface in the link document
                # This is the correct way to "project" a point onto a TopographySurface.
                # NOTE: This method requires the point to be in the Topo's own coordinate system (i.e., the link's).
                
                # Check for newer method (Revit 2021+)
                if rvt_year >= 2021:
                    elevation_in_link = surface_topo.GetElevationWithCurves(point_in_link)
                else:
                    elevation_in_link = surface_topo.GetElevation(point_in_link)

                
                # 3. Create the projected point (in Host coordinates)
                # Take the original X, Y (host coords) and the new Z (transformed back from link coords)
                
                # The elevation_in_link is an absolute Z value in the link's coordinates.
                # To get the final point in the HOST document:
                projected_point_link = XYZ(point_in_link.X, point_in_link.Y, elevation_in_link)
                projected_point_host = link_instance_transform.OfPoint(projected_point_link)

                # 4. Define points for NewSpotElevation (using host coordinates)
                
                # pOrigin: The point on the element (the projected point)
                origin_pt = projected_point_host
                
                # pElbow and pLeader define the placement (offset from the backup element location)
                offset_x = 5.0 
                elbow_pt = XYZ(point_base.X + offset_x, point_base.Y, projected_point_host.Z)
                leader_end_pt = XYZ(point_base.X + offset_x * 2, point_base.Y, projected_point_host.Z)
                
                # pPlane: Annotation placement point (using the backup element's location)
                plane_pt = point_base 
                
                # 5. Create the Spot Elevation
                spot_elev = doc.Create.NewSpotElevation(
                    current_view, 
                    topo_ref, # Reference to the linked element
                    origin_pt, 
                    elbow_pt, 
                    leader_end_pt, 
                    plane_pt, 
                    False 
                )
                
                print("Created Spot Elevation ID: {}".format(spot_elev.Id))
                
            except Exception as inner_e:
                print("❌ Failed for element {}: {}".format(el.Id, inner_e))
    
    t.Commit()
    print("Script completed successfully.")
    
except Exception as e:
    # Always roll back on error
    if t.GetStatus() == TransactionStatus.Started:
        t.RollBack()
    print("An error occurred: {}".format(e))