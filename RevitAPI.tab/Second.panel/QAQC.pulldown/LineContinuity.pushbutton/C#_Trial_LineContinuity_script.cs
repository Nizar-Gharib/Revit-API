using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using Autodesk.Revit.UI.Selection;

[Transaction(TransactionMode.Manual)]
public class FamilyTypeNamingValidator : IExternalCommand
{
        public Result Execute(
    ExternalCommandData commandData,
    ref string message,
    ElementSet elements)
    {
        UIDocument uidoc = commandData.Application.ActiveUIDocument;
        Document doc = uidoc.Document;
        View view = doc.ActiveView;

        // Create red color override
        OverrideGraphicSettings ogs = new OverrideGraphicSettings();
        ogs.SetProjectionLineColor(new Color(255, 0, 0));

        // Get all model or detail lines in the view
        FilteredElementCollector collector = new FilteredElementCollector(doc, view.Id);
        collector.OfClass(typeof(CurveElement));

        List<CurveElement> lines = collector.Cast<CurveElement>().ToList();

        // Loop through all lines and find those with matching direction and endpoints
        for (int i = 0; i < lines.Count; i++)
        {
            CurveElement line1 = lines[i];
            Curve curve1 = line1.GeometryCurve;
            XYZ dir1 = (curve1.GetEndPoint(1) - curve1.GetEndPoint(0)).Normalize();

            for (int j = i + 1; j < lines.Count; j++)
            {
                CurveElement line2 = lines[j];
                Curve curve2 = line2.GeometryCurve;
                XYZ dir2 = (curve2.GetEndPoint(1) - curve2.GetEndPoint(0)).Normalize();

                // Check if they are colinear and touching
                if (dir1.IsAlmostEqualTo(dir2) || dir1.IsAlmostEqualTo(dir2.Negate()))
                {
                    bool touching = curve1.GetEndPoint(0).IsAlmostEqualTo(curve2.GetEndPoint(0)) ||
                                    curve1.GetEndPoint(0).IsAlmostEqualTo(curve2.GetEndPoint(1)) ||
                                    curve1.GetEndPoint(1).IsAlmostEqualTo(curve2.GetEndPoint(0)) ||
                                    curve1.GetEndPoint(1).IsAlmostEqualTo(curve2.GetEndPoint(1));

                    if (touching)
                    {
                        using (Transaction t = new Transaction(doc, "Override Line Graphics"))
                        {
                            t.Start();
                            view.SetElementOverrides(line1.Id, ogs);
                            view.SetElementOverrides(line2.Id, ogs);
                            t.Commit();
                        }
                    }
                }
            }
        }

        return Result.Succeeded;
    }

}
