using System;
using System.Linq;
using System.Collections.Generic;
using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;

[Transaction(TransactionMode.Manual)]
public class SetLinkViewOverrides : IExternalCommand
{
    public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
    {
        UIApplication uiApp = commandData.Application;
        UIDocument uiDoc = uiApp.ActiveUIDocument;
        Document doc = uiDoc.Document;

        // Define dictionary: { Host View Name → Linked View Name }
        Dictionary<string, string> viewMapping = new Dictionary<string, string>
        {
            { "A3 CLIFF HOUSE (WEST) - GENERAL ARRANGEMENT PLAN Copy 1", "Testing Sheet Nested View_WIP_NG" },
            { "B4 CLIFF HOUSE (EAST) - GENERAL ARRANGEMENT PLAN Copy 1", "Testing Sheet Nested View_WIP_NG Copy 1" },
            { "First Floor", "Linked First Floor" }
            // Add more mappings as needed
        };

        // Collect all Revit link instances
        List<RevitLinkInstance> linkInstances = new FilteredElementCollector(doc)
            .OfClass(typeof(RevitLinkInstance))
            .Cast<RevitLinkInstance>()
            .ToList();

        int successCount = 0;

        using (Transaction trans = new Transaction(doc, "Set Linked Views"))
        {
            trans.Start();

            // Iterate through all views in the document
            foreach (View hostView in new FilteredElementCollector(doc)
                     .OfClass(typeof(View))
                     .Cast<View>()
                     .Where(v => !v.IsTemplate)) // Ignore templates
            {
                // Check if this view has a mapping
                if (!viewMapping.TryGetValue(hostView.Name, out string linkedViewName))
                    continue; // Skip if no linked view is assigned

                foreach (var linkInstance in linkInstances)
                {
                    Document linkDoc = linkInstance.GetLinkDocument();
                    if (linkDoc == null) continue; // Skip unloaded links

                    // Find the specified linked view
                    View linkedView = new FilteredElementCollector(linkDoc)
                        .OfClass(typeof(View))
                        .Cast<View>()
                        .FirstOrDefault(v => !v.IsTemplate && v.Name == linkedViewName);

                    if (linkedView != null)
                    {
                        // Apply "By Linked View" override
                        SetLinkViewOverride(hostView, linkInstance.Id, linkedView.Id);
                        successCount++;
                    }
                }
            }

            trans.Commit();
        }

        TaskDialog.Show("Result", successCount > 0
            ? $"Linked views applied to {successCount} views."
            : "No linked views were set. Check view names in dictionary.");

        return Result.Succeeded;
    }

    /// <summary>
    /// Sets the visibility override of a linked model in a view to "By Linked View".
    /// </summary>
    private void SetLinkViewOverride(View hostView, ElementId linkElementId, ElementId linkedViewId)
    {
        RevitLinkGraphicsSettings settings = new RevitLinkGraphicsSettings
        {
            LinkVisibilityType = LinkVisibility.ByLinkView,
            LinkedViewId = linkedViewId
        };

        hostView.SetLinkOverrides(linkElementId, settings);
    }
}
