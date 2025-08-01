# Loya Timer

此项目是一个手动计时器（加班机），供<del>有加班需求的</del>虚拟主播使用（估计给公司老板或者员工用也行？）。

该项目使用Python3.12.10开发。

## 引用项目

[bottle](https://bottlepy.org/): 一个只使用Python标准库、极其轻量化的Web框架，这是开发中唯一使用的模块。
[Pyinstaller](https://pyinstaller.org/): 一个方便快捷的打包工具，项目的可执行文件使用它生成。

## 许可证

项目当前为闭源发布，禁止二次分发；后续若变更许可证会另行公告（例如将源码直接发布到github）。

有关[bottle](https://bottlepy.org/)和[Pyinstaller](https://pyinstaller.org/)的许可证，请移步到项目根文件夹的`LICENSE`文件夹查看两个项目的许可证原文。

## 项目结构

`LICENSE` - 存放引用项目的许可证原文
 + `Bottle`
 + `Pyinstaller`

`views` - 项目使用的前端视图
 + `css`
 + `js`
 + `favicon.ico` - 图标文件
 + `index.html`
 + `timer.html`

`config.json` - 配置文件

`main.py` - 项目的入口文件

`README.md` - 此文件

## 注意

部分杀毒软件可能会将本项目的可执行文件误报为病毒，但项目内并无任何恶意代码，还请放心使用（如果您实在担心，也可以找到开发者本人索要项目的源代码文件，但前提是您必须保证不向他人提供这些文件）。
