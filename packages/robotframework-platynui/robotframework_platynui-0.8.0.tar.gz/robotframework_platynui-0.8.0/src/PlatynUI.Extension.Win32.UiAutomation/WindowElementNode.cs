// SPDX-FileCopyrightText: 2024 Daniel Biehl <daniel.biehl@imbus.de>
//
// SPDX-License-Identifier: Apache-2.0

using PlatynUI.Extension.Win32.UiAutomation.Client;
using INode = PlatynUI.Runtime.Core.INode;

namespace PlatynUI.Extension.Win32.UiAutomation;

public class WindowElementNode(INode? parent, IUIAutomationElement element) : ElementNode(parent, element)
{
    readonly Patterns.WindowPattern? pattern = Patterns.GetWindowPattern(element);

    public override object? GetStrategy(string name, bool throwException = true)
    {
        switch (name)
        {
            case "org.platynui.strategies.HasCanMinimize":
            case "org.platynui.strategies.HasCanMaximize":
            case "org.platynui.strategies.HasIsActive":
            case "org.platynui.strategies.Activatable":
                return this;
            default:
                return base.GetStrategy(name, throwException);
        }
    }

    public bool is_minimized => pattern?.IsMinimized ?? false;
    public bool is_maximized => pattern?.IsMaximized ?? false;

    public bool is_active => pattern?.IsActive ?? false;

    public void activate()
    {
        pattern?.Activate();
    }
}
