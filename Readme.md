
# 网络检查与测试

根据[配置文件](./app.conf)中的信息，从以下两方面检查网络情况：

* 进行`ping`操作，并记录相关的`ping`结果信息
* 下载指定文件，并记录下载过程相关的信息

检查结果保存至程序当前目录的`./report`文件夹

## 依赖

* python2.7
* pycurl
* beautifulsoup4
* PyInstaller(可选生成Windows可运行程序用)

## 运行

### 直接运行

```
python NetDetection.py
```

### 生成exe文件

```
pyinstaller -F NetDetection.py
```
