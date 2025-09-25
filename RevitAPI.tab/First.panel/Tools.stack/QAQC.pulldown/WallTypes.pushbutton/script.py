# -*- coding: utf-8 -*-
__title__ = "Rename Views"
__doc__ = """Version = 1.0
Date    = 31.07.2024
_____________________________________________________________________
Description:
Rename Views in Revit by using Find/Replace Logic.
_____________________________________________________________________
How-to:
-> Click on the button
-> Select Views
-> Define Renaming Rules
-> Rename Views
_____________________________________________________________________
Last update:
- [31.07.2024] - 1.0 RELEASE
_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
# Regular + Autodesk
from Autodesk.Revit.DB import *
# pyRevit
# from pyrevit import forms

from Autodesk.Revit.UI.Selection import ObjectType
from Autodesk.Revit.UI.Selection import PickBoxStyle
from Autodesk.Revit.DB import FilteredElementCollector

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


# Select Elements
# selected_element_ids = uidoc.Selection.GetElementIds()
# selected_elements    = [doc.GetElement(e_id) for e_id in selected_element_ids]
# print(selected_elements)
#
# # Filter Selection (Optionally)
# filtered_elements = [el for el in selected_elements if type(el) == Wall]
# print('filtered elements are: {}'.format(filtered_elements))

# #🟠 2. Pick Elements by Rectangle
# selected_elements = uidoc.Selection.PickElementsByRectangle('Select some Elements.')
# print(selected_elements)

#3 pick object
# ref_pick_object = uidoc.Selection.PickObject(ObjectType.Face, 'Select an Element.')
#
# picked_element = doc.GetElement(ref_pick_object)
# print(ref_pick_object)
# print('_'*50)
# print(picked_element)

#3 pick objects
# ref_picked_objects = uidoc.Selection.PickObjects(ObjectType.PointOnElement, 'Select some Elements.')
# picked_elements = [doc.GetElement(ref) for ref in ref_picked_objects]
# points_xyz = [ref.GlobalPoint for ref in ref_picked_objects]
# for p in points_xyz:
#     print (p)
# print('_'*50)
#
# for el in picked_elements:
#     print(el)

#4 pick point
# selected_pt = uidoc.Selection.PickPoint('Pick a Point.')
# print(selected_pt)

#5 pick box
# select_elements = uidoc.Selection.PickBox(PickBoxStyle.Directional, 'Select some Elements.')
#
# print(select_elements)
# print(select_elements.Min)
# print(select_elements.Max)

#⬇️ Imports


#🎯 Set Selection in Revit UI
# new_selection = FilteredElementCollector(doc).OfClass(Wall).ToElementIds()
# uidoc.Selection.SetElementIds(new_selection) #🔓 No need for transaction! It's just UI change

# This works because ToElementIds methods returns List[ElementId]

#Current selection
# current_selection = uidoc.Selection
# selected_ids = uidoc.Selection.GetElementIds()
#
# if (0 == selected_ids.Count):
#     print("You haven't selected any elements.")
#     # TaskDialog.Show("Revit", "You haven't selected any elements.")
# else:
#     info_message = "Ids of selected elements in the document are: "
#     for i in selected_ids:
#         info_message += "\n\t" + i.ToString()
#     print(info_message)

# TaskDialog.Show("Revit", info_message)


# ____________________________________
#Typed List


# Python List
el_ids = [ElementId(389303), ElementId(916523)] # List of ElementIds

# Import .NET List
import clr
clr.AddReference('System')
from System.Collections.Generic import List

# Convert to .NET List
List_el_ids = List[ElementId](el_ids)


#🎯 Set Selection in Revit UI
uidoc.Selection.SetElementIds(List_el_ids)
#🔓 No need for transaction! It's just UI change