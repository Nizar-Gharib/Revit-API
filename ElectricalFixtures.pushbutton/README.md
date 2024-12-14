This script was written in C# and it's supposed to refer to Excel file, this means there should be external references allow it to access the Excel application.
However, in order for it to be used in pyRevit, it was modified to use "Dictionary" instead of excel because this is a must if you are using C# script in pyRevit (not to refer to externals) 
Why pyRevit? because at that time it was easier to spread among the team The code can be easily modified to match any input/output accordingly.
