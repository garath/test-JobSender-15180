using Microsoft.DotNet.Helix.Client;
using Microsoft.DotNet.Helix.Client.Models;
using System;
using System.Collections.Generic;
using System.Linq;

IHelixApi api = ApiFactory.GetAnonymous();

ISentJob job = await api.Job.Define()
    .WithType("mistucke/15180-2")
    .WithTargetQueue("Raspbian.9.Arm32.IoT.Open")
    //.WithTargetQueue("Ubuntu.2004.Amd64.Open")
    .WithSource("mistucke/15180-2")
    .DefineWorkItem("mistucke test workitem")
    .WithCommand("export PYTHONIOENCODING=utf-8 && $HELIX_PYTHONPATH script.py")
    //.WithPayloadUri(new Uri("https://helixde8s23ayyeko0k025g8.blob.core.windows.net/helix-job-33fed28d-e352-4636-b5c2-d2675d2142a4fb0f082979d45709c/XsltCompiler.Tests.zip"))
    //.WithEmptyPayload()
    .WithFiles("script.py")
    .AttachToJob()
    .WithCreator("garath")
    .SendAsync();

Console.WriteLine($"Created job {job.CorrelationId}. Awaiting completion...");

JobPassFail result = await api.Job.WaitForJobAsync(job.CorrelationId);

Console.WriteLine($"Complete!");
Console.WriteLine($"  Passed: {string.Join(", ", result.Passed)}");
Console.WriteLine($"  Failed: {string.Join(", ", result.Failed)}");

//JobDetails details = await api.Job.DetailsAsync(job.CorrelationId);
IEnumerable<WorkItemSummary> summaries = await api.WorkItem.ListAsync(job.CorrelationId);
foreach (WorkItemSummary summary in summaries)
{
    WorkItemDetails details = await api.WorkItem.DetailsAsync(summary.Name, summary.Job);

    if (string.IsNullOrEmpty(details.ConsoleOutputUri))
    {
        Console.WriteLine("  No console log produced");
    }
    else
    {
        Console.WriteLine($"  Console log for workitem {summary.Name}:");
        Console.WriteLine($"    {details.ConsoleOutputUri}");
    }

    if (details.Logs.Any())
    {
        Console.WriteLine($"  ... and other logs:");

        foreach (WorkItemLog log in details.Logs)
        {
            Console.WriteLine($"    {log.Module}: {log.Uri}");
        }
    }
}