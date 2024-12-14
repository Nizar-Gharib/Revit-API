using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.DB.Electrical;
using Autodesk.Revit.UI;
using Autodesk.Revit.UI.Selection;
using System;
using System.Collections.Generic;
using System.Windows.Media.Animation;

namespace CopyPaste
{
    [Transaction(TransactionMode.Manual)]
    public class TypeMarkMappingDictionaryElectrical : IExternalCommand
    {
        public Result Execute(
            ExternalCommandData commandData,
            ref string message,
            ElementSet elements)
        {
            // Define the mappings directly in the code (substring -> Type Mark value)
            Dictionary<string, string> eleTypeMarkMappings = new Dictionary<string, string>
            {

                {"HD33B", "HD-33B"},
                {"HD-33B" , "HD-33B"},
                {"HD33C", "HD-33C"},
                {"HD-33C" , "HD-33C"},
                {"HD33D", "HD-33D"},
                {"HD-33D" , "HD-33D"},
                {"HD33E", "HD-33E"},
                {"HD-33E" , "HD-33E"},
                {"HD33F", "HD-33F"},
                {"HD-33F" , "HD-33F"},
                {"HD-33G" , "HD-33G"},
                {"HD33G", "HD-33G"},
                {"HD30", "HD-30"},
                {"HD-30", "HD-30"},
                {"Single", "HD-24"},
                {"Duplex", "HD-25"},
                {"EL1", "LT-01"},
                {"EL2", "HD-33A"},
                
                // Add additional mappings here
            };

            // Define the mappings directly in the code (substring -> Type Comment value)
            Dictionary<string, string> eleTypeCommentMappings = new Dictionary<string, string>
            {

                {"HD33B", "KEYPAD ENTRANCE"},
                {"HD-33B" , "KEYPAD ENTRANCE"},
                {"HD33C", "THERMOSTAT"},
                {"HD-33C" , "THERMOSTAT"},
                {"HD33D", "WAREDROBE LIGHTS"},
                {"HD-33D" , "WAREDROBE LIGHTS"},
                {"HD33E", "KEYPAD WC"},
                {"HD-33E" , "KEYPAD WC"},
                {"HD33F", "BATH LIGHT"},
                {"HD-33F" , "BATH LIGHT"},
                {"HD-33G" , "TERRACE LIGHT SWITCH"},
                {"HD33G", "TERRACE LIGHT SWITCH"},
                {"HD30", "2 BUTTON SWITCH"},
                {"HD-30", "2 BUTTON SWITCH"},
                {"Single", "1 GANG OUTLET"},
                {"Duplex", "2 GANG OUTLET"},
                {"EL1", "READING LIGHTS"},
                {"EL2", "HEADBOARD KEYPAD"},
                
                // Add additional mappings here
            };

            // Get the active document in Revit
            Document doc = commandData.Application.ActiveUIDocument.Document;

            // Start a transaction
            using (Transaction transaction = new Transaction(doc, "Set Wall Type Marks"))
            {
                transaction.Start();

                // Get all wall types in the document
                FilteredElementCollector collector = new FilteredElementCollector(doc)
                    .OfCategory(BuiltInCategory.OST_ElectricalFixtures);
                                
                foreach (Element wallType in collector)
                {
                    // Get the wall type name
                    string wallTypeName = wallType.Name;

                    // Check if the wall type name contains any of the keys in the dictionary
                    foreach (var entry in eleTypeMarkMappings)
                    {
                        if (wallTypeName.Contains(entry.Key))
                        {
                            // Get the Type Mark parameter
                            Parameter typeMarkParam = wallType.LookupParameter("Type Mark");

                            // Set the Type Mark to the mapped value if writable
                            if (typeMarkParam != null && !typeMarkParam.IsReadOnly)
                            {
                                typeMarkParam.Set(entry.Value);
                            }
                            break;
                        }
                    }

                    // Check if the wall type name contains any of the keys in the dictionary
                    foreach (var entry in eleTypeCommentMappings)
                    {
                        if (wallTypeName.Contains(entry.Key))
                        {
                            // Get the Type Mark parameter
                            Parameter typeMarkParam = wallType.LookupParameter("Type Comments");

                            // Set the Type Mark to the mapped value if writable
                            if (typeMarkParam != null && !typeMarkParam.IsReadOnly)
                            {
                                typeMarkParam.Set(entry.Value);
                            }
                            break;
                        }
                    }
                }

                transaction.Commit();
            }

            return Result.Succeeded;
        }
    }
}
