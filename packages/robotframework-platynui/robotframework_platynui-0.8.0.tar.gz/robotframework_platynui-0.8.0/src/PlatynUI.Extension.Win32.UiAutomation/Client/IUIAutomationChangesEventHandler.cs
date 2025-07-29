// SPDX-FileCopyrightText: 2024 Daniel Biehl <daniel.biehl@imbus.de>
//
// SPDX-License-Identifier: Apache-2.0

using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Extension.Win32.UiAutomation.Client;

[TypeLibType(TypeLibTypeFlags.FOleAutomation)]
[Guid("58EDCA55-2C3E-4980-B1B9-56C17F27A2A0")]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[ComImport]
public interface IUIAutomationChangesEventHandler
{
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    void HandleChangesEvent(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement sender,
        [In] ref UiaChangeInfo uiaChanges,
        [In] int changesCount
    );
}
