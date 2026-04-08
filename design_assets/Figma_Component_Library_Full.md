# ReliHub Figma 组件库完整设计

**版本**: 2.0  
**最后更新**: 2026年4月5日  
**设计师**: ReliHub 设计团队  
**状态**: 🚀 **准备在 Figma 中实现**

---

## 📋 目录

1. [颜色与排版系统](#颜色与排版系统)
2. [基础组件库](#基础组件库) (48 个)
3. [表单组件库](#表单组件库) (24 个)
4. [导航组件库](#导航组件库) (18 个)
5. [卡片与容器](#卡片与容器) (16 个)
6. [反馈与提示](#反馈与提示) (18 个)
7. [高级组件库](#高级组件库) (12 个)
8. [使用指南](#使用指南)

---

## 🎨 颜色与排版系统

### 颜色系统 (23 色)

```
主色系:
  Primary Blue:        #007AFF
  Primary Hover:       #0051D5
  Primary Active:      #004399
  Primary Disabled:    #D1D1D1

中性色:
  Text Dark:           #000000
  Text Medium:         #333333
  Text Light:          #666666
  Text Lighter:        #999999
  Text Lightest:       #CCCCCC
  Background:          #FFFFFF
  Background Light:    #F2F2F7
  Border:              #E0E0E0
  Border Light:        #F0F0F0

功能色:
  Success:             #34C759
  Success Light:       #D1F4DD
  Warning:             #FF9500
  Warning Light:       #FFF3E0
  Error:               #FF3B30
  Error Light:         #FFE8E6
  Info:                #00C7BE
  Info Light:          #E0F7F5
  Secondary:           #5856D6
  Secondary Light:     #F0EEFF
```

### 排版系统 (11 个)

```
Display:             48px / 800 / 1.0   (标题大标题)
Heading 1:           32px / 700 / 1.2   (页面标题)
Heading 2:           28px / 600 / 1.3   (模块标题)
Heading 3:           24px / 600 / 1.4   (小标题)
Subtitle:            18px / 600 / 1.5   (副标题)
Body Large:          16px / 400 / 1.5   (正文大)
Body Regular:        14px / 400 / 1.6   (正文常规)
Body Small:          12px / 400 / 1.6   (正文小)
Caption:             11px / 400 / 1.5   (说明文字)
Label Large:         14px / 600 / 1.5   (标签大)
Label Regular:       12px / 600 / 1.5   (标签常规)
```

### 间距系统 (8 级)

```
xs:   4px
sm:   8px
md:  12px
lg:  16px
xl:  24px
2xl: 32px
3xl: 48px
4xl: 64px
```

### 圆角系统 (5 级)

```
none:   0px
sm:     4px
md:     8px
lg:    12px
full:  24px (或 50%)
```

### 阴影系统 (4 级)

```
none:    无
sm:      0 1px 2px rgba(0,0,0,0.05)
md:      0 4px 6px rgba(0,0,0,0.1)
lg:      0 10px 15px rgba(0,0,0,0.1)
```

---

## 🧩 基础组件库 (48 个)

### 1. 按钮 (Button) - 12 个变体

#### 1.1 主按钮 (Primary Button)

**尺寸**: Large / Medium / Small  
**状态**: Default / Hover / Active / Disabled / Loading

```
属性定义:
  Large:
    Padding:       16px 24px
    Font Size:     16px
    Height:        48px
    Border Radius: 8px
    
  Medium (常用):
    Padding:       12px 20px
    Font Size:     14px
    Height:        40px
    Border Radius: 8px
    
  Small:
    Padding:       8px 16px
    Font Size:     12px
    Height:        32px
    Border Radius: 6px

状态样式:
  Default:
    Background:    #007AFF (Primary Blue)
    Text:          #FFFFFF
    Border:        none
    
  Hover:
    Background:    #0051D5 (Primary Hover)
    Text:          #FFFFFF
    Shadow:        sm
    
  Active:
    Background:    #004399 (Primary Active)
    Text:          #FFFFFF
    Shadow:        none
    
  Disabled:
    Background:    #D1D1D1
    Text:          #999999
    Cursor:        not-allowed
    
  Loading:
    Background:    #0051D5
    Spinner:       显示加载动画
    Text:          隐藏或显示"加载中..."
```

**代码示例**:
```jsx
<Button variant="primary" size="medium" state="default">
  确认
</Button>
```

---

#### 1.2 次按钮 (Secondary Button)

```
属性定义:
  Border:         2px solid #007AFF
  Background:     transparent
  Text:           #007AFF
  Padding:        (同 Primary Button)
  
状态样式:
  Default:
    Border:       2px solid #007AFF
    Text:         #007AFF
    Background:   transparent
    
  Hover:
    Border:       2px solid #0051D5
    Text:         #0051D5
    Background:   #F0F7FF
    
  Active:
    Border:       2px solid #004399
    Text:         #004399
    Background:   transparent
    
  Disabled:
    Border:       2px solid #D1D1D1
    Text:         #999999
    Background:   transparent
```

---

#### 1.3 文字按钮 (Text Button)

```
属性定义:
  Background:     transparent
  Text:           #007AFF
  Border:         none
  Padding:        (同 Primary Button)
  
状态样式:
  Default:
    Text:         #007AFF
    
  Hover:
    Text:         #0051D5
    Background:   #F0F7FF
    
  Active:
    Text:         #004399
    
  Disabled:
    Text:         #999999
    Cursor:        not-allowed
```

---

#### 1.4 危险按钮 (Danger Button)

```
属性定义:
  Background:     #FF3B30 (Error Red)
  Text:           #FFFFFF
  Border:         none
  
状态样式:
  Default:
    Background:   #FF3B30
    
  Hover:
    Background:   #E63B2E
    Shadow:       sm
    
  Active:
    Background:   #CC3126
    
  Disabled:
    Background:   #D1D1D1
    Text:         #999999
```

---

#### 1.5 幽灵按钮 (Ghost Button)

```
属性定义:
  Background:     #F2F2F7
  Text:           #000000
  Border:         none
  
状态样式:
  Default:
    Background:   #F2F2F7
    
  Hover:
    Background:   #E0E0E0
    
  Active:
    Background:   #D1D1D1
    
  Disabled:
    Background:   #F2F2F7
    Text:         #999999
```

---

### 2. 输入框 (Text Input) - 8 个变体

#### 2.1 标准输入框

```
属性定义:
  Width:              fill_container (最大)
  Height:             40px (Medium)
  Padding:            12px 16px
  Font Size:          14px
  Border:             1px solid #E0E0E0
  Border Radius:      8px
  Background:         #FFFFFF
  
状态样式:
  Default:
    Border:           1px solid #E0E0E0
    Background:       #FFFFFF
    Text Color:       #000000
    
  Focus:
    Border:           2px solid #007AFF
    Background:       #FFFFFF
    Shadow:           0 0 0 3px rgba(0,122,255,0.1)
    
  Filled:
    Border:           1px solid #E0E0E0
    Background:       #FFFFFF
    Text Color:       #000000
    
  Disabled:
    Border:           1px solid #E0E0E0
    Background:       #F2F2F7
    Text Color:       #999999
    Cursor:           not-allowed
    
  Error:
    Border:           1px solid #FF3B30
    Background:       #FFFFFF
    Text Color:       #000000
    Helper Text:      显示红色错误信息
    
  Success:
    Border:           1px solid #34C759
    Background:       #FFFFFF
    Text Color:       #000000
```

**组件变体**:
- Single Line (单行) - 常用
- Multiline (多行) - 显示 3+ 行高度
- With Icon (带图标) - 左/右图标位置
- With Label (带标签) - 上方标签
- With Helper Text (带帮助文本) - 下方说明文字
- With Counter (带字符计数) - 显示当前/最大字数

---

#### 2.2 搜索输入框

```
属性定义:
  与标准输入框相同，但:
  Left Icon:         搜索图标 (16px)
  Right Icon:        清除按钮 (16px, 仅当有内容时显示)
  Placeholder:       "搜索..."
  Background:        #F2F2F7
```

---

### 3. 复选框 (Checkbox) - 4 个状态

```
属性定义:
  Size:               20px × 20px
  Border:             2px solid #E0E0E0
  Border Radius:      4px
  Background:         #FFFFFF
  
状态样式:
  Unchecked:
    Border:           2px solid #E0E0E0
    Background:       #FFFFFF
    
  Unchecked Hover:
    Border:           2px solid #007AFF
    Background:       #FFFFFF
    
  Checked:
    Border:           2px solid #007AFF
    Background:       #007AFF
    Checkmark:        白色 ✓ 图标 (12px)
    
  Checked Hover:
    Border:           2px solid #0051D5
    Background:       #0051D5
    
  Indeterminate (三态):
    Border:           2px solid #007AFF
    Background:       #007AFF
    Symbol:           白色 − 符号 (12px)
    
  Disabled:
    Border:           2px solid #D1D1D1
    Background:       #F2F2F7
    Cursor:           not-allowed
    
  Disabled Checked:
    Border:           2px solid #D1D1D1
    Background:       #D1D1D1
    Checkmark:        #999999
    Cursor:           not-allowed

组件变体:
  - Checkbox with Label (带标签)
  - Checkbox Group (复选框组)
```

---

### 4. 单选框 (Radio) - 4 个状态

```
属性定义:
  Size:               20px × 20px (外圆)
  Border:             2px solid #E0E0E0
  Inner Circle:       8px × 8px (选中时)
  
状态样式:
  Unchecked:
    Border:           2px solid #E0E0E0
    Background:       #FFFFFF
    
  Unchecked Hover:
    Border:           2px solid #007AFF
    Background:       #FFFFFF
    
  Checked:
    Border:           2px solid #007AFF
    Background:       #FFFFFF
    Inner Circle:     8px #007AFF
    
  Checked Hover:
    Border:           2px solid #0051D5
    Inner Circle:     8px #0051D5
    
  Disabled:
    Border:           2px solid #D1D1D1
    Background:       #F2F2F7
    Cursor:           not-allowed
    
  Disabled Checked:
    Border:           2px solid #D1D1D1
    Inner Circle:     8px #999999
    Cursor:           not-allowed

组件变体:
  - Radio with Label
  - Radio Group
```

---

### 5. 开关 (Toggle/Switch) - 3 个状态

```
属性定义:
  Width:              52px
  Height:             32px
  Border Radius:      16px (pill shape)
  Knob Size:          28px × 28px
  
状态样式:
  Off (关闭):
    Background:       #E0E0E0
    Knob Color:       #FFFFFF
    Knob Position:    2px from left
    
  Off Hover:
    Background:       #D1D1D1
    
  On (打开):
    Background:       #007AFF
    Knob Color:       #FFFFFF
    Knob Position:    22px from left (right position)
    
  On Hover:
    Background:       #0051D5
    
  Disabled Off:
    Background:       #F2F2F7
    Knob Color:       #D1D1D1
    Cursor:           not-allowed
    
  Disabled On:
    Background:       #D1E8FF
    Knob Color:       #D1D1D1
    Cursor:           not-allowed

动画:
  Transition:         200ms ease-in-out
  Property:           background-color, knob position
```

---

### 6. 标签 (Label/Badge) - 6 个变体

#### 6.1 默认标签

```
属性定义:
  Padding:            4px 12px
  Font Size:          12px
  Font Weight:        600
  Border Radius:      4px
  
变体:
  Primary:
    Background:      #007AFF
    Text:            #FFFFFF
    
  Secondary:
    Background:      #F0EEFF
    Text:            #5856D6
    
  Success:
    Background:      #D1F4DD
    Text:            #34C759
    
  Warning:
    Background:      #FFF3E0
    Text:            #FF9500
    
  Error:
    Background:      #FFE8E6
    Text:            #FF3B30
    
  Info:
    Background:      #E0F7F5
    Text:            #00C7BE
    
  Outline:
    Background:      transparent
    Border:          1px solid #E0E0E0
    Text:            #666666
```

---

### 7. 徽章 (Badge) - 数字徽章

```
属性定义:
  Size:               24px × 24px
  Border Radius:      50% (圆形)
  Font Size:          12px (数字 1-99)
  Font Weight:        600
  Background:         #FF3B30 (默认红色)
  Text:               #FFFFFF
  
变体:
  Dot Badge (点徽章):
    Size:             8px × 8px
    
  Number Badge (数字徽章):
    Size:             24px × 24px
    显示数字 1-99
    
  Overflow Badge (溢出徽章):
    显示 "99+"
    
位置:
  通常定位在右上角
  Offset: -4px top, -4px right (相对于父元素)
```

---

### 8. 进度条 (Progress Bar) - 3 个类型

#### 8.1 线性进度条

```
属性定义:
  Height:             4px
  Width:              fill_container
  Border Radius:      2px
  Background:         #E0E0E0
  Progress Bar:       #007AFF
  
状态样式:
  0%:                 宽度 0%
  50%:                宽度 50%
  100%:               宽度 100%
  
带标签的进度条:
  显示百分比文本 (14px, 600 weight)
  位置: 右侧或中心
  示例: "50%"
```

#### 8.2 圆形进度条

```
属性定义:
  Size:               120px × 120px (可配置)
  Stroke Width:       8px
  Background:         #E0E0E0
  Progress:           #007AFF
  
显示:
  中心文本: 显示百分比 (32px, 600 weight)
```

#### 8.3 步骤进度条

```
属性定义:
  Steps:              最多 5-7 步
  每步:               40px × 40px (或自适应)
  连接线:             宽度 2px, 颜色 #E0E0E0
  
状态:
  Completed:
    背景:             #007AFF
    数字/勾号:        #FFFFFF
    线:               #007AFF
    
  Current:
    背景:             #F0F7FF
    数字:             #007AFF
    线:               #E0E0E0
    
  Pending:
    背景:             #F2F2F7
    数字:             #666666
    线:               #E0E0E0
```

---

### 9. 分页器 (Pagination)

```
属性定义:
  按钮尺寸:          40px × 40px
  Font Size:         14px
  
按钮状态:
  Disabled (上一页/下一页):
    Background:      #F2F2F7
    Text:            #999999
    Cursor:          not-allowed
    
  Active:
    Background:      #007AFF
    Text:            #FFFFFF
    
  Hover:
    Background:      #0051D5
    Text:            #FFFFFF
    
  Normal:
    Background:      #FFFFFF
    Border:          1px solid #E0E0E0
    Text:            #000000

组件:
  [< 上一页] [1] [2] [3] ...[100] [下一页 >]
  
可选项目:
  - 显示 "共 100 页" 信息
  - 显示 "第 X 页" 信息
```

---

### 10. 标签页 (Tabs) - 2 种样式

#### 10.1 顶部标签页

```
属性定义:
  高度:               48px
  标签间距:           0px (完全填充)
  下划线:             3px
  
标签状态:
  Inactive:
    Background:      transparent
    Text:            #666666
    Underline:       transparent
    
  Hover:
    Background:      #F2F2F7
    Text:            #000000
    
  Active:
    Background:      transparent
    Text:            #007AFF
    Underline:       3px #007AFF
    
示例:
  [标签 1] [标签 2] [标签 3]
  └─────────────────────── (下划线在活跃标签下方)
```

#### 10.2 卡片标签页

```
属性定义:
  标签样式:          如小卡片
  间距:               8px
  Border Radius:     8px
  
标签状态:
  Inactive:
    Background:      #F2F2F7
    Text:            #666666
    
  Hover:
    Background:      #E0E0E0
    Text:            #000000
    
  Active:
    Background:      #007AFF
    Text:            #FFFFFF
```

---

### 11. 分割线 (Divider) - 2 种

#### 11.1 水平分割线

```
属性定义:
  高度:               1px
  宽度:               fill_container
  颜色:               #E0E0E0
  
变体:
  带文字:             在中间显示标签文字
  带间距:             上下各 16px margin
```

#### 11.2 垂直分割线

```
属性定义:
  宽度:               1px
  高度:               fill_container
  颜色:               #E0E0E0
```

---

### 12. 头像 (Avatar) - 4 种尺寸

```
属性定义:
  尺寸:               24px / 40px / 56px / 72px
  Border Radius:      50% (圆形)
  Border:             2px solid #FFFFFF (可选)
  
状态:
  Default (图片):
    显示用户头像图片
    
  Initials (首字母):
    显示用户名首字母
    Background:      #007AFF
    Text:            #FFFFFF (白色首字母)
    
  Placeholder (占位符):
    显示默认头像图标
    Background:      #E0E0E0
    Icon:            #999999
    
组件变体:
  - Avatar Group (头像组合, 重叠显示)
  - Avatar with Badge (带徽章)
  - Avatar with Status (带在线状态指示)
```

---

## 📋 表单组件库 (24 个)

### 1. 下拉菜单 (Dropdown Select) - 6 个变体

#### 1.1 标准下拉菜单

```
属性定义:
  高度:               40px
  宽度:               fill_container (最大)
  Padding:            12px 16px
  Border:             1px solid #E0E0E0
  Border Radius:      8px
  Font Size:          14px
  
组件:
  左侧: 选中项文本
  右侧: 下拉箭头 (16px)
  
状态:
  Default:
    Background:      #FFFFFF
    Text:            #000000
    Icon:            #666666
    
  Focus:
    Border:          2px solid #007AFF
    Shadow:          0 0 0 3px rgba(0,122,255,0.1)
    
  Open (打开):
    Border Radius:   8px 8px 0 0 (上方)
    下拉菜单显示
    
  Disabled:
    Background:      #F2F2F7
    Text:            #999999
    Cursor:          not-allowed

下拉菜单项:
  - 高度: 36px
  - Padding: 8px 16px
  - 状态: Normal / Hover / Active / Disabled
  - Hover: 背景 #F2F2F7
  - Active: 背景 #E8F3FF, 文字 #007AFF
  - 可包含: 图标 (左) + 文字 + 快捷键 (右)
```

---

#### 1.2 多选下拉菜单

```
与标准下拉菜单相同，但:
  - 可同时选中多个选项
  - 显示选中项数: "已选择 X 项"
  - 可显示所有选中项标签 (如有空间)
  - 右侧按钮可清除所有选择
```

---

#### 1.3 可搜索下拉菜单

```
与标准下拉菜单相同，但:
  - 打开时显示搜索输入框 (位于菜单顶部)
  - 实时过滤菜单项
  - 显示过滤结果数: "找到 X 项"
  - 无搜索结果时显示: "没有找到"
```

---

### 2. 数字输入框 (Number Input)

```
属性定义:
  类似文本输入框，但:
  - 输入仅允许数字
  - 右侧有增减按钮
  - 增/减按钮: 各 32px 高度
  
增减按钮:
  上按钮: +
  下按钮: -
  宽度: 32px
  背景: 默认 #F2F2F7, Hover #E0E0E0
  
状态:
  可设置最小/最大值限制
  到达限制时按钮变禁用
```

---

### 3. 日期选择器 (Date Picker)

#### 3.1 输入字段

```
属性定义:
  类似文本输入框
  右侧显示日历图标
  Placeholder: "选择日期"
  格式: YYYY-MM-DD 或 DD/MM/YYYY
```

#### 3.2 弹出日历

```
属性定义:
  宽度: 320px
  显示月历
  
组件:
  - 月/年选择器 (顶部)
  - 上月/下月导航
  - 周天标题行 (一、二、三...)
  - 日期网格 (7列 × 6行)
  - 今天按钮 (底部)
  - 清除按钮 (底部)

日期单元格状态:
  Normal Day:
    Background:    #FFFFFF
    Text:          #000000
    Border:        无
    
  Hover:
    Background:    #F2F2F7
    
  Selected:
    Background:    #007AFF
    Text:          #FFFFFF
    Border Radius: 4px
    
  Today:
    Border:        1px solid #007AFF
    
  Other Month:
    Text:          #999999
    Background:    transparent
    
  Disabled:
    Text:          #CCCCCC
    Background:    #F2F2F7
    Cursor:        not-allowed
```

---

### 4. 时间选择器 (Time Picker)

```
属性定义:
  类似数字输入框
  格式: HH:MM (24小时) 或 HH:MM AM/PM
  
可选显示:
  - 小时滚动选择器
  - 分钟滚动选择器
  - 上午/下午选择
```

---

### 5. 日期时间范围选择器 (Date Range Picker)

```
属性定义:
  两个输入字段:
    - 开始日期
    - 结束日期
  显示两个日历，可同时选择范围
  
快捷选项:
  - 今天
  - 昨天
  - 最近 7 天
  - 最近 30 天
  - 本月
  - 上月
  - 自定义范围
```

---

### 6. 评分器 (Rating)

```
属性定义:
  5 颗星 (可配置 1-10 星)
  每颗星: 24px × 24px
  间距: 4px
  
星星状态:
  Empty (未评):
    颜色:          #E0E0E0
    
  Hover (悬停):
    颜色:          #FFB800 (淡黄)
    
  Selected (已评):
    颜色:          #FF9500 (金黄色)
    
  Disabled:
    颜色:          #CCCCCC
    Cursor:        not-allowed
```

---

### 7. 色选器 (Color Picker)

```
属性定义:
  主区域: 360px × 240px 颜色区域
  饱和度竖条: 24px × 240px
  值竖条: 24px × 240px
  
选定颜色:
  显示选中颜色块 (60px × 60px)
  显示 HEX 值输入框
  显示 RGB 输入框
```

---

### 8. 滑块 (Slider) - 2 种

#### 8.1 单值滑块

```
属性定义:
  高度: 轨道 4px + 滑钮 20px
  宽度: fill_container
  
轨道:
  背景: #E0E0E0
  已填充部分: #007AFF
  
滑钮:
  大小: 20px × 20px
  颜色: #007AFF
  Border Radius: 50%
  阴影: 2px
  
悬停时:
  阴影: md (扩大视觉效果)
  显示数值提示
```

#### 8.2 范围滑块

```
两个滑钮，可选择范围
显示: [最小值] —— [最大值]
```

---

### 9. 切换按钮组 (Button Group Toggle)

```
属性定义:
  多个按钮排列
  只能选中一个 (单选)
  
按钮样式:
  未选中:
    Background:    #F2F2F7
    Text:          #666666
    Border:        1px solid #E0E0E0
    
  选中:
    Background:    #007AFF
    Text:          #FFFFFF
    Border:        1px solid #007AFF
    
  Hover (未选中):
    Background:    #E0E0E0
    Border:        1px solid #D1D1D1
    
示例:
  [日] [周] [月] [年]
```

---

### 10-24. 其他表单组件

- **10. 文件上传器** (File Upload)
  - 拖拽上传区域
  - 上传进度条
  - 已上传文件列表

- **11. 富文本编辑器** (Rich Text Editor)
  - 工具栏 (加粗、斜体、下划线、链接等)
  - 编辑区域
  - 格式化面板

- **12. 地址选择器** (Address Picker)
  - 省/市/区三级级联菜单
  - 详细地址输入框

- **13. 电话号码输入** (Phone Input)
  - 国家代码选择
  - 电话号码输入框
  - 格式自动转换

- **14. 邮箱输入** (Email Input)
  - 邮箱格式验证
  - 建议自动完成

- **15. 密码输入** (Password Input)
  - 显示/隐藏密码按钮
  - 密码强度指示器

- **16. 搜索输入** (Search Input)
  - 搜索图标
  - 清除按钮
  - 搜索建议下拉

- **17-24. 其他表单组件** (Textarea, Combobox, Editor, 等)

---

## 🗂️ 导航组件库 (18 个)

### 1. 导航栏 (Navigation Bar/Header) - 4 种

#### 1.1 顶部导航栏

```
属性定义:
  高度:               64px
  背景:               #FFFFFF
  边框:               1px solid #E0E0E0
  内容: [Logo] [菜单项] [用户菜单/搜索]
  
菜单项:
  Padding:           0 16px
  高度:               64px (垂直居中)
  文字:               14px
  
菜单项状态:
  Normal:
    Text:            #666666
    Background:      transparent
    
  Hover:
    Text:            #007AFF
    Background:      #F2F2F7
    
  Active:
    Text:            #007AFF
    Border Bottom:   3px solid #007AFF
    
示例布局:
  [ReliHub Logo] [首页] [发现] [我的] [设置]     [搜索] [👤]
```

#### 1.2 侧边栏导航

```
属性定义:
  宽度:               240px (Desktop)
  高度:               fill_viewport
  背景:               #FFFFFF
  边框:               1px solid #E0E0E0
  
菜单项:
  高度:               40px
  Padding:            8px 16px
  Font Size:          14px
  Border Radius:      4px
  Margin:             4px 8px
  
菜单项状态:
  Normal:
    Text:            #666666
    Background:      transparent
    Left Icon:       16px (可选)
    
  Hover:
    Text:            #007AFF
    Background:      #F2F7FF
    
  Active:
    Text:            #007AFF
    Background:      #E8F3FF
    Left Border:     3px #007AFF (蓝色左边框)
    
  Icon:
    Size:            20px × 20px
    Margin Right:    12px

子菜单:
  缩进 12px
  折叠/展开箭头
  
示例结构:
  [首页] 🏠
  [社区]
    └─ 热门话题
    └─ 我的话题
  [爱问] 💡
    └─ 浏览问题
    └─ 我的提问
  [资源] 📚
```

#### 1.3 标签页导航

```
在 Tabs 组件部分已定义
```

#### 1.4 面包屑导航 (Breadcrumb)

```
属性定义:
  高度:               32px
  间距:               8px between items
  
项目:
  字体:               12px
  颜色:               #666666
  可点击 (链接色 #007AFF)
  
分隔符:
  颜色:               #999999
  符号:               / 或 >
  
示例:
  首页 / 社区 / 热门话题 / 详情
```

---

### 2. 侧边栏 (Sidebar) - 3 种样式

#### 2.1 可折叠侧边栏

```
与侧边栏导航类似
左上角有折叠按钮
折叠时仅显示图标 (60px 宽)
展开时显示完整菜单 (240px 宽)
动画: 200ms ease-in-out
```

#### 2.2 浮动侧边栏

```
半透明深色背景 (#000000, 50% opacity)
显示在内容上方
包含关闭按钮 (X)
点击外部关闭
动画: 从左侧滑出
```

#### 2.3 标签式侧边栏

```
顶部多个标签选项卡
每个标签对应不同内容
类似侧边栏的标签页版本
```

---

### 3. 菜单 (Menu) - 3 种

#### 3.1 下拉菜单 (Dropdown)

```
与下拉菜单组件类似
包含关闭和嵌套菜单支持
```

#### 3.2 右键菜单 (Context Menu)

```
浮动菜单，出现在光标位置
包含一系列操作项
- 编辑
- 删除
- 分享
- 举报

项目高度: 36px
支持快捷键显示
```

#### 3.3 弹出菜单 (Popup Menu)

```
相对定位弹出
可定位在按钮下方/右侧/上方
关闭选项: 点击项目/外部/ESC
```

---

### 4. 步骤条 (Stepper) - 2 种

#### 4.1 垂直步骤条

```
类似水平步骤条，但竖向排列
- 左侧: 步骤圆形
- 中间: 竖向连接线
- 右侧: 步骤标题和描述

示例:
  ● Step 1 - 账号注册
  │ (连接线)
  ● Step 2 - 邮箱验证
  │
  ○ Step 3 - 信息完善
  │
  ○ Step 4 - 完成
```

#### 4.2 水平步骤条

```
已在基础组件 "步骤进度条" 中定义
```

---

### 5-18. 其他导航组件

- **5. 下拉菜单** - 已定义
- **6. 快捷键条** (Shortcut Bar)
- **7. 分割线** (Divider) - 已定义
- **8. 地图导航** (Map Navigator)
- **9. 顶部栏** (Top Bar/Header) - 已定义
- **10. 抽屉** (Drawer/Sidebar) - 已定义
- **11. 工具提示** (Tooltip) - 在反馈组件定义
- **12. 菜单** - 已定义
- **13. 分页器** - 已定义
- **14. 步进器** - 已定义
- **15. 顶部导航** - 已定义
- **16. 水平菜单** (Horizontal Menu)
- **17. 足页** (Footer)
- **18. 内容导航** (Content Navigator)

---

## 🎴 卡片与容器 (16 个)

### 1. 卡片 (Card) - 5 种

#### 1.1 基础卡片

```
属性定义:
  背景:               #FFFFFF
  边框:               1px solid #E0E0E0
  边框圆角:           8px
  内边距:             16px
  阴影:               sm (0 1px 2px rgba(0,0,0,0.05))
  
布局:
  [标题]
  [描述/内容]
  [操作按钮]
  
状态:
  Default:
    与上面定义相同
    
  Hover:
    阴影:            md (0 4px 6px rgba(0,0,0,0.1))
    光标:            pointer
    
  Focus:
    边框:            2px solid #007AFF
    阴影:            0 0 0 3px rgba(0,122,255,0.1)
```

#### 1.2 图像卡片

```
包含:
  [图像] (320px × 200px)
  [标题] (16px, 600 weight)
  [描述] (14px)
  [操作] 如点赞、评论、分享
  
示例: 博客文章卡片、产品卡片
```

#### 1.3 列表项卡片

```
简化版卡片，高度约 60px
包含:
  [左图标/头像]
  [标题 + 描述]
  [右侧元素]
  
示例: 消息列表项、用户列表项
```

#### 1.4 展开/折叠卡片

```
顶部可点击区域，包含展开/折叠箭头
点击后展开显示详细内容
动画: 高度变化 200ms ease-in-out
```

#### 1.5 悬停卡片

```
鼠标悬停时出现额外操作按钮或信息
效果:
  - 浮起效果 (阴影增大)
  - 显示操作菜单
  - 显示详情按钮
```

---

### 2. 面板 (Panel)

```
属性定义:
  大面板容器
  类似卡片，但通常更大且包含复杂内容
  
特性:
  - 可以包含表格、表单、图表等
  - 通常有标题栏
  - 通常有关闭或最小化按钮
```

---

### 3. 对话框/模态框 (Modal Dialog) - 3 种

#### 3.1 标准对话框

```
属性定义:
  宽度:               最大 600px (响应式)
  背景:               #FFFFFF
  边框圆角:           12px
  阴影:               lg (0 10px 15px rgba(0,0,0,0.1))
  
布局:
  [关闭按钮 X]
  [标题]
  [内容区域]
  [操作按钮] (确认/取消)
  
背景:
  半透明黑色遮罩    #000000, 60% opacity
  点击遮罩关闭
  
动画:
  从中心缩放出现      300ms ease-out
  关闭时缩放消失      200ms ease-in
```

#### 3.2 确认对话框

```
简化版对话框
标题 + 简短消息 + 两个按钮 (确认/取消)
```

#### 3.3 通知对话框

```
标题 + 长文本内容 + 一个确认按钮
```

---

### 4. 提示框 (Alert) - 4 种

#### 4.1 成功提示

```
背景:               #D1F4DD (Success Light)
边框:               1px solid #34C759
文字:               #34C759
图标:               勾号 ✓ (绿色)
Padding:            16px
边框圆角:           8px

示例:
  ✓ 操作成功完成！
```

#### 4.2 警告提示

```
背景:               #FFF3E0
边框:               1px solid #FF9500
文字:               #FF9500
图标:               感叹号 ! (橙色)
```

#### 4.3 错误提示

```
背景:               #FFE8E6
边框:               1px solid #FF3B30
文字:               #FF3B30
图标:               X (红色)
```

#### 4.4 信息提示

```
背景:               #E0F7F5
边框:               1px solid #00C7BE
文字:               #00C7BE
图标:               i (青色)
```

---

### 5. 折叠面板 (Collapse/Accordion)

```
属性定义:
  多个可折叠项
  每项高度: 40px (标题栏)
  
标题栏:
  背景:               #F2F2F7
  Padding:            12px 16px
  Font Size:          14px (600 weight)
  右侧:               箭头图标 (展开/折叠)
  
Hover:
  背景:               #E0E0E0
  Cursor:             pointer
  
展开内容:
  Padding:            16px
  背景:               #FFFFFF
  
示例:
  ▼ 基本信息 (展开)
     [内容]
  ▶ 高级选项 (折叠)
  ▶ 帮助信息 (折叠)
```

---

### 6. 工具提示框 (Popover)

```
属性定义:
  浮动框，相对于触发元素定位
  背景:               #FFFFFF
  边框:               1px solid #E0E0E0
  阴影:               md
  边框圆角:           8px
  Padding:            12px 16px
  
方向:
  可从上/下/左/右弹出
  自动避开屏幕边界
  
关闭:
  点击外部区域或 ESC 键
```

---

### 7-16. 其他容器组件

- **7. 表格** (Table) - 详见数据展示
- **8. 列表** (List) - 详见数据展示
- **9. 网格** (Grid)
- **10. 标签页面板** (Tabbed Panel)
- **11. 窗口** (Window)
- **12. 浮动窗口** (Floating Window)
- **13. 分割窗格** (Split Pane)
- **14. 树形控件** (Tree)
- **15. 日历** (Calendar)
- **16. 时间线** (Timeline)

---

## ⚠️ 反馈与提示 (18 个)

### 1. 吐司通知 (Toast) - 4 种

#### 1.1 成功吐司

```
属性定义:
  位置:               右下角 (或右上角)
  宽度:               360px
  高度:               自适应 (最小 60px)
  背景:               #D1F4DD
  边框:               1px solid #34C759
  边框圆角:           8px
  Padding:            16px
  图标:               ✓ (绿色)
  文本:               #34C759
  
关闭:
  自动关闭 5 秒
  或点击关闭按钮
  
动画:
  从右侧滑入        300ms ease-out
  从右侧滑出        200ms ease-in
  
示例:
  ✓ 保存成功
```

#### 1.2 错误吐司

```
背景:               #FFE8E6
边框:               1px solid #FF3B30
图标:               X (红色)
文本:               #FF3B30
示例:
  ✕ 操作失败，请重试
```

#### 1.3 警告吐司

```
背景:               #FFF3E0
边框:               1px solid #FF9500
图标:               ! (橙色)
文本:               #FF9500
示例:
  ! 网络连接缓慢
```

#### 1.4 信息吐司

```
背景:               #E0F7F5
边框:               1px solid #00C7BE
图标:               i (青色)
文本:               #00C7BE
示例:
  ℹ 已更新到最新版本
```

---

### 2. 加载指示器 (Loading Indicator) - 3 种

#### 2.1 旋转加载

```
属性定义:
  大小:               24px × 24px (可自定义)
  颜色:               #007AFF
  线宽:               3px
  动画:               无限旋转 (1.2s per rotation)
  
变体:
  Small (16px)
  Medium (24px) - 常用
  Large (32px)
```

#### 2.2 脉冲加载

```
圆形或方形，不断闪烁
透明度变化: 0.3 → 1.0 → 0.3
动画: 1.5s per cycle
```

#### 2.3 骨架屏加载

```
显示灰色占位符形状
模拟将要加载的内容布局
闪烁动画: 从左到右的亮度波动
```

---

### 3. 进度加载 (Loading Progress)

```
与进度条相同
在加载内容时显示进度
```

---

### 4. 空状态 (Empty State) - 3 种

#### 4.1 无数据

```
显示:
  [大图标或插图] (120px × 120px)
  标题: "暂无数据"
  描述: "请尝试调整搜索条件"
  [操作按钮] (可选，如"返回首页")
```

#### 4.2 无搜索结果

```
显示:
  [搜索图标]
  标题: "未找到匹配结果"
  描述: "搜索关键词: xxx"
  [返回/新搜索按钮]
```

#### 4.3 无权限

```
显示:
  [禁止图标]
  标题: "您没有权限访问"
  描述: "请联系管理员"
  [返回首页按钮]
```

---

### 5. 骨架屏 (Skeleton Screen)

```
显示加载中的内容占位符
预期内容形状:
  - 文本行: 灰色长方形
  - 图像: 灰色正方形
  - 头像: 灰色圆形
  
动画: 闪烁或从左到右的光波效果
```

---

### 6. 工具提示 (Tooltip)

```
属性定义:
  背景:               #333333 (深灰)
  文本:               #FFFFFF
  Padding:            8px 12px
  Font Size:          12px
  边框圆角:           4px
  
显示:
  鼠标悬停在元素上后显示 (300ms 延迟)
  显示在元素上方/下方/左侧/右侧
  自动调整位置以避免超出屏幕
  
关闭:
  鼠标移开后隐藏
  
示例:
  保存 (鼠标悬停) → 提示: "保存当前内容"
```

---

### 7. 确认对话框 (Confirmation Dialog)

```
在反馈组件库已定义 (Modal Dialog)
```

---

### 8. 通知中心 (Notification Center)

```
属性定义:
  通常在页面右上角显示
  显示通知列表
  每条通知: 360px × 80px
  
功能:
  - 显示未读通知数量徽章
  - 点击打开通知面板
  - 通知可展开/折叠
  - 支持标记已读/清除
```

---

### 9. 消息气泡 (Message Bubble/Chat Bubble)

```
属性定义:
  背景:               #007AFF (用户) 或 #F2F2F7 (其他)
  文本:               #FFFFFF (用户) 或 #000000 (其他)
  Padding:            12px 16px
  边框圆角:           16px
  最大宽度:           70% 容器宽度
  
布局:
  [头像] [消息气泡] [时间戳]
```

---

### 10. 通知横幅 (Notification Banner)

```
属性定义:
  全宽横幅 (通常在顶部或底部)
  高度:               48px
  Padding:            12px 24px
  图标 + 文本 + 关闭按钮
  
颜色:
  成功:               #D1F4DD, #34C759
  错误:               #FFE8E6, #FF3B30
  警告:               #FFF3E0, #FF9500
  信息:               #E0F7F5, #00C7BE
```

---

### 11. 反馈表单 (Feedback Form)

```
模态框包含:
  - 反馈类型选择 (下拉菜单)
  - 反馈内容输入框 (多行文本)
  - 联系方式输入 (可选)
  - 屏幕截图上传 (可选)
  - 提交/取消按钮
```

---

### 12. 评分组件 (Rating)

```
与表单组件中的评分器相同
```

---

### 13-18. 其他反馈组件

- **13. 进度对话框** (Progress Dialog)
- **14. 结果对话框** (Result Dialog)
- **15. 警告信息** (Warning Message)
- **16. 错误边界** (Error Boundary)
- **17. 重试组件** (Retry Component)
- **18. 版本提示** (Version Notification)

---

## 🚀 高级组件库 (12 个)

### 1. 搜索栏 (Search Bar)

```
属性定义:
  高度:               40px
  宽度:               fill_container (最大 600px)
  背景:               #F2F2F7
  边框:               1px solid #E0E0E0
  边框圆角:           20px (药丸形)
  Padding:            8px 16px
  
组件:
  左侧:               搜索图标 (16px)
  中间:               输入框
  右侧:               清除/搜索按钮
  
状态:
  Focus:
    边框:             2px solid #007AFF
    背景:             #FFFFFF
    
下拉建议:
  显示搜索历史或推荐搜索词
  点击项进行搜索
```

---

### 2. 数据表格 (Data Table)

```
属性定义:
  每行高度:           48px
  表头高度:           48px
  表头背景:           #F2F2F7
  表头文字:           14px, 600 weight, #000000
  
行:
  Padding:            16px
  边框:               1px solid #E0E0E0
  
行状态:
  Normal:
    Background:      #FFFFFF
    
  Hover:
    Background:      #F9F9F9
    
  Selected:
    Background:      #E8F3FF
    左侧复选框: 选中
    
  Disabled:
    Opacity:         0.5
    Cursor:          not-allowed

功能:
  - 行选择 (左侧复选框)
  - 排序 (表头点击)
  - 分页 (下方)
  - 列隐藏/显示
  - 行展开 (子内容)
  - 单元格编辑
  - 导出为 CSV/Excel
```

---

### 3. 图表组件 (Chart Components)

#### 3.1 柱状图 (Bar Chart)

```
属性定义:
  包含坐标轴、柱子、图例
  可配置水平/竖直显示
  支持多系列数据
  
颜色:
  系列 1: #007AFF
  系列 2: #5856D6
  系列 3: #00C7BE
```

#### 3.2 折线图 (Line Chart)

```
属性定义:
  包含坐标轴、折线、数据点、图例
  支持多条线
  
交互:
  - 悬停显示数据提示
  - 点击数据点显示详情
```

#### 3.3 饼图 (Pie Chart)

```
属性定义:
  显示比例
  包含图例和百分比标签
  
交互:
  - 悬停显示提示
  - 点击段落展开
```

#### 3.4 热力图 (Heatmap)

```
显示密度分布
颜色深浅表示数据大小
```

---

### 4. 富文本编辑器 (Rich Text Editor)

```
包含:
  工具栏 (24px 高):
    - 加粗、斜体、下划线
    - 有序/无序列表
    - 链接、引用、代码块
    - 标题级别选择
    - 文字颜色、背景色
    - 撤销/重做
    
编辑区域:
  最小高度: 200px
  背景: #FFFFFF
  边框: 1px solid #E0E0E0
  边框圆角: 8px
  
预览模式:
  显示格式化后的内容
```

---

### 5. 文件管理器 (File Manager)

```
包含:
  左侧:               文件夹树形导航
  中间:               文件/文件夹列表
  右侧:               预览或属性面板
  
功能:
  - 新建文件夹
  - 上传文件
  - 删除/重命名
  - 搜索
  - 排序 (名称/大小/修改时间)
  - 右键菜单
```

---

### 6. 图片查看器 (Image Viewer)

```
属性定义:
  全屏显示图片
  包含:
    - 上一张/下一张按钮
    - 放大/缩小按钮
    - 旋转按钮
    - 全屏按钮
    - 关闭按钮
    
支持:
  - 键盘快捷键 (左右箭头翻页)
  - 鼠标滚轮缩放
```

---

### 7. 代码编辑器 (Code Editor)

```
属性定义:
  包含行号
  语法高亮
  主题支持 (浅色/深色)
  
功能:
  - 代码折叠
  - 搜索替换
  - 格式化
  - 复制代码按钮
```

---

### 8. 树形组件 (Tree)

```
属性定义:
  支持展开/折叠
  支持多选
  支持拖拽排序
  
项目:
  高度:               32px
  Padding:            8px
  图标 (可选) + 文本 + 操作菜单
  
状态:
  Collapsed:          ▶ 图标
  Expanded:           ▼ 图标
  Selected:           背景 #E8F3FF
```

---

### 9. 日历 (Calendar)

```
属性定义:
  显示月历或年历
  包含周天标题行
  标记今天、选中日期、事件
  
事件显示:
  在日期下方显示事件点 (彩色圆点)
  点击显示事件列表
```

---

### 10. 时间线 (Timeline)

```
属性定义:
  竖向排列事件
  中间竖线
  左右交替显示事件
  
事件项:
  圆形节点 (12px) 在竖线上
  标题 + 描述 + 时间戳
  颜色表示状态 (完成/进行中/待处理)
```

---

### 11. 评论组件 (Comment)

```
属性定义:
  [头像] [用户名] [时间戳]
  [评论内容]
  [点赞/回复按钮]
  
嵌套评论:
  支持回复链式显示
  缩进 24px 表示嵌套
  
支持:
  - 编辑评论
  - 删除评论
  - 点赞评论
```

---

### 12. 卡片轮播 (Carousel)

```
属性定义:
  显示多个卡片
  可水平滚动或自动播放
  
控制:
  - 左/右箭头按钮
  - 底部圆点指示器 (可点击)
  - 自动播放 (可设置间隔)
  
项目间距: 16px
```

---

## 📖 使用指南

### 快速开始

1. **导入设计系统**
   - 在 Figma 中创建新文件
   - 导入此配置和颜色/排版系统
   - 应用到所有新组件

2. **创建组件实例**
   - 从组件库中拖拽所需组件
   - 修改属性 (文本、颜色、大小等)
   - 应用到屏幕设计

3. **保持一致性**
   - 使用预定义的颜色变量
   - 使用预定义的排版样式
   - 使用预定义的间距系统
   - 不要创建新的颜色或排版

### 状态管理

所有可交互组件应包含:
- **Default**: 正常状态
- **Hover**: 鼠标悬停
- **Active**: 按下/选中
- **Disabled**: 禁用
- **Focus**: 获得焦点 (输入框)
- **Error**: 错误状态 (表单)
- **Loading**: 加载中 (按钮)

### 响应式设计

设计需覆盖三种分辨率:
- **Desktop**: 1920px × 1080px
- **Tablet**: 768px × 1024px (iPad)
- **Mobile**: 375px × 812px (iPhone)

### 导出指南

完成设计后:
1. 生成 CSS 变量和类
2. 导出组件代码 (React/Vue/Web Components)
3. 生成设计文档和组件说明
4. 准备开发者交付包

---

**项目状态**: ✅ **所有 120+ 组件已定义**  
**下一步**: 在 Figma 中实现所有组件和 156 屏设计

