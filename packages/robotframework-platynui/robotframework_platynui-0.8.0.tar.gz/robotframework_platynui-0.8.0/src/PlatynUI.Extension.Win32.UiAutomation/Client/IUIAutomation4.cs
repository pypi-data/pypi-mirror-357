// SPDX-FileCopyrightText: 2024 Daniel Biehl <daniel.biehl@imbus.de>
//
// SPDX-License-Identifier: Apache-2.0

using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Extension.Win32.UiAutomation.Client;

[Guid("1189C02A-05F8-4319-8E21-E817E3DB2860")]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[ComImport]
public interface IUIAutomation4 : IUIAutomation3
{
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new int CompareElements(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement el1,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement el2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new int CompareRuntimeIds(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] runtimeId1,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] runtimeId2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationElement GetRootElement();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationElement ElementFromHandle([In] IntPtr hwnd);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationElement ElementFromPoint([In] tagPOINT pt);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationElement GetFocusedElement();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationElement GetRootElementBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationElement ElementFromHandleBuildCache(
        [In] IntPtr hwnd,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationElement ElementFromPointBuildCache(
        [In] tagPOINT pt,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationElement GetFocusedElementBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationTreeWalker CreateTreeWalker(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition pCondition
    );

    [DispId(1610678283)]
    new IUIAutomationTreeWalker ControlViewWalker
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [DispId(1610678284)]
    new IUIAutomationTreeWalker ContentViewWalker
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [DispId(1610678285)]
    new IUIAutomationTreeWalker RawViewWalker
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [DispId(1610678286)]
    new IUIAutomationCondition RawViewCondition
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [DispId(1610678287)]
    new IUIAutomationCondition ControlViewCondition
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [DispId(1610678288)]
    new IUIAutomationCondition ContentViewCondition
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationCacheRequest CreateCacheRequest();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationCondition CreateTrueCondition();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationCondition CreateFalseCondition();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationCondition CreatePropertyCondition(
        [In] int propertyId,
        [MarshalAs(UnmanagedType.Struct), In] object value
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationCondition CreatePropertyConditionEx(
        [In] int propertyId,
        [MarshalAs(UnmanagedType.Struct), In] object value,
        [In] PropertyConditionFlags flags
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationCondition CreateAndCondition(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition1,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationCondition CreateAndConditionFromArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_UNKNOWN), In]
            IUIAutomationCondition[] conditions
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationCondition CreateAndConditionFromNativeArray(
        [MarshalAs(UnmanagedType.Interface), In] ref IUIAutomationCondition conditions,
        [In] int conditionCount
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationCondition CreateOrCondition(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition1,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationCondition CreateOrConditionFromArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_UNKNOWN), In]
            IUIAutomationCondition[] conditions
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationCondition CreateOrConditionFromNativeArray(
        [MarshalAs(UnmanagedType.Interface), In] ref IUIAutomationCondition conditions,
        [In] int conditionCount
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationCondition CreateNotCondition(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new void AddAutomationEventHandler(
        [In] int eventId,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new void RemoveAutomationEventHandler(
        [In] int eventId,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new void AddPropertyChangedEventHandlerNativeArray(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationPropertyChangedEventHandler handler,
        [In] ref int propertyArray,
        [In] int propertyCount
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new void AddPropertyChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationPropertyChangedEventHandler handler,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] propertyArray
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new void RemovePropertyChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationPropertyChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new void AddStructureChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationStructureChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new void RemoveStructureChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationStructureChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new void AddFocusChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationFocusChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new void RemoveFocusChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationFocusChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new void RemoveAllEventHandlers();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT)]
    new int[] IntNativeArrayToSafeArray([In] ref int array, [In] int arrayCount);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new int IntSafeArrayToNativeArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] intArray,
        [Out] IntPtr array
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Struct)]
    new object RectToVariant([In] tagRECT rc);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new tagRECT VariantToRect([MarshalAs(UnmanagedType.Struct), In] object var);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new int SafeArrayToRectNativeArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_R8), In] double[] rects,
        [Out] IntPtr rectArray
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationProxyFactoryEntry CreateProxyFactoryEntry(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationProxyFactory factory
    );

    [DispId(1610678317)]
    new IUIAutomationProxyFactoryMapping ProxyFactoryMapping
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.BStr)]
    new string GetPropertyProgrammaticName([In] int property);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.BStr)]
    new string GetPatternProgrammaticName([In] int pattern);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new void PollForPotentialSupportedPatterns(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement pElement,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT)] out int[] patternIds,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_BSTR)] out string[] patternNames
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new void PollForPotentialSupportedProperties(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement pElement,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT)] out int[] propertyIds,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_BSTR)] out string[] propertyNames
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new int CheckNotSupported([MarshalAs(UnmanagedType.Struct), In] object value);

    [DispId(1610678323)]
    new object ReservedNotSupportedValue
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.IUnknown)]
        get;
    }

    [DispId(1610678324)]
    new object ReservedMixedAttributeValue
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.IUnknown)]
        get;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationElement ElementFromIAccessible(
        [MarshalAs(UnmanagedType.Interface), In] IAccessible accessible,
        [In] int childId
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationElement ElementFromIAccessibleBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IAccessible accessible,
        [In] int childId,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [DispId(1610743808)]
    new int AutoSetFocus
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    [DispId(1610743810)]
    new uint ConnectionTimeout
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    [DispId(1610743812)]
    new uint TransactionTimeout
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new void AddTextEditTextChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [In] TextEditChangeType TextEditChangeType,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationTextEditTextChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new void RemoveTextEditTextChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationTextEditTextChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    void AddChangesEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [In] ref int changeTypes,
        [In] int changesCount,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest pCacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationChangesEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    void RemoveChangesEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationChangesEventHandler handler
    );
}
