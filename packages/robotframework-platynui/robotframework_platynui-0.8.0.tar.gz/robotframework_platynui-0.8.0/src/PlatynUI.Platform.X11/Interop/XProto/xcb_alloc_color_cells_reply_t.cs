using System.Runtime.CompilerServices;

namespace PlatynUI.Platform.X11.Interop.XCB;

public partial struct xcb_alloc_color_cells_reply_t
{
    [NativeTypeName("uint8_t")]
    public byte response_type;

    [NativeTypeName("uint8_t")]
    public byte pad0;

    [NativeTypeName("uint16_t")]
    public ushort sequence;

    [NativeTypeName("uint32_t")]
    public uint length;

    [NativeTypeName("uint16_t")]
    public ushort pixels_len;

    [NativeTypeName("uint16_t")]
    public ushort masks_len;

    [NativeTypeName("uint8_t[20]")]
    public _pad1_e__FixedBuffer pad1;

    [InlineArray(20)]
    public partial struct _pad1_e__FixedBuffer
    {
        public byte e0;
    }
}
