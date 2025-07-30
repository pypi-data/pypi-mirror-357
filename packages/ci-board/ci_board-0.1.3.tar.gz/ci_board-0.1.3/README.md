# CI-Board - 杂鱼主人也能用的高性能剪贴板监控库

![CI/CD](https://github.com/Xuehua-Meaw/ci_board/actions/workflows/ci_board_CICD.yml/badge.svg)

> 杂鱼♡～这可是本喵为杂鱼主人精心重构的 Windows 剪贴板监控库 v0.1.3 喵～

## 🎯 项目概览

**CI-Board** (Clipboard Intelligence Board) 是一个为 Windows 设计的高性能、模块化的 Python 剪贴板监控库。它不仅能实时捕获文本、图片、文件等多种剪贴板内容，还能智能追踪内容的来源应用程序。经过本喵的精心重构，现在的架构更加清晰、健壮和类型安全了，哼～是不是很厉害喵！～

### ✨ 核心特性
- 🐱 **懒人API** - 只需一行代码就能添加处理器，本喵都帮你弄好了喵～
- 🧱 **模块化设计** - 核心监控器现在是指挥官，把具体工作都交给了专业的组件，各司其职，清爽干净！
- 🔄 **实时监控** - 基于 Windows 原生消息的事件驱动模式，高效又灵敏！
- 🎯 **智能源追踪** - 能准确识别是哪个程序（比如 `Arc.exe` 或 `explorer.exe`）复制了内容喵。
- 📋 **多格式支持** - 原生支持文本、图片和文件列表，杂鱼主人不用再自己解析了。
- ⚡ **真·异步处理** - 使用独立的线程池处理回调，避免阻塞主线程，就算杂鱼主人写出很慢的代码也不会卡住喵！
- 🛡️ **高级去重** - 内置智能哈希算法，能有效过滤因多步骤操作（如截图、编辑、复制）产生的重复内容。
- 🔌 **高扩展性** - 处理器和过滤器都可以自定义，想怎么玩都行，哼～
- 📝 **详细日志** - 内置彩色日志系统，方便杂鱼主人调试时查看内部状态。
- 🔒 **类型安全** - 大量使用 `dataclasses` 和 `Generics`，让代码更健壮，杂鱼主人不容易犯错喵！

### 📊 项目信息
- **版本**: v0.1.3
- **Python版本**: >=3.8
- **平台**: Windows
- **依赖**: 纯Python，无强制第三方依赖
- **许可证**: MIT

## 🚀 快速开始

### 安装
```bash
# 杂鱼♡～推荐使用本喵最喜欢的 uv 包管理器喵～
uv add ci-board

# 或者用你那慢吞吞的 pip
pip install ci-board
```
> **可选依赖**: 如果要处理图片，本喵建议你安装 `Pillow` 库喵～ `uv add pillow` 或 `pip install Pillow`

### 懒人API - 30秒上手
哼～看好了，杂鱼主人！这就是本喵设计的懒人API，让你这种懒蛋也能轻松上手喵～

```python
# 杂鱼♡～这是最简单的使用方式喵～
import time
from ci_board import create_monitor, ProcessInfo, BMPData
# 杂鱼♡～为了看清本喵的工作过程，可以打开日志喵～
from ci_board.utils.logger import setup_ci_board_logging, LogLevel
setup_ci_board_logging(console_level=LogLevel.INFO)

def on_text_change(text: str, source: ProcessInfo):
    print(f"杂鱼♡～本喵抓到了新的文本喵！是从 [{source.process_name}] 来的！")
    print(f"  内容: {text[:80]}...")

def on_image_change(image: BMPData, source: ProcessInfo):
    print(f"杂鱼♡～抓到一张图片！尺寸 {image.width}x{image.height}，来自 [{source.process_name}] 喵！")
    # 杂鱼♡～想看图的话，记得先安装 Pillow 喵～
    try:
        import io
        from PIL import Image
        img = Image.open(io.BytesIO(image.data))
        img.show()
    except ImportError:
        print("  （杂鱼主人快去安装 Pillow 才能看图喵！）")
    except Exception as e:
        print(f"  （哎呀，图片出错了喵：{e}）")

def on_files_change(files: list[str], source: ProcessInfo):
    print(f"杂鱼♡～有文件被复制了喵！一共 {len(files)} 个，来自 [{source.process_name}]！")
    for f in files:
        print(f"  - {f}")

# 哼～创建监控器，就是这么简单喵～
monitor = create_monitor()

# 杂鱼♡～看好了，本喵的懒人API可以直接把函数变成处理器喵！
monitor.add_handler('text', on_text_change)
monitor.add_handler('image', on_image_change)
monitor.add_handler('files', on_files_change)

print("杂鱼♡～监控开始了喵！快去复制点东西给本喵看看！(按 Ctrl+C 结束)")
monitor.start()

try:
    monitor.wait()
except KeyboardInterrupt:
    print("\n哼～杂鱼主人不玩了，那本喵就结束了喵～")
finally:
    monitor.stop()
```

## 📋 API 文档 (概览)

### `create_monitor()`
这是最简单的创建监控器的方法，它会返回一个配置好默认参数的、随时可以工作的 `ClipboardMonitor` 实例。

```python
def create_monitor(
    async_processing: bool = True,
    max_workers: int = 4,
    handler_timeout: float = 30.0,
    enable_source_tracking: bool = True,
):
```

### `monitor.add_handler()`
懒人专用API，直接把你的回调函数注册到监控器上。

```python
monitor.add_handler(
    content_type: Literal["text", "image", "files"], 
    handler: Union[BaseClipboardHandler, Callable]
)
```

### 核心数据结构
哼～这些是回调函数会收到的数据结构，给本喵看仔细了！

```python
# 来源进程信息，本喵查到的可详细了喵！
@dataclass
class ProcessInfo:
    process_name: str       # 进程名, 像 'vscode.exe'
    process_path: str       # 完整路径
    process_id: int         # 进程ID
    window_title: str       # 窗口标题
    detection_method: str   # 本喵是用什么方法抓到它的
    confidence_level: str   # 本喵对结果的自信程度，哼～
    is_system_process: bool # 是不是系统进程
    is_screenshot_tool: bool # 是不是截图工具，本喵可聪明了
    timestamp: float        # 发现它的时间戳

# BMP图片数据，才...才不是为了杂鱼优化的代码♡～
@dataclass
class BMPData:
    success: bool           # 转换是否成功
    data: bytes | None      # BMP 格式的图片数据
    width: int              # 图片宽度
    height: int             # 图片高度
    bit_count: int          # 位深度

# 新增的文件信息，哼～
@dataclass
class FileInfo:
    path: str
    name: str
    size: str               # 格式化后的大小
    # ... 还有更多信息 ...

# 设备无关位图，给ImageHandler的原始材料喵
@dataclass
class DIBData:
    width: int
    height: int
    data: bytes
    # ...
```

## 🛡️ 架构设计

重构后的架构围绕一个作为"指挥官"的 `ClipboardMonitor` 展开，它协调了一系列各司其职的组件：
- **`MessagePumpWrapper`**: 封装了 Windows 消息循环，是事件驱动的核心。
- **`ClipboardReader`**: 负责所有底层的剪贴板读取操作。
- **`SourceTracker`**: 负责焦点追踪和剪贴板所有者分析，以确定内容来源。
- **`Deduplicator`**: 负责计算内容哈希，防止重复事件。
- **`AsyncExecutor`**: 管理一个线程池，用于异步执行用户的回调函数。
- **`Handlers`**: `TextHandler`, `ImageHandler` 等，负责处理特定类型的数据。

这种设计使得代码更加清晰、可维护和可扩展，哼～这才配得上本喵的智慧！

## 📁 项目结构
```
ci_board/
├── core/                   # 核心模块，本喵的心脏！
│   ├── monitor.py          # 指挥官：主监控器
│   ├── source_tracker_.py  # 侦察兵：源追踪器
│   ├── executor.py         # 工人领袖：异步执行器
│   └── (其他包装器...)
├── handlers/               # 工人：各种处理器
├── interfaces/             # 蓝图：接口定义
├── types/                  # 语言：数据类型
└── utils/                  # 工具箱：底层工具
    ├── win32_api.py        # Windows API 封装
    └── logger.py           # 日志工具
```

## 📝 开发信息

- **作者**: Xuehua-Meaw & Neko
- **GitHub**: [ci_board](https://github.com/Xuehua-Meaw/ci_board)
- **许可证**: MIT License

## 💝 致谢

哼～感谢所有使用本喵作品的杂鱼主人们喵～
如果觉得好用...就...就给本喵一个 Star 吧！才...才不是因为想要才跟你要的！只是看你可怜而已！♡～
