// SPDX-FileCopyrightText: 2024 Daniel Biehl <daniel.biehl@imbus.de>
//
// SPDX-License-Identifier: Apache-2.0

using System.ComponentModel.Composition;
using PlatynUI.Extension.Win32.UiAutomation.Client;
using PlatynUI.Extension.Win32.UiAutomation.Core;
using PlatynUI.Runtime;
using PlatynUI.Runtime.Core;

[assembly: PlatynUiExtension(supportedPlatforms: [RuntimePlatform.Windows])]

namespace PlatynUI.Extension.Win32.UiAutomation;

[Export(typeof(INodeProvider))]
class NodeProvider : INodeProvider
{
    public IEnumerable<Runtime.Core.INode> GetNodes(Runtime.Core.INode parent)
    {
        var processIds = new HashSet<int>();

        foreach (var e in Automation.RootElement.EnumerateChildren(Automation.RawViewWalker, true))
        {
            if (e == null)
            {
                continue;
            }
            processIds.Add(e.CurrentProcessId);
            if (e.TryGetCurrentPattern(out IUIAutomationWindowPattern? pattern))
            {
                if (pattern != null)
                {
                    yield return new WindowElementNode(parent, e);
                }
            }
            else
            {
                yield return new ElementNode(parent, e);
            }
        }

        foreach (var processId in processIds)
        {
            yield return new ApplicationNode(parent, processId);
        }
    }
}
