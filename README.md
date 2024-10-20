# Tutorial
将下载好的`*.glb`文件存入文件夹`/glb_data`，运行`render_all.py`会将所有渲染结果存入文件夹`/rendered_data`，再运行`pa_classify.py`(需先下载预训练模型)即可以将分类结果存入对应被分类图片所在文件夹下的`output.txt`中。有关爬虫、渲染器、分类器三部分的介绍依次如下。

# Tutorial : Scrapy

## Requirements
using python==3.12.5.

```bash=
pip install -r requirements.txt
```

### Part 1 ChromeDriver
用谷歌chrome访问[这里](https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json)寻找对应版本/系统的谷歌驱动。

![alt text](<./assets/1.png>)

注意勾选pretty-print。
安装完成后记得将其加入你的命令行中。（windows 添加环境变量），直到在powershell/cmd中输入chromedriver可以有输出为止。

![alt text](<./assets/2.png>)
![alt text](<./assets/3.png>)
![alt text](<./assets/4.png>)
![alt text](<./assets/5.png>)

### Part 2 爬虫

过程中请不要随意改变窗口大小，会导致页面布局和抓取元素错误QAQ

要注意登陆后等待控制台输出“请确认登录状态，按任意键继续。”后再输入密码，登录。登录完成后按任意键。

### TODO:
    Recovery from StaleElementRefrence at any time.
    Bad Network Connection.
    Store in Json.
    
#### 从sketchfab 迁移到 sketchfab2

10.11.2024: 我们刚刚发布了新的爬虫脚本`sketchfab2.py`和内容获取脚本`./progress/prepare_urls.py`脚本，旨在于改善原有的直接获取下载弹窗导致的不稳定状况。
通过预先加载和储存下载url的方式进行。

##### 直接迁移爬虫

> 1. 首先，从sketchfab中获得您原有的下载进度，将其填入到`/progress/download_index.json`中。
> 2. 清除并且新建一个`/progress/download_url.pkl`文件。
> 3. 运行`sketchfab2.py`。

您也可以自行先加载url。运行`prepare_urls.py`即可。

10.12.2024 00:40:34
增加了對於下載了zip文件的處理。經詢問可以不保留texture。

# Tutorial : render
## Python
所需Python版本为3.10

## 依赖库下载
由于新版本blender(4.2)对于深度图的处理存在bug，请由 https://pypi.org/project/bpy/3.6.0/#files 根据系统下载对应的bpy库wheel文件，并使用`pip install` 安装。

若pypi下载速度过慢，可使用Motrix等并行下载器，效果显著。

## 性能设置
若设备拥有独立显卡，对于Windows11系统，请在 `设置->系统->屏幕->显示卡->应用的自定义选项`界面，根据所使用的Python路径（注意区分虚拟环境与base环境），将`python.exe`设置为 “高性能”。

## 摄像头距离的调整
由于模型尺度不一，渲染过程使用了`auto_dist`函数来自动调整摄像头到模型中心的距离，若需手动控制距离或者获得相关距离信息，请修改256行处的`auto_dist(target)`为长度(米)或为其添加输出。

# Tutorial : pa-classifier

## Requirments
一般只需torch，如运行不了请参考`/pa_classifier/requirments.txt`

