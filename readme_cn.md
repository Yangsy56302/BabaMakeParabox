# Baba Make Parabox

![游戏图标](BabaMakeParabox.png)

**Baba Make Parabox**是一个二创同人推箱子元游戏，作者是**Yangsy56302**。
取材游戏为[**Baba Is You**](https://hempuli.com/baba/)与[**Patrick's Parabox**](https://www.patricksparabox.com/)，
作者分别为**Arvi Hempuli**和**Patrick Traynor**。

## 如何运行

注意：`python`文件夹中的批处理文件只会在Python代码文件存在时工作，
而`windows`文件夹中的批处理文件只会在EXE可执行程序文件存在时工作。

**不要关闭或点击终端窗口**
**除非你需要在终端里面输入数据**
**或者你确实知道你要干什么。**

如果你想运行源代码，下载这些软件：
- **Python** *（最新版）*：[链接](https://www.python.org/downloads/)
- **PIP**：应该会与Python一起安装
- **Pygame**：在终端或类似终端的地方运行`pip install -U pygame`
- **PyInstaller** *（可选，仅制作EXE用）*：类似上面，运行`pip install -U pyinstaller`

运行`test.bat`以开始该游戏的官方测试。

运行`input.bat`以从`levelpacks`文件夹内读取关卡包的JSON文件来开始游戏。

运行`edit.bat`以编辑`levelpacks`文件夹内的关卡包文件并在原地保存，若无文件则会新建一份。

可以运行`help.bat`以获取更多关于如何在终端运行该游戏的说明。

如果你需要打包EXE文件，运行`py_2_exe.bat`。

### 如何控制

- WSAD：移动
- Space：等待
- Z：撤回
- R：重新开始关卡包
- Esc：保存所在关卡的状态并返回上一级
- \- / =：选择摄像机所在的世界

### 如何胜利

请记住：

1. 有时规则能改变；
2. 有时有些规则改不了；
3. 有时你得钻进房间里；
4. 有时你需要创造一个悖论。

## 如何制作存档

**注意：放置的世界，克隆和关卡指向摄像头所在的房间。**
**若有将某个房间放在其他房间内的需要，请考虑剪切、复制和粘贴。**

### 如何控制

- WSAD：移动光标
- IKJL：选择物体朝向
- Q / E：选择物体
- Tab：切换物体和名词
- Enter (Return)：在光标上放置物体
- Backspace：删除光标上的物体
- \- / =：选择摄像机所在的世界
- \[ / \]：选择摄像机所在的关卡
- P：新世界，需要在终端输入信息
- O：删除世界，需要在终端确认
- M：新关卡，需要在终端输入信息
- N：删除关卡，需要在终端确认
- R：改变全局规则，需要在终端输入信息
- Z：撤回
- X：剪切光标上的物体至剪切板
- C：复制光标上的物体至剪切板
- V：从剪切板粘贴物体到光标上
- 关闭游戏窗口：保存并退出
- 关闭终端：不保存只退出

## 杂项

### 关于 options.json

位于游戏根目录下的`options.json`是本游戏的设置文件。
如果您知道什么是`JSON`，您可以试着更改里面的默认设置。
例如，`fps`理论上代表游戏帧率，而`fpw`理论上代表贴图抖动帧数。

## 版本列表（版本详细信息暂不翻译）

| 版本号 |    时间    | 版本详细信息 |
|--------|------------|--------------|
| 1.0    | 2024.07.05 | Initialized. |
| 1.1    | 2024.07.06 | Keke is Move; Game is Undo and Restart; Baba make Levels |
| 1.11   | 2024.07.06 | Level is Previous and Next |
| 1.2    | 2024.07.06 | Flag is Win; Game is EXE |
| 1.3    | 2024.07.06 | Baba is Keke; World is Input and Output |
| 1.31   | 2024.07.07 | Terminal is More; Text is not Hide; Level is Red |
| 1.4    | 2024.07.07 | Baba make Worlds |
| 1.41   | 2024.07.07 | Level is Best and Swap |
| 1.42   | 2024.07.08 | Code is Better |
| 1.5    | 2024.07.08 | Baba is Float; Me is Sink; Rock is Defeat |
| 1.6    | 2024.07.08 | Door is Shut; Key is Open |
| 1.7    | 2024.07.09 | All has Color; Lava is Hot; Ice is Melt |
| 1.8    | 2024.07.10 | Game has Icon; Baba is Word; Keke is Shift; Rock is Tele |
| 1.81   | 2024.07.10 | Argv is Better |
| 1.9    | 2024.07.10 | All is Wobble; Code is Better |
| 1.91   | 2024.07.10 | Lava is Orange; Pos is Best |
| 2.0    | 2024.07.11 | Level is not World; Cursor is Select |
| 2.1    | 2024.07.11 | Bug is Fix; World is Level |
| 2.11   | 2024.07.12 | Undo and Restart is Fix |
| 2.12   | 2024.07.12 | Object is More |
| 2.13   | 2024.07.12 | Esc is Out |
| 2.2    | 2024.07.12 | World feeling Push and Options is Better |
| 2.21   | 2024.07.12 | Bug is Fix; Patrick is You |
| 2.22   | 2024.07.12 | Changes is Small |

## 报告漏洞和提出建议

发送邮件到**yangsy56302@163.com**！
另外，你也可以联系我的QQ：**2485385799**，这样更方便一些，毕竟中国国内没几个人用邮箱。

## 支持作者

外网暂时不开放。
对于内网，可以尝试在微信添加我的好友并转账给我。
微信号：**yangsy56302**。