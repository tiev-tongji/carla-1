# multicarlasevers

## 运行Server

1. 进入CarlaUE4.sh所在路径，在terminal输入

   ```shell
   ./CarlaUE4.sh
   ```

   注：直接使用UE4 editor点击play也可运行，但速度很慢，可以使用make package进行打包。

2. 进入/PythonAPI/util，输入指令更改地图配置

   ```shell
   python3 config.py --map Town04
   ```

## 运行Client

 1. 在Server开启的前提下，运行/Mult-carla/client下的客户端程序

    ```
    python3 manual_control.py   
    ```

2. 配置Mult-carla文件夹下carlaservers.yaml文件，其中需要同步的服务器CarlaUE的ip和端口。（至少一台）

## 同步模块

1. 在控制台下运行Mult-carla下的同步服务器程序

   ```
   python3 synchronization.py
   ```

2. 运行Mult-carla/viewer下的程序可以轮流查看服务器内车辆

   ```
   python3 clientview.py
   ```

3. 设置服务器日志为DEBUG级别可以运行

   ```
   python3 synchronization.py --debug
   ```

## Carla-SUMO协同仿真

详见Carla官方文档https://carla.readthedocs.io/en/latest/adv_sumo/

## 关于测试

1. 运行/Mult-carla/client下的客户端程序，在控制台会输出帧率、内存、显存情况，运行结束后会生成表格文件，查看详细数据。

   ```shell
   python3 manual_control_test.py
   ```

2. 在需要分析的函数前面增加`@profile`装饰器，在控制台输入如下命令进行内存消耗分析

   ```shell
   python -m memory_profiler manual_control.py
   ```

3. 在需要分析的函数前面增加`@profile`装饰器，在控制台中使用如下指令启动运行时间消耗分析工具，结束会在窗口打印逐行信息以及生成一个lprof文件。

   ```
   kernprof -l manual_control.py
   ```

## 如果提示找不到carla包

```
cd ~/carla/PythonAPI/carla/dist/
unzip carla-0.9.13-py3.8-linux-x86_64.egg -d carla-0.9.13-py3.8-linux-x86_64
cd carla-0.9.13-py3.8-linux-x86_64
```
接下来打开你的文档编辑器，建立一个setup.py, 将以下内容复制进去。
```
from distutils.core import setup
setup(name='carla',
      version='0.9.13', 
      py_modules=['carla'],
      )
```
然后通过pip安装到你的python3当中，从此可以直接import carla了。
```
pip3 install -e ~/carla/PythonAPI/carla/dist/carla-0.9.13-py3.8-linux-x86_64
```
