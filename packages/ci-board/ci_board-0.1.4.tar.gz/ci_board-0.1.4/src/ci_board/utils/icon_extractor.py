# 杂鱼♡～Windows图标提取核心功能模块喵～
# 本喵使用ctypes直接调用Windows API，完美处理透明度～～
"""
Windows图标提取核心功能
====================

本模块提供了从Windows可执行文件和其他文件中提取图标的核心功能喵～
支持大图标和小图标，完美处理透明度♡～
"""

import ctypes
from ctypes.wintypes import HWND, UINT, LPCSTR, DWORD, HICON, WORD, LONG, BYTE, HANDLE
from PIL import Image
import io
import os
from typing import Optional, Union

from .win32_api import Win32API, Win32Structures
from ci_board.utils import get_component_logger

# 杂鱼♡～获取组件专用logger喵～
logger = get_component_logger("utils.icon_extractor")

# 杂鱼♡～定义HBITMAP类型喵～
HBITMAP = HANDLE

# 杂鱼♡～Windows结构体定义区域喵～
class ICONINFO(ctypes.Structure):
    """杂鱼♡～图标信息结构体喵～"""
    _fields_ = [
        ("fIcon", ctypes.c_bool),      # 是否为图标（True）还是光标（False）
        ("xHotspot", DWORD),           # 光标热点x坐标
        ("yHotspot", DWORD),           # 光标热点y坐标
        ("hbmMask", HBITMAP),          # 掩码位图句柄
        ("hbmColor", HBITMAP)          # 颜色位图句柄
    ]

class RGBQUAD(ctypes.Structure):
    """杂鱼♡～RGB颜色结构体喵～"""
    _fields_ = [
        ("rgbBlue", BYTE),
        ("rgbGreen", BYTE),
        ("rgbRed", BYTE),
        ("rgbReserved", BYTE)
    ]

class BITMAPINFO(ctypes.Structure):
    """杂鱼♡～位图信息结构体喵～"""
    _fields_ = [
        ("bmiHeader", Win32Structures.BITMAPINFOHEADER),
        ("bmiColors", RGBQUAD * 1)
    ]

class SHFILEINFO(ctypes.Structure):
    """杂鱼♡～文件信息结构体喵～"""
    _fields_ = [
        ("hIcon", HICON),
        ("iIcon", ctypes.c_int),
        ("dwAttributes", DWORD),
        ("szDisplayName", ctypes.c_char * 260),
        ("szTypeName", ctypes.c_char * 80)
    ]

# 杂鱼♡～常量定义区域喵～
SHGFI_ICON = 0x000000100
SHGFI_LARGEICON = 0x000000000
SHGFI_SMALLICON = 0x000000001
BI_RGB = 0
DIB_RGB_COLORS = 0
DI_NORMAL = 0x0003

def _setup_icon_api():
    """杂鱼♡～设置图标相关Windows API函数的参数类型，避免类型转换错误喵～"""
    # GetIconInfo
    Win32API.user32.GetIconInfo.argtypes = [HICON, ctypes.POINTER(ICONINFO)]
    Win32API.user32.GetIconInfo.restype = ctypes.c_bool
    
    # DrawIconEx
    Win32API.user32.DrawIconEx.argtypes = [
        HANDLE,  # HDC
        ctypes.c_int,  # xLeft
        ctypes.c_int,  # yTop
        HICON,  # hIcon
        ctypes.c_int,  # cxWidth
        ctypes.c_int,  # cyWidth
        UINT,  # istepIfAniCur
        HANDLE,  # hbrFlickerFreeDraw
        UINT  # diFlags
    ]
    Win32API.user32.DrawIconEx.restype = ctypes.c_bool
    
    # DestroyIcon
    Win32API.user32.DestroyIcon.argtypes = [HICON]
    Win32API.user32.DestroyIcon.restype = ctypes.c_bool
    
    # 杂鱼♡～GDI函数类型定义喵～
    # CreateDIBSection
    Win32API.gdi32.CreateDIBSection.argtypes = [
        HANDLE,  # HDC
        ctypes.c_void_p,  # BITMAPINFO*
        UINT,  # usage
        ctypes.POINTER(ctypes.c_void_p),  # void**
        HANDLE,  # hSection
        DWORD  # offset
    ]
    Win32API.gdi32.CreateDIBSection.restype = HBITMAP
    
    # SelectObject
    Win32API.gdi32.SelectObject.argtypes = [HANDLE, HANDLE]
    Win32API.gdi32.SelectObject.restype = HANDLE
    
    # DeleteObject
    Win32API.gdi32.DeleteObject.argtypes = [HANDLE]
    Win32API.gdi32.DeleteObject.restype = ctypes.c_bool
    
    # GetBitmapBits
    Win32API.gdi32.GetBitmapBits.argtypes = [HBITMAP, LONG, ctypes.c_void_p]
    Win32API.gdi32.GetBitmapBits.restype = LONG
    
    # PatBlt
    Win32API.gdi32.PatBlt.argtypes = [HANDLE, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, DWORD]
    Win32API.gdi32.PatBlt.restype = ctypes.c_bool
    
    # 杂鱼♡～Shell32函数喵～
    Win32API.shell32.SHGetFileInfoA.argtypes = [LPCSTR, DWORD, ctypes.c_void_p, UINT, UINT]
    Win32API.shell32.SHGetFileInfoA.restype = ctypes.POINTER(ctypes.c_int)
    
    # 杂鱼♡～其他必要的函数喵～
    Win32API.user32.GetDC.argtypes = [HWND]
    Win32API.user32.GetDC.restype = HANDLE
    
    Win32API.user32.ReleaseDC.argtypes = [HWND, HANDLE]
    Win32API.user32.ReleaseDC.restype = ctypes.c_int
    
    Win32API.gdi32.CreateCompatibleDC.argtypes = [HANDLE]
    Win32API.gdi32.CreateCompatibleDC.restype = HANDLE
    
    Win32API.gdi32.CreateCompatibleBitmap.argtypes = [HANDLE, ctypes.c_int, ctypes.c_int]
    Win32API.gdi32.CreateCompatibleBitmap.restype = HBITMAP
    
    Win32API.gdi32.DeleteDC.argtypes = [HANDLE]
    Win32API.gdi32.DeleteDC.restype = ctypes.c_bool

