1.该项目是为了便于获取https://oss-fuzz-build-logs.storage.googleapis.com/index.html网站中
有状态变化的项目build日志，用于构建一个关于OSS-fuzz项目构建失败和对应修复方法的数据集。
2.下载的chrome驱动要在项目文件夹下创建文件夹chromedriver。或者在代码中修改指定的chrome驱动路径。
3.可以浏览https://oss-fuzz-build-logs.storage.googleapis.com/index.html的主机不需要配置科学上网工具，
不能的话需要进行配置
4.主函数调用的函数中顺序功能依次是获取/index.html网页代码、获取build error的项目的url、对项目的目标log
进行获取。