

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
![image.png](https://s2.loli.net/2022/07/12/5aXVpYI4Ec6TUxD.png)




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



# 一些不那么废话的废话
* 我用了一年的selenium方法，挂在腾讯服务器，除了几次小意外，基本没有意外。
* 没有必要去弄邮件、微信通知，如果打卡失败，班群会发通知，到时再去检查即可
* 在速度上request比selenium快的多，个人也推荐用request方法
* 如果要用腾讯云函数，自己百度怎么创建，注意将包安装在src目录即可。如：（pip3 install request -t ./src）
* 如果要挂在服务器，如centos，则需要安装chrome，百度有教程





# 感谢

request方法，登录部分rsa解密使用的函数：[该仓库](https://github.com/AxisZql/Automatic-clock-in)