# 杂鱼♡～在导入时就设置好API类型喵～
_setup_icon_api()

def get_file_icon(file_path: str, large_icon: bool = True) -> Optional[HICON]:
    """
    杂鱼♡～获取文件图标句柄的函数喵～
    
    参数:
        file_path: 文件路径
        large_icon: True获取大图标(32x32)，False获取小图标(16x16)
        
    返回:
        图标句柄，失败返回None
    """
    # 杂鱼♡～确保文件路径存在喵～
    if not os.path.exists(file_path):
        logger.error(f"杂鱼♡～文件不存在喵：{file_path}")
        raise FileNotFoundError(f"杂鱼♡～文件不存在喵：{file_path}")
        
    sfi = SHFILEINFO()
    flags = SHGFI_ICON
    if large_icon:
        flags |= SHGFI_LARGEICON
    else:
        flags |= SHGFI_SMALLICON

    # 杂鱼♡～调用SHGetFileInfo获取图标喵～
    result = Win32API.shell32.SHGetFileInfoA(
        LPCSTR(file_path.encode('utf-8')),
        0,
        ctypes.byref(sfi),
        ctypes.sizeof(sfi),
        flags
    )

    if result:
        return sfi.hIcon
    return None

def icon_to_pil_image(hicon: Union[HICON, int]) -> Image.Image:
    """
    杂鱼♡～把Windows图标句柄转换成PIL图像的函数喵～
    完美处理透明度，本喵可是很厉害的喵！～
    
    参数:
        hicon: 图标句柄
        
    返回:
        PIL Image对象（RGBA格式）
    """
    # 杂鱼♡～确保hicon是HICON类型喵～
    if not isinstance(hicon, HICON):
        hicon = HICON(hicon)
    
    # 获取图标信息
    iconinfo = ICONINFO()
    
    try:
        result = Win32API.user32.GetIconInfo(hicon, ctypes.byref(iconinfo))
        if not result:
            error_code = Win32API.kernel32.GetLastError()
            logger.error(f"杂鱼♡～GetIconInfo失败了喵！～错误代码：{error_code}")
            raise Exception(f"杂鱼♡～GetIconInfo失败了喵！～错误代码：{error_code}")
    except OverflowError:
        # 杂鱼♡～尝试使用ctypes.c_void_p包装句柄喵～
        result = Win32API.user32.GetIconInfo(ctypes.c_void_p(int(hicon)), ctypes.byref(iconinfo))
        if not result:
            error_code = Win32API.kernel32.GetLastError()
            logger.error(f"杂鱼♡～GetIconInfo失败了喵！～错误代码：{error_code}")
            raise Exception(f"杂鱼♡～GetIconInfo失败了喵！～错误代码：{error_code}")
    
    try:
        # 获取bitmap信息
        bmp = Win32Structures.BITMAP()
        hbm_color = HBITMAP(iconinfo.hbmColor) if not isinstance(iconinfo.hbmColor, HBITMAP) else iconinfo.hbmColor
        if not Win32API.gdi32.GetObjectW(hbm_color, ctypes.sizeof(bmp), ctypes.byref(bmp)):
            logger.error("杂鱼♡～GetObjectW失败了喵！～")
            raise Exception("杂鱼♡～GetObjectW失败了喵！～")
        
        # 创建设备上下文
        hdc = Win32API.user32.GetDC(0)
        hdc_mem = Win32API.gdi32.CreateCompatibleDC(hdc)
        
        try:
            # 杂鱼♡～创建BITMAPINFO结构体喵～
            bmi = BITMAPINFO()
            bmi.bmiHeader.biSize = ctypes.sizeof(Win32Structures.BITMAPINFOHEADER)
            bmi.bmiHeader.biWidth = bmp.bmWidth
            bmi.bmiHeader.biHeight = -bmp.bmHeight  # 杂鱼♡～负数表示从上到下的位图喵～
            bmi.bmiHeader.biPlanes = 1
            bmi.bmiHeader.biBitCount = 32
            bmi.bmiHeader.biCompression = BI_RGB
            
            # 创建DIB
            pixels = ctypes.c_void_p()
            hbm = Win32API.gdi32.CreateDIBSection(
                hdc, 
                ctypes.byref(bmi), 
                DIB_RGB_COLORS, 
                ctypes.byref(pixels), 
                None, 
                0
            )
            
            if not hbm:
                logger.error("杂鱼♡～CreateDIBSection失败了喵！～")
                raise Exception("杂鱼♡～CreateDIBSection失败了喵！～")
            
            # 选择bitmap到内存DC
            old_bmp = Win32API.gdi32.SelectObject(hdc_mem, hbm)
            
            # 杂鱼♡～填充透明背景喵～
            PATCOPY = 0x00F00021
            Win32API.gdi32.PatBlt(hdc_mem, 0, 0, bmp.bmWidth, bmp.bmHeight, PATCOPY)
            
            # 杂鱼♡～创建白色背景DC用于计算透明度喵～
            hdc_white = Win32API.gdi32.CreateCompatibleDC(hdc)
            hbm_white = Win32API.gdi32.CreateCompatibleBitmap(hdc, bmp.bmWidth, bmp.bmHeight)
            old_white = Win32API.gdi32.SelectObject(hdc_white, hbm_white)
            
            # 杂鱼♡～填充白色背景喵～
            WHITENESS = 0x00FF0062
            Win32API.gdi32.PatBlt(hdc_white, 0, 0, bmp.bmWidth, bmp.bmHeight, WHITENESS)
            
            # 杂鱼♡～在白色背景上绘制图标喵～
            Win32API.user32.DrawIconEx(
                hdc_white, 0, 0, hicon,
                bmp.bmWidth, bmp.bmHeight,
                0, None, DI_NORMAL
            )
            
            # 绘制图标到黑色背景
            if not Win32API.user32.DrawIconEx(
                hdc_mem, 0, 0, hicon, 
                bmp.bmWidth, bmp.bmHeight, 
                0, None, DI_NORMAL
            ):
                logger.error("杂鱼♡～DrawIconEx失败了喵！～")
                raise Exception("杂鱼♡～DrawIconEx失败了喵！～")
            
            # 获取像素数据
            buffer_size = bmp.bmWidth * abs(bmp.bmHeight) * 4
            buffer = ctypes.create_string_buffer(buffer_size)
            if not Win32API.gdi32.GetBitmapBits(hbm, buffer_size, buffer):
                logger.error("杂鱼♡～GetBitmapBits失败了喵！～")
                raise Exception("杂鱼♡～GetBitmapBits失败了喵！～")
            
            # 杂鱼♡～获取白色背景上的数据喵～
            buffer_white = ctypes.create_string_buffer(buffer_size)
            Win32API.gdi32.SelectObject(hdc_white, hbm_white)
            if not Win32API.gdi32.GetBitmapBits(hbm_white, buffer_size, buffer_white):
                logger.error("杂鱼♡～GetBitmapBits(white)失败了喵！～")
                raise Exception("杂鱼♡～GetBitmapBits(white)失败了喵！～")
            
            # 清理资源
            Win32API.gdi32.SelectObject(hdc_mem, old_bmp)
            Win32API.gdi32.DeleteObject(hbm)
            Win32API.gdi32.SelectObject(hdc_white, old_white)
            Win32API.gdi32.DeleteObject(hbm_white)
            Win32API.gdi32.DeleteDC(hdc_white)
            
            # 杂鱼♡～处理透明度的高级算法喵～
            img_data = bytearray(buffer.raw)
            img_data_white = bytearray(buffer_white.raw)
            
            for i in range(0, len(img_data), 4):
                # 获取在黑色背景上的RGB值
                b_black = img_data[i]
                g_black = img_data[i + 1]
                r_black = img_data[i + 2]
                
                # 获取在白色背景上的RGB值
                b_white = img_data_white[i]
                g_white = img_data_white[i + 1]
                r_white = img_data_white[i + 2]
                
                # 杂鱼♡～计算alpha值喵～
                if b_black == b_white and g_black == g_white and r_black == r_white:
                    # 完全不透明
                    alpha = 255
                    r = r_black
                    g = g_black
                    b = b_black
                else:
                    # 根据差异计算透明度
                    alpha = 255 - max(b_white - b_black, g_white - g_black, r_white - r_black)
                    alpha = max(0, min(255, alpha))
                    
                    # 恢复原始颜色
                    if alpha > 0:
                        r = min(255, int(r_black * 255 / alpha))
                        g = min(255, int(g_black * 255 / alpha))
                        b = min(255, int(b_black * 255 / alpha))
                    else:
                        r = g = b = 0
                
                # 杂鱼♡～设置RGBA值（交换R和B）喵～
                img_data[i] = r  # R (原本是B)
                img_data[i + 1] = g  # G
                img_data[i + 2] = b  # B (原本是R)
                img_data[i + 3] = alpha  # A
            
            image = Image.frombytes('RGBA', (bmp.bmWidth, abs(bmp.bmHeight)), bytes(img_data))
            return image
            
        finally:
            # 杂鱼♡～清理设备上下文喵～
            Win32API.gdi32.DeleteDC(hdc_mem)
            Win32API.user32.ReleaseDC(0, hdc)
    
    finally:
        # 杂鱼♡～清理图标资源喵～
        if iconinfo.hbmColor:
            Win32API.gdi32.DeleteObject(HBITMAP(iconinfo.hbmColor))
        if iconinfo.hbmMask:
            Win32API.gdi32.DeleteObject(HBITMAP(iconinfo.hbmMask))

