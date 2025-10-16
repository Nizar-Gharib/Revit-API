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
from Autodesk.Revit.DB import Categories
from Autodesk.Revit.DB import Element
from Autodesk.Revit.DB import CategoryNameMap
from Autodesk.Revit.DB import APIObject
from Autodesk.Revit.UI.Selection import*
from Autodesk.Revit.DB import FilteredElementCollector
from pyrevit import forms



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

#🔷 Get Selected Elements

def get_selected_sheets(given_uidoc = uidoc, exit_if_none = False, title='__title__', label='Select Sheets',
                        btn_name = 'Select Sheets',  version = 'Version: _'):
    """Function to get selected views. return list of selected views.
    LastUpdates:
    [15.02.2022] - If no sheets selected -> Select from DialogBox
    [01.06.2022] - Bug Fixed + added more controls(label, btn_name)"""
    #>>>>>>>>>> GET SELECTED ELEMENTS
    doc         = given_uidoc.Document
    UI_selected = given_uidoc.Selection.GetElementIds()

    #>>>>>>>>>> GET SHEETS FROM SELECTION
    selected_sheets = [doc.GetElement(sheet_id) for sheet_id in UI_selected if type(doc.GetElement(sheet_id)) == ViewSheet]

    #>>>>>>>>>> IF NONE SELECTED - OPEN A DIALOGBOX TO CHOOSE FROM.
    if not selected_sheets:
        all_sheets      = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
        dict_sheets     = {'{} - {}'.format(sheet.SheetNumber, sheet.Name): sheet for sheet in all_sheets}
        selected_sheets = select_from_dict(dict_sheets, title=title, label=label, button_name=btn_name, version=version)

    #>>>>>>>>>> EXIT IF STILL NONE SELECTED
    if not selected_sheets and exit_if_none:
        forms.alert("No sheets were selected. Please try again.", exitscript=True)
    return selected_sheets


selected_elements = get_selected_sheets(uidoc, exit_if_none=True, title=__title__)

working_sheets = []

for i in selected_elements:
    placed_views = i.GetAllPlacedViews()
    # Filter for sheets with exactly one placed view and that view is a FloorPlan
    if len(placed_views) == 1:
        for v in placed_views:
            view_obj = doc.GetElement(v)
            view_type = view_obj.ViewType
            if view_type == ViewType.FloorPlan:
                print(i.Title)
                print(' - Placed View Type: {}'.format(view_type))
                # Proceed with further processing here
                working_sheets.append(i)
            else:
                print('Sheet "{}" does not have a Floor Plan view.'.format(i.Title))
    else:
        print('Sheet "{}" does not have exactly one placed view.'.format(i.Title))



print(len(working_sheets))
print(working_sheets)

    

# Start a transaction before modifying parameters
t = Transaction(doc, 'Set BIG_Sheet Volume Code')
t.Start()
try:
    for s in working_sheets:
        working_placed_views = s.GetAllPlacedViews()
        for view in working_placed_views:
            view_title = doc.GetElement(view).Title
            volume_code = view_title[-2:]
            print ('    - view title: {}'.format(view_title))
            print('     - Volume Code: {}'.format(volume_code))
        s.LookupParameter('BIG_Sheet Volume Code').Set(volume_code)
    t.Commit()
except Exception as e:
    t.Rollback()
    print("Error occurred while setting BIG_Sheet Volume Code: {}".format(str(e)))




# t = Transaction(doc, 'Modify Subcategory Properties')
# t.Start()
# try:
#     for (layer_name, R, G, B, LW, LP_id) in data:
#         override_dwg_layers(layer_name, R, G, B, LW, LP_id)

#     t.Commit()
# except Exception as e:
#     t.RollBack()
#     print("Error occurred: %s" % str(e))