using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CSCI3280_GP_Project
{
    static class FunctionCalling
    {
        public static void CallPythonFunction(string arg = "")
        {
            string path = "python";

            //string arg = Application.persistentDataPath + $"/try.py";

            // Create a process
            Process process = new Process();

            // Set the StartInfo of process
            process.StartInfo.FileName = path;
            process.StartInfo.Arguments = arg;

            process.StartInfo.UseShellExecute = false;
            process.StartInfo.RedirectStandardOutput = true;
            process.StartInfo.RedirectStandardError = true;

            process.StartInfo.CreateNoWindow = true;
            //process.StartInfo.WindowStyle = ProcessWindowStyle.Normal;

            // Start the process
            process.Start();

            string consoleMessage = process.StandardOutput.ReadToEnd();
            string errorMessage = process.StandardError.ReadToEnd();
            process.WaitForExit();
        }
    }
}