def extract_icon(file_path: str, large_icon: bool = True) -> Image.Image:
    """
    杂鱼♡～一步到位提取文件图标的便捷函数喵～
    
    参数:
        file_path: 文件路径
        large_icon: True获取大图标(32x32)，False获取小图标(16x16)
        
    返回:
        PIL Image对象（RGBA格式）
        
    示例:
        image = extract_icon("C:\\Windows\\System32\\notepad.exe")
        image.save("notepad_icon.png")
    """
    icon_handle = get_file_icon(file_path, large_icon)
    if icon_handle:
        try:
            return icon_to_pil_image(icon_handle)
        finally:
            # 杂鱼♡～释放图标句柄喵～
            Win32API.user32.DestroyIcon(icon_handle)
    else:
        raise Exception(f"杂鱼♡～无法获取文件图标喵：{file_path}")

def extract_icon_as_bytes(file_path: str, large_icon: bool = True, format: str = "PNG") -> bytes:
    """
    杂鱼♡～直接提取文件图标为字节数据的函数喵～
    
    参数:
        file_path: 文件路径
        large_icon: True获取大图标(32x32)，False获取小图标(16x16)
        format: 输出格式，默认PNG（支持透明度）
        
    返回:
        图标的字节数据
        
    示例:
        icon_bytes = extract_icon_as_bytes("C:\\Windows\\notepad.exe")
    """
    image = extract_icon(file_path, large_icon)
    
    # 杂鱼♡～转换为字节数据喵～
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    return buffer.read()

