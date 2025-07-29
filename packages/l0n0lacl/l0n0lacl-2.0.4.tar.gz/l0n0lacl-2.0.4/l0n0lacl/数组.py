from .动态库加载器 import 加载cann_toolkit_lib64中的库
from .数据类型 import 将numpy类型转换为acl类型, acl数据类型
from .设备 import 设备
from .日志 import 记录acl返回值错误日志并抛出异常
from typing import Union, List
import numpy as np
import ctypes


libnnopbase = 加载cann_toolkit_lib64中的库('libnnopbase.so')
# aclIntArray *aclCreateIntArray(const int64_t *value, uint64_t size)
libnnopbase.aclCreateIntArray.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
libnnopbase.aclCreateIntArray.restype = ctypes.c_void_p
# aclnnStatus aclDestroyIntArray(const aclIntArray *array)
libnnopbase.aclDestroyIntArray.argtypes = [ctypes.c_void_p]
libnnopbase.aclDestroyIntArray.restype = ctypes.c_int

# aclFloatArray *aclCreateFloatArray(const float *value, uint64_t size)
libnnopbase.aclCreateFloatArray.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
libnnopbase.aclCreateFloatArray.restype = ctypes.c_void_p
# aclnnStatus aclDestroyFloatArray(const aclFloatArray *array)
libnnopbase.aclDestroyFloatArray.argtypes = [ctypes.c_void_p]
libnnopbase.aclDestroyFloatArray.restype = ctypes.c_int

# aclBoolArray *aclCreateBoolArray(const bool *value, uint64_t size)
libnnopbase.aclCreateBoolArray.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
libnnopbase.aclCreateBoolArray.restype = ctypes.c_void_p
# aclnnStatus aclDestroyBoolArray(const aclBoolArray *array)
libnnopbase.aclDestroyBoolArray.argtypes = [ctypes.c_void_p]
libnnopbase.aclDestroyBoolArray.restype = ctypes.c_int


class 数组:
    def __init__(self,
                 data: Union[np.ndarray, List[Union[int, float, bool]]],
                 设备索引: Union[int, None] = None):
        self.设备索引 = 0
        设备.初始化目标设备(self, 设备索引)
        data_array: np.ndarray
        # 创建ndarray
        if isinstance(data, list):
            data_array = np.array(data)
        else:
            data_array = data
        # 矫正类型
        self.np_array = data_array
        if data_array.dtype == np.int32:
            data_array = data_array.astype(np.int64)
        elif data_array.dtype == np.float64:
            data_array = data_array.astype(np.float32)
        # 缓存dtype
        self.dtype: int = 将numpy类型转换为acl类型(data_array.dtype)
        self._创建()

    def _创建(self):
        if self.np_array is None:
            return
        # 创建Array
        if self.dtype == acl数据类型.ACL_INT64:
            self.ptr = libnnopbase.aclCreateIntArray(
                self.np_array.ctypes.data, self.np_array.size)
        elif self.dtype == acl数据类型.ACL_FLOAT:
            self.ptr = libnnopbase.aclCreateFloatArray(
                self.np_array.ctypes.data, self.np_array.size)
        elif self.dtype == acl数据类型.ACL_BOOL:
            self.ptr = libnnopbase.aclCreateBoolArray(
                self.np_array.ctypes.data, self.np_array.size)
        else:
            raise Exception(
                "np_array的类型必须是[numpy.int64, numpy.float32, numpy.bool] 的一种, 提供的类型为:" + str(self.np_array.dtype))
        self.np_array = None

    def __del__(self):
        self._销毁()

    def _销毁(self):
        ret: int = 0
        if self.dtype == acl数据类型.ACL_INT64:
            ret = libnnopbase.aclDestroyIntArray(self.ptr)
            记录acl返回值错误日志并抛出异常('libnnopbase.aclDestroyIntArray 错误', ret)
        elif self.dtype == acl数据类型.ACL_FLOAT:
            ret = libnnopbase.aclDestroyFloatArray(self.ptr)
            记录acl返回值错误日志并抛出异常('libnnopbase.aclDestroyFloatArray 错误', ret)
        elif self.dtype == acl数据类型.ACL_BOOL:
            ret = libnnopbase.aclDestroyBoolArray(self.ptr)
            记录acl返回值错误日志并抛出异常('libnnopbase.aclDestroyBoolArray 错误', ret)

    @property
    def 指针(self):
        return self.ptr

    def 切换到设备(self, 设备索引: int):
        if self.设备索引 == 设备索引:
            return self
        self._销毁()
        设备.初始化目标设备(self, 设备索引)
        self._创建()
        return self
