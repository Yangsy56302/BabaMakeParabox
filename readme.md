# Baba Make Parabox

![游戏图标](bmp.bmp)

**Baba Make Parabox**（简称 **BMP**）是一个二创同人推箱子元游戏，作者是**Yangsy56302**。
该游戏取材自游戏[**Baba Is You**](https://hempuli.com/baba/)与[**Patrick's Parabox**](https://www.patricksparabox.com/)，
作者分别为**Arvi Hempuli**和**Patrick Traynor**。

**本游戏的源代码使用[MIT许可证](https://opensource.org/license/MIT/)。**
_……大概吧。_

**本游戏使用[Pygame](https://www.pygame.org/news/)作为游戏引擎，而Pygame使用[GNU宽通用公共许可证 2.1版](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html)。**
因此，本人不提供Pygame的源代码，而是提供使用未经修改的Pygame版本经[PyInstaller](https://pyinstaller.org/en/stable/index.html)打包后形成的游戏程序。
**PyInstaller使用[GNU通用公共许可证 第2版](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html)。**

**我并未拥有游戏纹理的所有权。**
如果您有关于游戏纹理的使用权等权利的更多信息，请尽快联系我。

该游戏的雏形诞生于2024.05.15，游戏文件夹创建时间为北京时间12:12:15。

## 新手指南

### 下载

请跳转到[Gitlab](https://gitlab.com/Yangsy56302/BabaMakeParabox)，
点击页面右上方写着**Code**的蓝色按钮，在展开的下拉菜单里找到**zip**，点击即可下载。
该流程下载的压缩包（`BabaMakeParabox-main.zip`）内含有**可执行程序（bmp.exe）**，**源代码（BabaMakeParabox文件夹）**，
**Baba Make Parabox 添加的新纹理（sprites_new）**， **Baba Is You 的部分音效（sounds）** 等内容。

备用下载地址包括连接不稳定的[Github](https://github.com/Yangsy56302/BabaMakeParabox)
以及需要注册账号才能下载的[Gitee](https://gitee.com/Yangsy56302/BabaMakeParabox)，此处不推荐。

### 安装

+ **推荐方式**
    1. 在您准备安装的位置（如`C:\Program Files`）新建文件夹；
    2. 将压缩包`BabaMakeParabox-main.zip`内的文件和文件夹解压到上一步新建的文件夹内；
    3. 在上一步解压的文件中找到`baba-is-you-original-sprites.zip`，解压到与上一步相同的文件夹内；
    4. 找到文件夹`sprites_old`并将其重命名为`sprites`；
    5. 把文件夹`sprites_new`里面的所有图片放到重命名后的`sprites`文件夹里面。
+ **备用方式**
    1. 完成**推荐方式**的所有步骤；
    2. 通过以下任意一种方式安装**Python**：
        + 官方安装方式
            1. 进入[Python的官方网站](https://www.python.org)；
            2. 找到位于Logo右下方的**Downloads**，悬停展开；
            3. 在展开后的部分找到**Download for Windows**下方的按钮，点击以下载；
            4. 打开下载完成的安装程序，勾选最下方的**Add python.exe to PATH**，然后点击醒目的**Install Now**以安装Python；
            5. 等待安装完成，然后重启电脑。
        + _（待补）_
    3. 运行`inst-win.bat`，等待一段时间（大概在三分钟以内），直到文件夹内出现`bmp.exe`和`submp.exe`。

### 运行

双击运行`play-win.bat`，这将会间接运行`bmp.exe`，然后启动程序。
直接运行`bmp.exe`也是可行的，但程序故障后会直接关闭终端窗口，所以不推荐。
如果您的**Windows**系统安装了**Python**，还可以尝试运行`run-win.bat`来启动游戏。

同时确保您已经准备关卡包文件……或者[准备制作一个新的关卡包了](#编辑器)。

**游戏仅在命令行窗口存在且未选中内部文本时正常运行。**
这是Windows命令提示符的预期行为和游戏的简陋交互设计导致的现象，而并非游戏Bug。
游戏未响应时，请先在命令行内 **取消选中文字** ，
确保游戏 **并未询问输入** ，
然后耐心 **等待十秒左右** 直至游戏继续运行。
如果游戏仍然处于未响应状态，则该现象可以确认是一个需要汇报的游戏漏洞。

## 游戏内容

### 控制

+ **`W` / `S` / `A` / `D`**：移动
+ **`SPACE`**：等待
+ **`ESC`**：回到上层关卡
+ **`Z`**：撤销
+ **`CTRL` + `R`**：重新开始关卡包
+ **`O`**：载入临时存档
    + **`CTRL` + `...`**：可指定此临时存档的名字
+ **`P`**：保存临时存档
    + **`CTRL` + `...`**：可指定此临时存档的名字
+ **`TAB`**：显示各种信息
+ **`F1`**: 显示FPS
+ **鼠标左键**：进入世界
+ **鼠标右键**：回到上层世界
+ **鼠标滚轮**：循环选择世界
+ **关闭游戏窗口**：停止游玩，指定文件名以保存
+ **关闭终端**：强制退出程序

## 编辑器

该章节暂时不提供有关游戏设计的相关信息。

### 控制

+ **鼠标左键**：放置物体
    + **`SHIFT` + `...`**：即使该位置存在物体也额外放置
    + **`CTRL` + `...`**：设置部分物体的额外信息
    + **`ALT` + `...`**：进入世界
        + **`SHIFT` + `...`**：进入关卡
+ **鼠标右键**：删除物体
    + **`ALT` + `...`**：回到上层世界
        + **`SHIFT` + `...`**：回到上层关卡
+ **鼠标滚轮**：循环选择物体类型
    + **`SHIFT` + 鼠标滚轮向上滚动**：选择该物体的名词
    + **`SHIFT` + 鼠标滚轮向下滚动**：选择该名词指向的物体
    + **`ALT` + `...`**：循环选择世界
        + **`SHIFT` + `...`**：循环选择关卡
+ **(`W` / `S` / `A` / `D`) / 方向键**：选择物体朝向
+ **`0` ~ `9`**：从调色板选择物体类型
    + **`SHIFT` + `...`**：设置调色板的物体类型
+ **`N`**：新建世界
    + **`ALT` + `...`**：新建关卡
+ **`M`**：删除世界
    + **`ALT` + `...`**：删除关卡
+ **`R`**：设置全局规则
    + **`SHIFT` + `...`**：删除全局规则
+ **`T`**：设置所处世界的标识符
    + **`ALT` + `...`**：设置所处关卡的标识符
+ **`CTRL` + (`X` / `C` / `V`)**：剪切 / 复制 / 粘贴 光标上的物体
+ **`F1`**: 显示FPS
+ **关闭游戏窗口**：退出编辑器，指定文件名以保存
+ **关闭终端**：强制退出程序

**注意：带有 \* 的键位提示代表按下该键之后需要在终端内输入更多信息。**
这段时间内，游戏窗口会被冻结，因为程序正在等待您的输入。

**放置的世界、克隆和关卡默认指向摄像头所在的世界和关卡。**

## 一段有关特殊物体的极其详细且复杂甚至可能会忘了更新的描述

+ **文本** *（TEXT）* ：组成自定义游戏规则的物体。
    + 文本物体默认拥有`PUSH`属性。
    + 根据用法的不同，可以进行分类：
        + 名词：指代一类物体。
            + 诸如`BABA`，`FLAG`，`TEXT`等都是名词。
                + 注意区分所有文本和`TEXT`：所有文本都是`TEXT`名词的指代对象。
            + 部分特殊名词可以指定更详细的物体。
            + 如果开启元文本选项，则可以出现元文本——指向特定文本的名词，如指向`BABA`的`TEXT_BABA`。
                + 元文本也属于文本，所以可以出现`TEXT_TEXT_TEXT_BABA`这样的多层套娃元文本。
        + 介词：指代操作类型。
            + 截至3.2，只有四种：`IS`，`HAS`，`MAKE`，和`WRITE`。
        + 属性词：指代一类物体属性。
            + 诸如`YOU`，`WIN`，`WORD`等都是属性词。
            + 当名词作为属性词使用时，会将被赋予名词属性的物体，转换为用于属性词的名词所指代的物体。
        + 修饰词：指代限定条件类型。
            + 前缀修饰词：`SELDOM`，`OFTEN`和`META`。
            + 中缀修饰词：`ON`，`NEAR`，`NEXTTO`，`WITHOUT`和`FEELING`。
        + 元文本修饰词：`TEXT_`。
            + 尽管`TEXT_`的作用方式类似于前缀修饰词，然而数据层面上`TEXT_`并不属于修饰词。
                + `TEXT_`在源代码内的类名为`TextText_`，其直接继承自`Text`类（文本）而非`Prefix`类（前缀修饰词）。
                + `TEXT_`暂时无法修饰其他`TEXT_`。
        + 并列词：`AND`。
        + 否定词：`NOT`。
    + 初步检测时允许的语法：
        + 并列泛名词 介词 并列泛属性词
            + 并列泛名词 := 并列泛名词 并列词 泛名词 *或者* 泛名词
                + 泛名词 := 并列泛前缀修饰词 泛名词 泛中缀修饰词 *或者* 基础泛名词
                    + 泛中缀修饰词 := 基础泛中缀修饰词 并列泛属性词
                        + 并列泛属性词 := 并列泛属性词 并列词 泛属性词 *或者* 泛属性词
                            + 泛属性词 := 否定词 泛属性词 *或者* 属性词 *或者* 元名词
                                + 元名词 := 元文本修饰词 元名词 *或者* 名词
                        + 基础泛中缀修饰词 := 否定词 基础泛中缀修饰词 *或者* 中缀修饰词
                    + 并列泛前缀修饰词 := 并列泛前缀修饰词 并列词 基础泛前缀修饰词 *或者* 基础泛前缀修饰词
                        + 基础泛前缀修饰词 := 否定词 基础泛前缀修饰词 *或者* 前缀修饰词
                    + 基础泛名词 := 否定词 基础泛名词 *或者* 元名词
    + 若将其他类型的物体转换为文本物体，则该物体会转换为对应的名词物体。
+ **世界** *（WORLD）* ：可以指一个容纳物体的长方形空间，也可以指一个间接包含前者的特殊物体。约定称前者为**世界**，称后者为**世界物体**。
    + 世界物体默认拥有`PUSH`属性。
    + 若外世界内有一个内世界物体，则可以尝试通过把具有`PUSH`属性的物体推出边缘而将其从内世界推出到外世界。
        + 若前提不成立，则失败。
        + 若物体被空间物体阻挡，则尝试根据相对位置转移物体。
            + 若物体被阻挡，则失败。
            + 若物体试图推动自己，则失败。
            + 若物体或转移世界的`ENTER`属性被禁用，则失败。
        + 若物体被其他物体阻挡，则失败。
        + 若过程中多次经过同一世界，则：
            1. 在关卡内寻找名称相同，无限等级大一的世界，作为无限大世界。
                + 若世界未找到，则失败。
            2. 在关卡内寻找包含无限大世界物体的世界。
                + 若世界物体未找到，则失败。
            3. 尝试将物体从无限大世界推出。
                + 若物体被阻挡，则失败。
                + 若物体试图推动自己，则失败。
                + 若物体或无限大世界的`LEAVE`属性被禁用，则失败。
        + 若物体或世界的`LEAVE`属性被禁用，则失败。
    + 若外世界内有一个内空间物体受到推力，则其优先按顺序选择以下一项：
        1. 尝试通过推动前面的物体从而允许自身被推动。
            + 若前方物体无法被推动，则失败。
        2. 将在推力方向距离内空间物体最近的具有`PUSH`属性但无法被推动的物体从外世界挤入到内世界。
            + 若物体被阻挡，则失败。
            + 若物体试图推动自己，则失败。
            + 若物体或世界的`ENTER`属性被禁用，则失败。
        3. 将对内空间物体施加推力的物体从外世界推入到内世界。
            + 若物体被阻挡，则失败。
            + 若物体试图推动自己，则失败。
            + 若过程中多次经过同一世界，则：
                1. 在关卡内寻找名称相同，无限等级小一的世界，作为无限小世界。
                    + 若世界未找到，则失败。
                2. 尝试将物体推入无限小世界。
                    + 若物体试图推动自己，则失败。
                    + 若物体或无限小世界的`ENTER`属性被禁用，则失败。
            + 若物体或世界的`ENTER`属性被禁用，则失败。
        4. 拒绝移动。
    + 可以有多个指向同一个世界的世界物体。
        + 尽管 Patrick's Parabox 里的盒子只能有一个对应的本体，但本游戏抛弃了该设定。
        + 当物体从被多个世界物体对应的世界推出时，所有世界物体都会创建一个该物体的副本。
            + 此机制可以用来快捷地复制物体。
    + 关于规则：
        + 部分属性词会同时作用在整个世界范围内。
        + 关于转换：
            + 若将世界物体转换为其他类型的物体，则：
                + 克隆物体：转换为指向相同世界的克隆物体。
                + 关卡物体：转换为以指向的世界为主世界，包含所在关卡内所有世界的关卡物体。
                + 其他物体：转换为该物体，保留世界相关信息。
            + 若将其他类型的物体转换为世界物体，则：
                + 克隆物体：转换为指向相同世界的世界物体。
                + 关卡物体：转换为以主世界为所指向的世界，包含该关卡内所有世界的世界物体。
                + 其他物体：
                    1. 转换为以该物体可能包含的世界相关信息为所指向的世界的世界物体。
                    2. 若无相关信息，则转换为包含该物体的 3 \* 3 世界。
+ **克隆** *（CLONE）* ：类似于世界物体，但有些许不同，约定称为**克隆物体**。
    + 克隆物体默认禁用`LEAVE`属性。
        + 这会导致将物体从世界内推出时忽略克隆物体。
    + 其他特性与关卡物体一致。
+ **关卡** *（LEVEL）* ：可以指包含多个世界的存在，也可以指被包含在世界内的指向前者的特殊物体。约定称前者为**关卡**，称后者为**关卡物体**。
    + 关卡物体默认包含属性`STOP`。
    + 关于规则：
        + 部分属性词会同时作用在整个关卡范围内。
        + 关于转换：
            + 除了上述情况外，若将关卡物体转换为其他类型的物体，则转换为该物体，保留关卡相关信息。
            + 除了上述情况外，若将其他类型的物体转换为关卡物体，则：
                1. 转换为以该物体可能包含的关卡相关信息为所指向的关卡的关卡物体。
                2. 若无相关信息，则转换为包含将该物体转换为世界时产生的世界的关卡。
+ **游戏** *（GAME）*：指代游戏本身。
    + 关于规则：
        + 可以使用大部分属性词，且部分有独特的效果。
        + 无法附加修饰词。
        + 关于转换：
            + 若将游戏物体转换为其他类型的物体，则将该物体贴图覆盖游戏界面。
            + 若将其他类型的物体转换为游戏物体，则删除该物体，同时新建子进程显示该物体的默认贴图。

## 杂项

### 计划实现

+ **短期**
    + 普通物体转变为新的世界时默认指向其所在的世界。
    + `GROUP`的逻辑。
+ **中期**
    + 物体试图到达不存在的世界时会被删除。
    + GUI（图形用户界面）。
        + 使用可输入文本的游戏窗口取代命令行的显示。
+ **长期**
    + `GAME`的复杂语法。
        + 目前对`GAME`应用修饰词会使其不指代任何物体。
    + `Infinite Loop`与其检测方法。

### 异常情况分类

#### 游戏特性

+ 属性前带有多个`NOT`的规则只会否定一条恰好缺少一个`NOT`的规则。
    + 例如，`BABA IS NOT YOU`否定一条`BABA IS YOU`；`BABA IS NOT NOT YOU`否定一条`BABA IS NOT YOU`，可能导致已有的`BABA IS YOU`不再被那条`BABA IS NOT YOU`否定。
+ `FEELING`每轮只检测一次，以试图避免检测停机问题和判定无限循环。
+ `TEXT IS WORD`有效，导致非元文本被识别为`TEXT`。
    + 通常，这会导致该规则同时被识别成`TEXT IS TEXT`。

#### 游戏漏洞

+ 移动系统的完成度很低，有时表现会与 Baba Is You 不同，主要出现在多个物体同时移动的情况下。

### 关于 options.json

位于游戏根目录下的`options.json`是本游戏的设置文件。
如果您知道什么是`JSON`，您可以试着更改里面的默认设置。
例如，`fps`理论上代表游戏帧率，而`fpw`代表贴图抖动帧数。

## [更新日志](changelog.md)

见<changelog.md>（标题也是链接）。

## 联系作者

哔哩哔哩：**<https://space.bilibili.com/430612354>**

QQ：**2485385799**

163邮箱：**<yangsy56302@163.com>**