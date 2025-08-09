# 多平台内容抓取工具

这是一个用于抓取微信公众号文章和微博内容（包括PC端和手机端）的Python应用程序，提供Web API接口和直接脚本运行两种方式。支持使用Microsoft Edge浏览器进行内容抓取。

## 功能特性

- 通过API接口获取微信公众号文章标题和内容
- 支持处理微信文章访问验证
- 提供Web服务和命令行两种使用方式
- 支持后台服务运行
- 使用Microsoft Edge浏览器进行内容抓取
- 支持微博内容抓取（PC端和手机端）
- 支持多种内容源的统一接口

## 环境要求

1. Windows 10或更高版本
2. Python 3.7或更高版本
3. Microsoft Edge浏览器
4. Microsoft Edge WebDriver (EdgeDriver)

## 安装步骤

### 1. 安装Python

- 访问[Python官方网站](https://www.python.org/downloads/windows/)
- 下载适用于Windows的最新Python版本
- 运行安装程序，确保勾选"Add Python to PATH"选项
- 完成安装后，在命令提示符中验证安装：
  ```
  python --version
  ```

### 2. 安装Microsoft Edge浏览器

- 确保系统已安装Microsoft Edge浏览器（Windows 10/11通常默认安装）
- 检查Edge浏览器版本：打开Edge浏览器，点击右上角三个点 -> 帮助和反馈 -> 关于Microsoft Edge

### 3. 安装Microsoft Edge WebDriver

- 访问[Microsoft Edge WebDriver下载页面](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)
- 根据您安装的Edge浏览器版本下载对应的Edge WebDriver
- 将下载的Edge WebDriver解压，并将其路径添加到系统PATH环境变量中
  1. 右键"此电脑" -> "属性" -> "高级系统设置"
  2. 点击"环境变量"
  3. 在系统变量中找到"Path"并编辑
  4. 添加Edge WebDriver所在的文件夹路径

### 4. 安装项目依赖

1. 打开命令提示符(cmd)或PowerShell
2. 进入项目目录：
   ```
   cd D:\self_project\wechat_official_download
   ```
3. 安装所需依赖：
   ```
   pip install -r requirements.txt
   ```

## 运行方式

### 方法1：命令行直接运行

直接运行`wx.py`脚本获取微信公众号文章：
```bash
python wx.py
```
根据提示输入微信公众号文章链接

直接运行`weibo.py`脚本获取PC端微博内容：
```bash
python weibo.py
```
根据提示输入微博文章链接

直接运行`weibocn.py`脚本获取手机端微博内容：
```bash
python weibocn.py
```
根据提示输入手机端微博文章链接（m.weibo.cn域名）

### 方法2：Web API服务

1. 在命令提示符中进入项目目录
2. 运行以下命令启动服务：
   ```
   python api.py
   ```
3. 服务将在`http://localhost:5000`上运行

## 内容标题格式

微博内容的标题按照"发布者在发布时间发布了一条微博"的格式显示，例如：

```
现代快报在25-8-8 23:00发布了一条微博
```

微信公众号文章标题保持原样。

## 使用API

启动服务后，可以通过以下方式获取文章内容：

```bash
curl "http://localhost:5000/get_article?url=文章链接"
```

或者在浏览器中访问：
```
http://localhost:5000/get_article?url=文章链接
```

API会根据URL域名自动选择合适的处理脚本：
- weixin.qq.com 域名使用 wx.py 脚本
- weibo.com 域名使用 weibo.py 脚本
- m.weibo.cn 域名使用 weibocn.py 脚本

## 常见问题

1. 如果遇到Edge WebDriver版本不匹配问题，请确保Edge WebDriver版本与Edge浏览器版本一致
2. 如果遇到权限问题，请尝试以管理员身份运行命令提示符
3. 如果遇到依赖安装问题，请尝试使用：
   ```
pip install --upgrade pip
pip install -r requirements.txt
```

## 免责声明

本项目仅供学习交流使用，不得用于任何商业用途。使用者应遵守相关法律法规，自行承担使用本项目产生的风险和责任。作者不对因使用本项目而导致的任何损失或法律问题负责。
