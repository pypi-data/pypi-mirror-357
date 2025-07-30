# 配置页面生成助手

只需一个JSON/YAML配置文件，就可以生成一个配置页面并实现配置功能，支持多种表单控件，包括文本输入框、下拉框、单选框、复选框、开关、日期选择器、范围选择器等。

---

## 使用方法

> 支持直接调用，也可以生成项目模板

使用前需要 `pip install -U xiaoqiangclub` 安装 `xiaoqiangclub` 模块

### 直接调用接口

参考下面的调用示例：

```python
from xiaoqiangclub import generate_config_ui

# 用户可以在现有应用中调用 generate_config_ui 函数
# default_config_file = r"D:\001_MyArea\002_MyCode\001_PythonProjects\2024\xiaoqiangclub\xiaoqiangclub\templates\html\config_template\config_ui.json"
config_file = r"D:\001_MyArea\002_MyCode\001_PythonProjects\2024\xiaoqiangclub\xiaoqiangclub\templates\html\config_template\config_ui.yml"
data_dir = r"D:\001_MyArea\002_MyCode\001_PythonProjects\2024\xiaoqiangclub\tests"
# 将配置功能集成到现有应用中
app = generate_config_ui(default_config_file=config_file, user_config_dir_or_file=data_dir, route_path="/config")


# 其他路由或功能保持不变
@app.get("/")
async def root():
    return "Hello XiaoqiangClub!"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

```

### 生成模板

安装 `xiaoqiangclub` 模块后，终端执行 `xiaoqiangclub config_ui_template` 生成项目模板。修改 [config_ui.py](./config_ui.py)
中的 `config_file = "config_ui.json"` 指向你的配置文件，然后运行
`config_ui.py` 即可启动配置页面服务器。用户配置后，会自动生成一个 `"data/user_config.json"` 文件，用户可以通过访问
`127.0.0.1:8000` 或手动修改该文件，以实现动态配置。后端的其他应用直接调用该文件即可。

注意：配置文件中需要使用 `双引号""`

## 顶级字段说明

### **title**: 页面标题（必需）

- **描述**: 页面标题显示在浏览器标签栏。
- **类型**: 字符串
- **示例**:
  ```json
  "title": "设置界面"
  ```

### **title_link**: 页面标题链接（可选）

- **描述**: 标题下方的链接，点击后会跳转到该链接
- **类型**: 字符串
- **示例**:
  ```json
  "title": "设置界面"
  ```

### **welcome**: 欢迎页面的设置字段（可选）

- **描述**: 用于设置网站的欢迎页面内容，包括页面标题、正文内容、同意条款文本以及取消跳转链接等配置项。用户首次访问时会看到该页面，用户必须同意条款才能继续使用系统。支持自定义标题、内容、同意条款文本、链接等配置。

- **类型**: 字典（包含标题、内容、取消时跳转的链接等配置项）

- **示例**:
  ```json
  "welcome": {
    "title": "欢迎使用本系统",     
    "content": "请阅读以下须知并确认同意。我们希望为您提供优质服务。",  
    "content_alignment": "center",  
    "agree_text": "我已阅读并同意以上条款", 
    "agree_link": "https://example.com/terms",
    "cancel_link": "https://xiaoqiangclub.us.kg/" 
  }
  ```

- **字段说明**:
    - **`title`**: （可选）欢迎页面的标题，默认为 `"欢迎使用本系统"`。可以根据需求进行自定义。
    - **`content`**: （可选）欢迎页面的详细内容，默认为 `"请阅读以下须知并确认同意。我们希望为您提供优质服务。"。` 内容支持
      `\n` 换行符，用于多行显示，可自定义内容。
    - **`content_alignment`**: （可选）设置 `content` 内容的对齐方式。可选值为 `"left"`、`"center"`、`"right"`。默认值为
      `"left"`。
    - **`agree_text`**: （可选）同意条款的文本，默认为 `"我已阅读并同意以上内容"`。此字段可以根据需求自定义。
    - **`agree_link`**: （可选）当用户点击 "阅读用户须知" 时跳转的链接。默认为空，如果设置了该字段，用户点击链接将跳转至提供的链接（如填写条款链接）。若未设置，则默认不会显示此链接或使用
      `agree_link == ""` 时显示默认链接。
    - **`cancel_link`**: （可选）点击取消按钮时跳转的链接，默认为 `https://xiaoqiangclub.us.kg/`。如果没有设置此字段，取消时跳转至默认链接。

