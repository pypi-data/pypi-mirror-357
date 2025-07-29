// SPDX-FileCopyrightText: 2024 Daniel Biehl <daniel.biehl@imbus.de>
//
// SPDX-License-Identifier: Apache-2.0

using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Extension.Win32.UiAutomation.Client;

[Guid("C7CB2637-E6C2-4D0C-85DE-4948C02175C7")]
[TypeLibType(TypeLibTypeFlags.FOleAutomation)]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[ComImport]
public interface IUIAutomationNotificationEventHandler
{
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    void HandleNotificationEvent(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement sender,
        NotificationKind NotificationKind,
        NotificationProcessing NotificationProcessing,
        [MarshalAs(UnmanagedType.BStr), In] string displayString,
        [MarshalAs(UnmanagedType.BStr), In] string activityId
    );
}
