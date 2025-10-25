# -*- coding: utf-8 -*-
__title__ = "Key Plan Control"
__doc__ = """Version = 1.0
Date    = 31.07.2024
_____________________________________________________________________
Description:
To match the keyplan control with the view name last syllable (Volume Code).
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
from Autodesk.Revit.UI.Selection import*

# Custom
from Snippets._selection import get_selected_sheets 
# pyRevit
from pyrevit import forms


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#==================================================


# def get_selected_sheets(given_uidoc = uidoc, exit_if_none = False, title='__title__', label='Select Sheets',
#                         btn_name = 'Select Sheets',  version = 'Version: _'):
#     """Function to get selected views. return list of selected views.
#     LastUpdates:
#     [15.02.2022] - If no sheets selected -> Select from DialogBox
#     [01.06.2022] - Bug Fixed + added more controls(label, btn_name)"""
#     #>>>>>>>>>> GET SELECTED ELEMENTS
#     doc         = given_uidoc.Document
#     UI_selected = given_uidoc.Selection.GetElementIds()

#     #>>>>>>>>>> GET SHEETS FROM SELECTION
#     selected_sheets = [doc.GetElement(sheet_id) for sheet_id in UI_selected if type(doc.GetElement(sheet_id)) == ViewSheet]

#     #>>>>>>>>>> IF NONE SELECTED - OPEN A DIALOGBOX TO CHOOSE FROM.
#     if not selected_sheets:
#         all_sheets      = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
#         dict_sheets     = {'{} - {}'.format(sheet.SheetNumber, sheet.Name): sheet for sheet in all_sheets}
#         selected_sheets = select_from_dict(dict_sheets, title=title, label=label, button_name=btn_name, version=version)

#     #>>>>>>>>>> EXIT IF STILL NONE SELECTED
#     if not selected_sheets and exit_if_none:
#         forms.alert("No sheets were selected. Please try again.", exitscript=True)
#     return selected_sheets



selected_elements = get_selected_sheets(uidoc, exit_if_none=True, title=__title__)
first_element    = selected_elements[0]
volume_code_mapping_dictionary = {}

# Ensure the selected sheets have exactly one placed view and that view is a FloorPlan
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



#Get the titleblock family and print the formulas of the instance parameters
for s in first_element.GetDependentElements(ElementCategoryFilter(BuiltInCategory.OST_TitleBlocks)):
    titleblock = doc.GetElement(s)
    titleblock_Type = doc.GetElement(titleblock.GetTypeId())
    family = titleblock_Type.Family
    family_doc = doc.EditFamily(family)
    family_manager = family_doc.FamilyManager
    family_parameters = family_manager.Parameters

    print("Title Block: {}".format(titleblock.Name))
    # get the 1.250 parameters
    param_250 = []
    for param in family_parameters:
        if '250' in param.Definition.Name:
            param_250.append(param)

    for param in param_250:
        if param.IsShared or param.Definition is not None:
            
            formula = None
            try:
                # get the last 3 chracters of the formula if it exists
                keyplan_control_number = param.Formula[-3:]
                # get the last 2 characters of the parameter name
                volume_code_from_param = param.Definition.Name[-2:]
                # create a mapping dictionary
                volume_code_mapping_dictionary[volume_code_from_param] = keyplan_control_number
                formula = param.Formula
            except AttributeError:
                formula = None
            # if formula:
            #     print("    Parameter: {} | Formula: {}".format(param.Definition.Name, formula))


print(volume_code_mapping_dictionary)

# Investigating the parameters of the titleblocks on all selected sheets
# for sheet in selected_elements:
#     # Collect all FamilyInstances of category OST_TitleBlocks on the sheet
#     title_blocks = [doc.GetElement(id) for id in sheet.GetDependentElements(ElementCategoryFilter(BuiltInCategory.OST_TitleBlocks))]
#     #get the formulas of the instance parameters of the titleblock family instances
#     for tb in title_blocks:
#         print('-' * 100)
#         print("Sheet: {} | Title Block: {}".format(sheet.Name, tb.Name))
#         # Print formulas of instance parameters (if any)
#         for param in tb.Parameters:
#             print(param.Definition.Name)
#             if '250' in param.Definition.Name:
#                 try:
#                     print (param.Formula)
#                 except:
#                     print ("No Formula")
#             if param.IsShared or param.Definition is not None:
#                 formula = None
#                 try:
#                     formula = param.Definition.Formula
#                 except AttributeError:
#                     formula = None
#                 if formula:
#                     print("    Parameter: {} | Formula: {}".format(param.Definition.Name, formula))


t = Transaction(doc, 'Automate Keyplan Control')
t.Start()
try:
    for s in working_sheets:
        #get titleblocks on the sheet
        title_blocks = [doc.GetElement(ids) for ids in s.GetDependentElements(ElementCategoryFilter(BuiltInCategory.OST_TitleBlocks))]
        #get the views placed on the sheet
        placed_views = s.GetAllPlacedViews()
        for view in placed_views:
            view_title = doc.GetElement(view).Title
            volume_code = view_title[-2:]
        for tb in title_blocks:
            print ('    - Current keyplan control is: {}'.format(tb.LookupParameter('Keyplan Control').AsInteger()))
            tb.LookupParameter('Keyplan Control').Set(int(volume_code_mapping_dictionary.get(volume_code, 0)))
            # print the current value of the keyplan control parameter
            
            print ('updated keyplan control to: {} to match volume code: {}'.format(volume_code_mapping_dictionary.get(volume_code, 0), volume_code))

    t.Commit()
except Exception as e:
    t.Rollback()
    print("Error occurred while setting Keyplan Control: {}".format(str(e)))

