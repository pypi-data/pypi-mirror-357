namespace PlatynUI.Platform.X11.Interop.XCB;

public unsafe partial struct xcb_icccm_get_wm_colormap_windows_reply_t
{
    [NativeTypeName("uint32_t")]
    public uint windows_len;

    [NativeTypeName("xcb_window_t *")]
    public uint* windows;

    public xcb_get_property_reply_t* _reply;
}