- **注意**:
    - **`welcome` 字段未设置**: 如果未设置 `welcome` 字段，则欢迎页面将不会显示。
    - **`agree_link`**: 如果设置了 `agree_link`，在同意条款文本后将会显示“阅读用户须知”的超链接，点击后用户将跳转至该链接。若此字段为空（
      `""`），则会显示默认的链接（例如：`https://xiaoqiangclub.blog.csdn.net/article/details/138905099`）。
    - **“取消”按钮的跳转**: 如果用户点击“取消”按钮，则会跳转到 `cancel_link`
      所指定的链接。如果该字段为空或未设置，默认会跳转至 `https://xiaoqiangclub.us.kg/`。
    - **未同意条款时**: 如果用户未勾选“我已阅读并同意”复选框，点击“确认”按钮时，系统会弹出提示要求用户勾选同意框后才能继续操作。

### **help**: 帮助文档

- **描述**: 当鼠标悬浮在标题上时，会显示该字段中的内容
- **类型**: 字符串
- **示例**:
  ```json
  "help": "这是一个帮助文档"
  ```

### **logo**: 网站或应用的 logo 图片地址（可选）

- **描述**: 设置网站 logo 图片地址，默认为：http://217.142.251.127/h/img/xiaoqiangclub_logo.png
- **类型**: 字符串（URL 地址）
- **示例**:
  ```json
  "logo": "https://example.com/logo.png"
  ```

### **footer**: 页脚说明（可选）

- **描述**: 页脚说明，显示在页面底部，默认值为 `XiaoqiangClub`。可以设置 `footer_link` 进行跳转。
- **类型**: 字符串
- **示例**:
  ```json
  "footer": "All rights reserved."
  ```

### **footer_link**: 页脚链接（可选）

- **描述**: footer的链接，点击后会跳转到该链接，默认为：https://xiaoqiangclub.us.kg/
- **类型**: 字符串
- **示例**:
  ```json
  "footer_link": "https://xiaoqiangclub.us.kg/"
  ```

### **max_width**: 页面最大宽度（可选）

