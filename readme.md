

# 一、简介

>  广州大学 健康信息系统 自动打卡 

可以多个账号打卡





可使用平台：

* Linux
* Windows



可选择的方法：

* selenium
* requests直接请求





# 二、演示

## selenium

### ① Linux

![20220712150124.png](https://s2.loli.net/2022/07/12/djcb8eR2Xpg5TPy.png)







### ② Windows

![2022071215gfdsgdfg0124.png](https://s2.loli.net/2022/07/12/9fsHzURF1dbimK3.png)





## requests直接请求

### ① 腾讯云函数





### ② Linux

![image.png](https://s2.loli.net/2022/07/12/sHm6ZxWTcLw7GfC.png)





### ③ Windows

![20220712fdafds150647.png](https://s2.loli.net/2022/07/12/94nPvcZ6AN8j73u.png)









# 三、安装

## selenium

只需要安装`selenium`

~~~shell
pip install -r requirements.txt
~~~



## requests请求方法

需要安装`request`和`lxml`

~~~shell
pip install -r requirements.txt
~~~







# 使用方法

建议使用腾讯**云函数**通过**request**方法直接打卡（腾讯云函数有免费额度，相当于白嫖）









# 感谢

request方法，登录部分rsa解密使用的函数：[该仓库](https://github.com/AxisZql/Automatic-clock-in)

