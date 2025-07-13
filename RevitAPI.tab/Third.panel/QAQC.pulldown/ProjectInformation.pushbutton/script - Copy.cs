using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using System;
using System.Collections.Generic;
using System.Linq;

namespace RevitAddin
{
    [Autodesk.Revit.Attributes.Transaction(Autodesk.Revit.Attributes.TransactionMode.Manual)]
    public class SetProjectInfo : IExternalCommand
    {
        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            UIApplication uiapp = commandData.Application;
            UIDocument uidoc = uiapp.ActiveUIDocument;
            Document doc = uidoc.Document;

            string modelName = doc.Title;
            string summary = "Updated Parameters:\n";
            string[] modelNameChar = modelName.Split('-');

            var sharedParamValues = new Dictionary<string, string>
            {
                { "RSG_Asset Code", modelNameChar[1].Substring(0,3) },
                { "RSG_Asset Name", "COUNTRY CLUB ESTATE RESIDENCES" },
                { "RSG_Contract Code", modelNameChar[1].Substring(3) },
                { "RSG_Discipline Code", modelNameChar[6] },
                { "RSG_Doc Type", modelNameChar[5] },
                { "RSG_Model Number", modelName },
                { "RSG_Originator Code", modelNameChar[2] },
                { "RSG_Phase Code", modelNameChar[0].Substring(0,3) },
                { "RSG_Program Code", modelNameChar[0] },
                { "RSG_Program Name", "PROGRAM 02 / COUNTRY CLUB ESTATE RESIDENCES" },
                { "Model Name", modelName },
                { "Organization Description", "BJARKE INGELS GROUP" },
                
                { "RSG_Volume Code", modelNameChar[3] }
            };

            using (Transaction trans = new Transaction(doc, "Set Project Information"))
            {
                trans.Start();

                ProjectInfo projectInfo = new FilteredElementCollector(doc)
                    .OfClass(typeof(ProjectInfo))
                    .Cast<ProjectInfo>()
                    .FirstOrDefault();

                if (projectInfo != null)
                {
                    // Built-in parameters
                    Parameter param;

                    if ((param = projectInfo.get_Parameter(BuiltInParameter.PROJECT_NAME)) != null)
                    {
                        param.Set("AL NUMAN ISLAND");
                        summary += "PROJECT_NAME: AL NUMAN ISLAND\n";
                    }
                        
                    //projectInfo.get_Parameter(BuiltInParameter.ORGANIZATION_DESCRIPTION)?.Set("BJARKE INGELS GROUP");
                    if ((param = projectInfo.get_Parameter(BuiltInParameter.PROJECT_NUMBER)) != null)
                    {
                        param.Set("PROGRAM 02 / COUNTRY CLUB ESTATE RESIDENCES");
                        summary += "PROJECT_NUMBER: PROGRAM 02 / COUNTRY CLUB ESTATE RESIDENCES\n";
                    }
                        
                    if ((param = projectInfo.get_Parameter(BuiltInParameter.PROJECT_STATUS)) != null)
                    {
                        param.Set("SD - SCHEMATIC DESIGN");
                        summary += "PROJECT_STATUS: SD - SCHEMATIC DESIGN\n";
                    }
                        
                    if ((param = projectInfo.get_Parameter(BuiltInParameter.CLIENT_NAME)) != null)
                    {
                        param.Set("Red Sea Global (RSG)");
                        summary += "CLIENT_NAME: Red Sea Global (RSG)\n";
                    }    
                        

                    // Shared parameters using dictionary
                    foreach (Parameter sharedParam in projectInfo.Parameters)
                    {
                        if (sharedParam.IsShared && sharedParamValues.TryGetValue(sharedParam.Definition.Name, out string value))
                        {
                            sharedParam.Set(value);
                            summary += $"{sharedParam.Definition.Name}: {value}\n";
                        }
                    }
                }
                else
                {
                    message = "Project Information element not found.";
                    return Result.Failed;
                }

                trans.Commit();
            }

            TaskDialog.Show("Project Information", summary);
            return Result.Succeeded;
        }
    }
}
