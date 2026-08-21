# 阴阳师视觉自动化脚本

通过 TCP ADB 控制 Android 模拟器或手机，并使用 OpenCV 模板匹配识别游戏按钮。

> 仅建议用于减少个人账号的重复操作。使用自动化工具可能违反游戏服务条款，请自行评估账号风险。

## 环境要求

- Windows 10/11
- Python 3.10 或更高版本
- 支持 TCP ADB 的模拟器或 Android 设备
- 推荐使用 16:9 横屏分辨率；模板基准为 `1920 × 1080`，运行时会自动适配

项目默认连接 MuMu 模拟器的 `127.0.0.1:16384`。实际端口以 MuMu 多开器中显示的 ADB 端口为准。

## 安装

建议在虚拟环境中安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 使用

### 图形界面

双击 `launcher.pyw`，或在虚拟环境中运行：

```powershell
python main.py --gui
```

界面支持设备检测和截图预览、任务参数设置、启动、暂停、继续、停止及实时日志。

### 命令行

运行默认的活动任务：

```powershell
python main.py
```

指定任务和模拟器端口：

```powershell
python main.py --task mitama --port 16416
```

查看所有参数：

```powershell
python main.py --help
```

可用任务：

| 参数 | 功能 |
|---|---|
| `active` | 月伴生活动 |
| `mitama` | 御魂副本（悲鸣单人/组队） |
| `hero-exp` | 英杰经验副本 |
| `spirit` | 御灵副本 |
| `fire` | 业原火 |

常用选项：

- `--host`：ADB 地址，默认 `127.0.0.1`
- `--port`：ADB 端口，默认 `16384`
- `--threshold`：模板匹配阈值，默认 `0.8`
- `--interval`：每轮识别间隔，默认 `1` 秒
- `--gui`：显示独立日志窗口
- `--debug`：输出模板匹配度等调试信息

按 `Ctrl+C` 可安全停止任务并断开 ADB。

## 项目结构

```text
main.py                 命令行入口
schedule.py             多设备、多任务调度辅助类
runner/
  base.py               任务进程和识图点击流程
  simple.py             游戏任务定义
  connector/            ADB 连接、截屏、点击和滑动
  player/               OpenCV 模板识别
  gui/                  可选日志窗口
wanted/                 1920×1080 环境下截取的目标模板
tests/                   离线单元测试
```

每轮任务只获取一次设备截图，然后按任务定义的顺序查找目标；识别到第一个目标并点击后进入下一轮，避免对已经变化的界面继续使用旧截图。

模板以 `1920×1080` 为基准。识别器会根据当前截图自动缩放模板，例如 MuMu 的 `1600×900` 横屏模式无需单独制作一套素材。

## 测试

测试不需要启动模拟器：

```powershell
python -m unittest discover -s tests -v
```

## 打包

安装打包依赖后使用仓库中的配置生成单文件程序；配置会自动包含 `wanted/` 模板资源：

```powershell
python -m pip install -r requirements-dev.txt
pyinstaller main.spec
```

生成的 `dist/main.exe` 默认启动图形界面。

## 增加任务

在 `runner/simple.py` 中继承 `FindListRunner`，按优先级填写模板文件名：

```python
class Example(FindListRunner):
    name = "example"
    description = "示例任务"
    targets = ("confirm.jpg", "begin.jpg", "continue.jpg")
```

然后将任务类加入 `main.py` 的 `TASKS` 即可。

## 致谢

项目思路参考了 [anywhere2go/auto_player](https://github.com/anywhere2go/auto_player)。项目采用 MIT License。
