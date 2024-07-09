# Baba Make Parabox

![游戏图标](BabaMakeParabox.png)

**Baba Make Parabox**是一个二创同人推箱子元游戏，作者是**Yangsy56302**。
取材游戏为[**Baba Is You**](https://hempuli.com/baba/)与[**Patrick's Parabox**](https://www.patricksparabox.com/)，
作者分别为**Arvi Hempuli**和**Patrick Traynor**。

## 如何运行

注意：带有`py`前缀的批处理文件只会运行Python代码文件，
而带有`exe`前缀的批处理文件只会运行EXE可执行程序。

如果你想运行源代码，下载这些软件：
- **Python** **_(最新版)_**：[链接](https://www.python.org/downloads/)
- **PIP**：应该会与Python一起安装
- **Pygame**：在终端或类似终端的地方运行`pip install -U pygame`
- **PyInstaller** **_(可选，仅制作EXE用)_**：类似上面，运行`pip install -U pyinstaller`

运行`前缀_test.bat`以开始该游戏的官方测试。

运行`前缀_input.bat`以从`worlds`文件夹内读取存档的JSON文件来开始游戏。

运行`前缀_edit.bat`以编辑`worlds`文件夹内的存档文件并在原地保存，若无文件则会新建一份。

可以运行`前缀_help.bat`以获取更多关于如何在终端运行该游戏的说明。

如果你需要打包EXE文件，运行`py_2_exe.bat`。

### 如何控制

- WSAD：移动
- Space：等待
- Z：撤回，最多100次
- R：重新开始
- 减号 / 等于号：选择摄像机所在的房间

### 如何胜利

只需要把标记为**你** **_(you)_**的物体移到标记为**赢** **_(you)_**的物体上。

记住：

1. 有时规则能改变；
2. 有时有些规则改不了；
3. 有时你得钻进房间里；
4. 有时你需要创造一个悖论。

## 如何制作存档

**注意：放置的房间和克隆房间指向摄像头所在的房间。**
**若有将某个房间放在其他房间内的需要，请考虑剪切粘贴。**

### 如何控制

- WSAD：移动光标
- IKJL：选择物体朝向
- Q / E：选择物体
- 缩进：切换物体和名词
- 回车：在光标上放置物体
- 退格：删除光标上的物体
- 减号 / 等于号：选择房间（关卡）
- P：新房间（关卡），需要在终端输入信息
- O：删除房间（关卡），需要在终端确认
- R：改变全局规则，需要在终端输入信息
- Z：撤回，最多100次
- X：剪切光标上的物体至剪切板
- C：复制光标上的物体至剪切板
- V：从剪切板粘贴光标上的物体
- 关闭窗口：保存并退出

## 版本列表（版本详细信息暂不翻译）

注意：制作完成时间可能不准确，具体以Git记录为准。

| 版本号 |    时间    | 版本详细信息 |
|--------|------------|--------------|
| 1.0    | 2024.07.05 | Initialized. |
| 1.1    | 2024.07.06 | Keke is Move; Undo and Restart; Baba make Levels |
| 1.11   | 2024.07.06 | Level is Previous and Next |
| 1.2    | 2024.07.06 | Flag is Win; Game is EXE |
| 1.3    | 2024.07.06 | Baba is Keke; World is Input and Output |
| 1.31   | 2024.07.07 | Terminal is More; Text is not Hide; Level is Red |
| 1.4    | 2024.07.07 | Baba make Worlds |
| 1.41   | 2024.07.07 | Level is Best and Swap |
| 1.42   | 2024.07.08 | Code is Better |
| 1.5    | 2024.07.08 | Baba is Float; Me is Sink; Rock is Defeat |
| 1.6    | 2024.07.08 | Door is Shut; Key is Open |

## 报告漏洞和提出建议

发送邮件到yangsy56302@163.com！
另外，你也可以联系我的QQ：2485385799，这样更方便一些，毕竟中国国内没几个人用邮箱。

## 支持作者

暂时不开放。