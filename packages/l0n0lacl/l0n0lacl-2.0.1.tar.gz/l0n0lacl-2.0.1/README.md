# 1 功能描述
由于在ascendc算子开发过程中运行算子比较复杂，为了简化算子的运行，将运行算子变成可以用python直接调用的函数。所以编写了此代码。

# 2 安装
```
pip install l0n0lacl
```

# 3 运行算子实例
## 3.1 先切换到cann环境,比如我的环境是:
```
source /home/HwHiAiUser/Ascend/ascend-toolkit/set_env.sh
```
## 3.2 设置要用到的设备
```
export ASCEND_VISIBLE_DEVICES=0,1
```

## 3.3 运行算子
```python
from l0n0lacl import *
import numpy as np
import ctypes
fn = 算子运行器('Abs')
a = np.random.uniform(-2, -1, (2000,2000))
a_out = np.zeros_like(a)
out = fn(a, a_out)
print(a)
print(out[1])

a = 张量(a).切换到设备(1)
a_out = 张量(a_out).切换到设备(1)
out = fn(a, a_out)
print(a)
print(out[1])

fn = 算子运行器('InplaceAcos')
a = np.random.uniform(-1, 1, (2000,2000)).astype(np.float16)
print(a)
out = fn(a)
print(out[0])

fn = 算子运行器('AdaptiveAvgPool2d')
a = np.random.uniform(0, 100, (2, 100, 100)).astype(np.float32)
out = np.zeros((2, 3, 3), dtype=a.dtype)
a = 张量(a, 格式=张量格式.NCL)
out = 张量(out).变更格式(张量格式.NCL)
output = fn(a, [3, 3], out)
print(output[2])


fn = 算子运行器('Addmv')
s = np.ones(3, dtype=np.float32)
mat = np.random.uniform(-1, 1, (3, 4)).astype(np.float32)
vec = np.random.uniform(-1, 1, 4).astype(np.float32)
alpha = 标量(1.2)
beta = 标量(1.1)
out = np.zeros(3, dtype=np.float32)
output = fn(s, mat, vec, alpha, beta, out, ctypes.c_int8(1))
print(output[-2])
```
## 3.3 算子查找顺序
```
如果 ${NO_VENDORS_OPP} != '1':
    查找 ${ASCEND_OPP_PATH}/vendors目录(自己写的算子默认安装目录) 
查找 ${ASCEND_HOME_PATH}/lib64/libopapi.so 支持的算子(也就是官方算子包)
```
* `NO_VENDORS_OPP` 如果不需要使用自定义算子, 可以添加此环境变量
* `ASCEND_OPP_PATH` cann自带环境变量 在(source /home/HwHiAiUser/Ascend/ascend-toolkit/set_env.sh)时设置
* `ASCEND_HOME_PATH`cann自带环境变量在(source /home/HwHiAiUser/Ascend/ascend-toolkit/set_env.sh)时设置