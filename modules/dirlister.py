# coding: utf-8
'''
定义 run 函数并提供可变数量的参数，好处有二：
1. 可以使用相同的方法加载模块，使接口更通用
2. 提供了充分的可扩展能力，在需要的时候通过定制配置文件提供不同的参数，从而完成不同的任务
'''
import os


def run(**args):
    print("[*] In dirlister module.")
    files = os.listdir(".")

    return str(files)
