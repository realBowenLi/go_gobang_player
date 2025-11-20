# 棋类对战平台

一个支持五子棋和围棋的对战平台，支持人机对战和本地双人对战。

## 安装与运行

### 环境要求
- Python 3.7+
- tkinter（Python标准库，通常已包含）

### 运行方式

#### GUI模式

**方式：运行GUI主程序**
```bash
cd go_gobang_player
python main_gui.py
```

#### 控制台模式
**方式：运行主程序**
```bash
cd go_gobang_player
python main.py
```

## 快速开始示例

1. **开始五子棋双人对战**
   ```
   start gobang 15 human
   ```

2. **开始围棋人机对战（执黑）**
   ```
   start go 19 ai black
   ```

3. **落子**
   ```
   place 7 7
   ```

4. **保存游戏**
   ```
   save my_game.json
   ```

5. **加载游戏**
   ```
   load my_game.json
   ```

## GUI界面使用说明

### 界面功能

1. **菜单栏**
   - 游戏菜单：新游戏、重新开始、保存、加载、退出
   - 帮助菜单：关于

2. **游戏信息面板**
   - 显示游戏类型、棋盘大小
   - 显示当前玩家和游戏状态

3. **棋盘区域**
   - 点击棋盘交叉点落子
   - 自动绘制棋子和网格线
   - 支持棋盘缩放
   - 19路和15路棋盘显示星位

4. **控制按钮**
   - 新游戏：打开新游戏设置对话框
   - 悔棋：撤销上一步
   - 认负：投子认负
   - 虚着：围棋虚着（仅围棋）
   - 保存：保存当前游戏
   - 加载：加载已保存的游戏


## 核心功能实现

### 1. 游戏类型
- ✅ 五子棋
- ✅ 围棋

### 2. 对战模式
- ✅ 本地双人对战
- ✅ 人机对战（超级AI）

### 3. 超级AI特性
- ✅ 超级AI并不是传统意义上的 AI
- ✅ 它只会基于简单规则胡乱落子
- ✅ 优先选择与玩家上一手相邻的位置
- ✅ 否则随机落子

### 4. 游戏功能
- ✅ 开始游戏（含参数配置）
- ✅ 落子
- ✅ 虚着（围棋）
- ✅ 悔棋（一次撤销双方各一步）
- ✅ 投子认负
- ✅ 保存 / 加载游戏
- ✅ 重新开始

### 5. 围棋规则
- ✅ 提子
- ✅ 打劫检测（简化）
- ✅ 自杀检测
- ✅ 虚着支持
- ✅ 胜负判断（数子法简化版）

### 6. 五子棋规则
- ✅ 连五判断
- ✅ 平局判断（棋盘填满）

## 项目结构

```
go_gobang_player/
├── main.py                 # 程序入口
├── config.py              # 配置管理
├── exceptions.py          # 自定义异常
│
├── core/                  # 核心业务逻辑
│   ├── game.py           # Game抽象类
│   ├── gobang_game.py    # 五子棋
│   ├── go_game.py        # 围棋
│   ├── board.py          # Board抽象类
│   ├── gobang_board.py
│   ├── go_board.py
│   ├── player.py
│   ├── human_player.py
│   ├── ai_player.py
│   ├── stone.py
│   ├── position.py
│   └── game_factory.py
│
├── command/               # 命令模式
│   ├── command.py
│   └── commands.py
│
├── persistence/           # 持久化
│   ├── serializer.py
│   └── file_manager.py
│
├── ui/                    # 界面层
│   ├── builder.py
│   ├── components.py
│   └── console_ui.py
│
└── controller/            # 控制层
    ├── game_controller.py
    └── command_parser.py
```

## 设计模式

本项目使用了以下设计模式：

1. **策略模式**：游戏类型（五子棋/围棋）作为策略
2. **工厂模式**：GameFactory创建游戏实例
3. **命令模式**：用户命令封装为命令对象
4. **建造者模式**：UIBuilder构建界面
5. **模板方法模式**：Game基类定义游戏流程模板
6. **备忘录模式**：游戏历史记录支持悔棋与存档读档