- **描述**: 页面最大宽度，默认为 `3xl`，TailwindCSS风格，[参考文档](https://tailwindcss.com/docs/max-width) 。
- **类型**: 字符串
- **示例**:
  ```json
  "max_width": "5xl"
  ```

### **items**: 配置项的分组（必需）

- **描述**: 配置项分组，每个分组表示一个表单的标题，包含该表单下的所有配置项。
- **类型**: 对象
- **示例**:
  ```json
  {
      "个人信息": { ... },
      "账户设置": { ... }
  }
  ```

### **update_info**: 更新提示页面（可选）

- **描述**: 用于设置网站的更新提示页面内容，包括版本号、更新内容、更新链接等配置项。当有新版本时，系统会弹出此提示页面，用户可以查看更新内容并通过点击按钮跳转到指定的更新页面进行更新。
- **使用方法**: 后端检查是否有新版本，有新版本的时候给传递到前端的 `settings` 参数中 **添加 `update_info`
  字段，该字段的值为字典类型，包含发现的`新版本号、更新内容、更新内容对齐方式、更新链接`等** 配置项。

- **类型**: 字典（包含版本号、更新内容、更新链接等配置项）

- **示例**:
  ```json
  "update_info": {
    "version": "1.2.0",   // 新版本的版本号
    "content": "新版本已发布，\n新增了多个功能和修复了一些问题。点击下方按钮进行更新。", // 更新的具体内容，支持换行符
    "content_alignment": "center",  // 内容的对齐方式，可选 "left"、"center"、"right"。默认值为 "left"
    "update_url": "https://example.com/update"  // 更新链接，用户点击按钮后跳转到此链接进行更新
  }
  ```

- **字段说明**:
    - **`version`**: （必填）新版本的版本号，用于显示在更新提示标题中。例如 `"1.2.0"`。
    - **`content`**: （可选）更新的详细内容，默认为 `"发现新版本可用，请点击下方按钮进行更新。"。` 内容支持换行符 (`\n`)
      ，用于多行显示，可以自定义内容。例如，描述新增的功能或修复的错误等。
    - **`content_alignment`**: （可选）设置 `content` 内容的对齐方式。可选值为 `"left"`、`"center"`、`"right"`。默认值为
      `"center"`。
    - **`update_url`**: （必填）点击“立即更新”按钮后跳转的链接。用户点击按钮后将被引导到此链接，通常是应用的更新页面或应用商店链接。

- **功能说明**:
    - 在有更新信息时，系统会自动显示一个更新提示弹窗，用户可以查看更新版本和内容。更新内容支持换行显示，且内容区域提供滚动条以适应较长内容。
    - 弹窗中的“立即更新”按钮将链接到指定的 `update_url`，用户点击按钮后跳转到更新页面进行更新。

- **示例使用场景**:
    - 当后台系统发布了新版本时，可以通过此配置告知用户有关版本更新的详细信息，确保用户及时更新到最新版本。

---

## 配置项字段说明

每个配置项包含以下字段：

### **order**: 表单项顺序（必需）

- **描述**: 控制每一个表单项在页面中的显示顺序。
- **类型**: 整数
- **示例**:
  ```json
  "order": 1
  ```

### **label**: 表单项标签（必需）

- **描述**: 表单项的名称或标签，显示在用户界面上。
- **类型**: 字符串
- **示例**:
  ```json
  "label": "用户名"
  ```

### **help**: 表单项帮助说明（可选）

- **描述**: 设置该项后会在 `label` 后面显示一个 `?`，悬停时会显示帮助说明。
- **类型**: 字符串
- **示例**:
  ```json
  "help": "请输入用户名"
  ```

### **help_link**: 表单项帮助链接（可选）

- **描述**: 设置该项后，help 会变成一个链接，点击后会跳转到该链接。
- **类型**: 字符串
- **示例**:
  ```json
  "help_link": "https://example.com"
  ```

### **type**: 表单项类型（必需）

- **描述**: 表单项的类型，决定表单项的显示方式。
- **类型**: 字符串
- **可选值**:
    - `text`：文本输入框
    - `list` ：添加多个项并展示，支持删除
    - `select`：下拉框
    - `radio`：单选框
    - `checkbox`：复选框
    - `switch`：开关
    - `date`：日期选择器
    - `range`：范围选择器
- **示例**:
  ```json
  "type": "input"
  ```

### **value**: 默认值（必需）

- **描述**: 表单项的初始值，用户提交时将会返回该字段的值。
- **类型**: 根据 `type` 类型不同而不同：
    - 对于 `input`、`select`、`radio`、`date` 等类型，`value` 为字符串。
    - 对于 `checkbox` 和 `list` 类型，`value` 为字符串数组，表示选中的选项。
    - 对于 `switch` 类型，`value` 为布尔值。
- **示例**:
  ```json
  "value": "xiaoqiangclub"
  ```

### **options**: 可选项（适用于 `select`、`radio`、`checkbox` 类型）

- **描述**: 提供的选项列表，用户可以选择其中一个或多个。
- **类型**: 数组（字符串）
- **示例**:
  ```json
  "options": ["男", "女"]
  ```

### **placeholder**: 占位符文本（适用于 `input` 类型）

- **描述**: 输入框未输入内容时显示的提示文本。
- **类型**: 字符串
- **示例**:
  ```json
  "placeholder": "请输入用户名"
  ```

### **min**: 最小值（适用于 `range` 类型）

- **描述**: 范围选择器的最小值。
- **类型**: 数字
- **示例**:
  ```json
  "min": 0
  ```

### **max**: 最大值（适用于 `range` 类型）

- **描述**: 范围选择器的最大值。
- **类型**: 数字
- **示例**:
  ```json
  "max": 100
  ```

---

## 各种表单控件类型及示例

### 1. **input** （文本输入框）

文本框用于输入单行文本。

```json
"username":{
"label": "用户名",
"type": "input",
"value": "user123"
}
```

### 2. **list** （列表输入框）

添加多个项并展示，支持删除。

```json
"douban": {
"label": "豆瓣",
"order": 2,
"placeholder": "请输入豆瓣用户ID",
"help": "请输入豆瓣用户ID",
"help_link": "https://www.douban.com/people/fsf/",
"type": "list",
"value": ["56548956"]
}
```

### 3. **password** （密码输入框）

文本框用于输入密码。

```json
"password":{
"order": 1,
"label": "用户名",
"type": "password",
"value": "password123"
}
```

### 4. **select** （下拉框）

下拉框用于提供多个选项供用户选择。

```json
"language":{
"order": 2,
"label": "语言选择",
"type": "select",
"options": [
"简体中文",
"English",
"日本語"
],
"value": "简体中文"
}
```

### 5. **radio** （单选框）

单选框允许用户从多个选项中选择一个。

```json
"gender":{
"order": 3,
"label": "性别",
"type": "radio",
"options": [
"男",
"女"
],
"value": "男"
}
```

### 6. **checkbox** （复选框）

复选框允许用户从多个选项中选择多个，`value` 为字符串数组。

```json
"hobby":{
"order": 4,
"label": "兴趣爱好",
"type": "checkbox",
"options": [
"阅读",
"旅行",
"运动",
"电影"
],
"value": [
"运动",
"旅行"
]
}
```

注意：`checkbox`不能单独放在一个 `item`，否则当全部没选中的情况下会无法保存数据。

### 7. **switch** （开关）

开关用于切换布尔值（例如启用/禁用）。

```json
"enable_notification":{
"order": 5,
"label": "启用通知",
"type": "switch",
"value": true
}
```

注意：`switch`不能单独放在一个 `switch`，否则当全部没选中的情况下会无法保存数据。

### 8. **date** （日期选择器）

日期选择器用于选择日期，`value` 为日期字符串。

```json
"birthday":{
"order": 6,
"label": "选择生日",
"type": "date",
"value": "2000-01-01"
}
```

### 9. **range** （范围选择器）

范围选择器通常用于选择一个数字范围。

```json
"brightness":{
"order": 7,
"label": "设置亮度",
"type": "range",
"min": 0,
"max": 100,
"value": 50
}
```

下面是修改后完成的 **分隔线**（line）的说明，包含了参数说明和 `JSON` 示例：

---

### 10. **line** （分隔线）

分隔线用于分隔不同部分的配置，参数说明：

- **"type"**: `"line"`。指定分隔线类型，必须为 `line`。
- **"thickness"**: 分隔线的粗细值 `border-t`，默认为 `1`
  。该值可以参考 [Tailwind CSS 文档](https://tailwindcss.com/docs/border-width)，可以设置为 `1`、`2`、`3` 等，表示不同的粗细程度。
- **"color"**: 分隔线的颜色 `border-`，默认为 `"gray-600"`。你可以选择 Tailwind CSS 预定义的颜色（如 `red-300`、`blue-500`
  等），也可以自定义颜色值，参考 [Tailwind CSS 自定义颜色文档](https://tailwindcss.com/docs/customizing-colors)。
- **"length"**: 分隔线的长度 `w-`，默认为 `"full"`。该值决定了分隔线的宽度。你可以选择像 `full`（100%宽度）、`1/2`（50%宽度）、
  `1/3`（33%宽度）等，或者使用具体的像素宽度如 `w-32` 等，参考 [Tailwind CSS 宽度文档](https://tailwindcss.com/docs/width)。
- **"spacing"**: 上下间距 `my-`，默认为 `6`，表示 `1.5rem`
  。可以根据需要调整分隔线与其他元素的垂直间距，参考 [Tailwind CSS 间距文档](https://tailwindcss.com/docs/margin)。

### 示例：

```json
"separator": {
"order": 8,
"type": "line",
"thickness": 2,
"color": "red-300",
"length": "2/3",
"spacing": 8
}
```

理解了，`code` 应该是后端响应返回的状态码，而不是前端配置的字段。也就是说，前端发送请求时，后端会返回一个 `code` 字段，前端需要根据这个
`code` 来判断请求是否成功或失败。

### 11. **button** （自定义按钮）

自定义按钮类型，可以在页面上显示按钮，并触发相应的操作（如提交表单、刷新页面等）。可以自定义按钮的文本、背景颜色、文字颜色等样式。

#### 示例配置：

```json
"submit_button": {
"order": 9,
"type": "button",
"button_text": "提交",
"fields": ["username", "password", "email"],
"route": "/submit",
"tooltip": "点击提交表单",
"bg_color": "#4CAF50",
"text_color": "#FFFFFF",
"success_message": "提交成功！",
"error_message": "提交失败！",
"reload": true
}
```

#### 字段说明：

- **type**: 固定为 `button`，表示这是一个按钮类型的字段。
- **button_text**: 按钮的显示文本，用户可根据需要自定义。
- **fields**: 一个数组，列出按钮触发时需要提交的字段名。可以是表单中的其他字段（如 `username`、`password`）。
- **route**: 按钮点击时向后端发送请求的 URL。可以是一个用于提交数据的 API 路径。
- **open_link**: 按钮点击时打开的链接。可以是一个 URL，用户点击按钮后，浏览器将打开该链接。
- **tooltip**: 鼠标悬停在按钮上时显示的提示文本。
- **bg_color**: 按钮的背景颜色（red-800）。遵守 Tailwind CSS [颜色类名](https://tailwindcss.com/docs/background-color)。
- **hover_color**: 鼠标触碰按钮时背景颜色变为什么颜色（red-800）。遵守 Tailwind
  CSS [颜色类名](https://tailwindcss.com/docs/background-color)。
- **text_color**: 按钮的文字颜色（gray-700）。遵守 Tailwind CSS [颜色类名](https://tailwindcss.com/docs/text-color)。
- **success_message**: 按钮操作成功后的提示信息。默认值为 `'操作成功'`。
- **error_message**: 按钮操作失败后的提示信息。默认值为 `'操作失败'`。
- **reload**: 一个布尔值，指示操作成功后是否刷新页面。默认为 `false`（不刷新），如果设置为 `true`，页面将在成功后刷新。

#### 按钮样式说明：

按钮的样式可以通过 `bg_color` 和 `text_color` 来定制，支持设置任何有效的 CSS 颜色值。如果这两个字段未提供，则会使用默认的配色方案（蓝色背景和白色文字）。

- `bg_color`: 背景色，支持任何有效的颜色值（如 `#ff5733`, `rgba(255,87,51,0.5)` 等）。
- `text_color`: 文字颜色，支持任何有效的颜色值（如 `#ffffff`, `black`, `rgb(0,0,0)` 等）。

#### 按钮功能：

1. **提交数据**: 按钮点击后，将提交 `fields` 字段数据到指定的后端接口，如果 `fields` 为空，将发送整个配置页面的数据。
2. **提示信息**: 根据请求的成功与否，显示相应的成功或失败消息。
3. **页面刷新**: 如果配置了 `reload: true`，则在操作成功后刷新当前页面。
4. **根据 `code` 进行错误判断**: 如果后端返回的 `code` 以 4 开头，前端会触发错误回调，显示错误提示并不执行成功回调。

#### 示例实现：

```html
<!-- 在前端 HTML 中，按钮会被渲染成以下内容 -->
<button id="custom-button-submit_button"
        class="bg-green-600 text-white px-3 py-2 rounded-md hover:bg-green-500 transition duration-300"
        title="点击提交表单"
        data-button='{"type": "button", "button_text": "提交", "fields": ["username", "password"], "route": "/submit", "tooltip": "点击提交表单", "bg_color": "#4CAF50", "text_color": "#FFFFFF", "successMessage": "提交成功！", "errorMessage": "提交失败！", "reload": true}'>
    提交
</button>
```

### 按钮操作的前端逻辑更新：

在前端，我们会根据后端返回的 `code` 字段来判断操作是否成功。下面是更新后的 `sendSettingsToBackend` 函数，它将根据 `code`
来决定是否触发错误回调。

```javascript
function sendSettingsToBackend(url, postData, successMessage = '设置已保存！', errorMessage = '保存失败！', shouldReload = false) {
    $.ajax({
        url: url,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(postData),
        success: function (response) {
            // 如果返回的 code 以 4 开头，表示错误
            if (response.code && response.code.toString().startsWith('4')) {
                // 显示错误提示
                $('#toast-error').text(errorMessage || '保存失败！').show().fadeOut(3000);
                return;  // 终止成功回调的执行
            }

            // 显示成功提示
            $('#toast').text(successMessage).show().fadeOut(3000);

            // 如果返回的响应包含 reload 标志，则刷新页面
            if (response.reload || shouldReload) {
                location.reload();  // 刷新整个页面
            }
        },
        error: function () {
            // 显示失败提示
            $('#toast-error').text(errorMessage || '保存失败！').show().fadeOut(3000);
        }
    });
}
```

### 后端的 `code` 返回示例：

后端返回时，应包含一个 `code` 字段，表示请求的结果状态。若返回的 `code` 以 4 开头（如 400、404、500 等），前端会视为错误。

#### 示例响应（成功）：

```json
{
  "code": 200,
  "message": "操作成功",
  "reload": true
}
```

#### 示例响应（错误）：

```json
{
  "code": 400,
  "message": "操作失败",
  "reload": false
}
```

### 总结：

- 后端返回的 `code` 字段用于前端判断操作是否成功。
- 当 `code` 以 4 开头时，表示请求失败，前端会触发 `error` 回调，显示错误提示，并停止执行后续成功回调。
- 自定义按钮的文本、颜色、字段和路由可以完全按照需求进行配置。
- 支持操作成功后显示提示消息，并根据 `reload` 配置决定是否刷新页面。

---

## 完整配置文件示例

```json
{
  "title": "设置界面",
  "logo": "http://217.142.251.127/h/img/xiaoqiangclub_logo.png",
  "footer": "XiaoqiangClub",
  "max_width": "3xl",
  "个人信息": {
    "gender": {
      "order": 1,
      "label": "性别",
      "type": "radio",
      "options": [
        "男",
        "女"
      ],
      "value": "男"
    },
    "douban": {
      "label": "豆瓣",
      "order": 2,
      "placeholder": "请输入豆瓣用户ID",
      "help": "请输入豆瓣用户ID",
      "help_link": "https://www.douban.com/people/fsf/",
      "type": "list",
      "value": [
        "56548956"
      ]
    }
  },
  "账户设置": {
    "username": {
      "order": 3,
      "label": "用户名",
      "type": "input",
      "placeholder": "请输入用户名",
      "value": ""
    },
    "password": {
      "order": 4,
      "label": "密码",
      "type": "password",
      "placeholder": "请输入密码",
      "value": ""
    },
    "separator": {
      "order": 5,
      "type": "line",
      "thickness": 3,
      "color": "red-300",
      "length": "2/3"
    },
    "hobbies": {
      "order": 6,
      "label": "选择兴趣爱好",
      "type": "checkbox",
      "options": [
        "阅读",
        "旅行",
        "运动",
        "电影"
      ],
      "value": [
        "旅行",
        "运动",
        "电影"
      ]
    }
  },
  "系统设置": {
    "language": {
      "order": 7,
      "label": "语言选择",
      "type": "select",
      "options": [
        "简体中文",
        "English",
        "日本語"
      ],
      "value": "简体中文"
    },
    "theme": {
      "order": 8,
      "label": "启用暗黑模式",
      "type": "switch",
      "value": "on"
    },
    "birthday": {
      "order": 9,
      "label": "选择生日",
      "type": "date",
      "value": "2000-01-01"
    },
    "brightness": {
      "order": 10,
      "label": "设置亮度",
      "type": "range",
      "min": 0,
      "max": 100,
      "value": "15"
    }
  }
}
```

## 提交与保存数据

- 用户修改表单项后，通过表单提交按钮提交数据，后端会接收到更新后的 JSON 数据。
- 后端根据提交的 JSON 数据更新配置文件，只修改对应 `value` 参数的值，保持数据结构不变。