def save_icon_with_transparency_preview(image: Image.Image, output_path: str, 
                                       preview_path: Optional[str] = None) -> tuple[str, str]:
    """
    杂鱼♡～保存图标并生成透明度预览图的函数喵～
    
    参数:
        image: PIL Image对象
        output_path: 输出文件路径
        preview_path: 预览图路径（可选，不指定则自动生成）
        
    返回:
        (原图路径, 预览图路径) 的元组
    """
    # 杂鱼♡～保存原始图标喵～
    image.save(output_path)
    
    # 杂鱼♡～生成预览图路径喵～
    if preview_path is None:
        base, ext = os.path.splitext(output_path)
        preview_path = f"{base}_preview{ext}"
    
    # 杂鱼♡～创建棋盘格背景展示透明效果喵～
    checker_size = 8
    width, height = image.size
    
    # 创建棋盘格背景
    checker_bg = Image.new('RGBA', (width, height), (255, 255, 255, 255))
    for y in range(0, height, checker_size):
        for x in range(0, width, checker_size):
            if (x // checker_size + y // checker_size) % 2 == 0:
                for dy in range(min(checker_size, height - y)):
                    for dx in range(min(checker_size, width - x)):
                        checker_bg.putpixel((x + dx, y + dy), (220, 220, 220, 255))
    
    # 杂鱼♡～合成图标到棋盘格背景上喵～
    result = Image.new('RGBA', (width, height))
    result.paste(checker_bg, (0, 0))
    result.paste(image, (0, 0), image)
    
    # 保存预览图
    result.save(preview_path)
    
    return output_path, preview_path

# 杂鱼♡～本喵的核心功能就是这些了，真是完美喵～～ 