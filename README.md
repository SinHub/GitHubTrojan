# 利用 GitHub 仓库实现的 Python 模块分发器 #
代码以及构想来自《Python 黑帽子: 黑客与渗透测试编程之道》一书第 7 章节：利用 GitHub 的命令和控制。

原书的做法是利用 GitHub 仓库作为一个木马远端控制，木马程序通过 GitHub 交互来实现异步的控制、更新，以及上传被控端数据到 GitHub 仓库。
这里使用 Python 3.6 实现，所幸的是用到第三方库并不多（github3.py、py2exe）而且也算支持 Python3，除了一小部分坑之外几乎完全还原。

相关知识点和代码结构都可以参考 `project.json` 文件。

# 使用 Python 3 的注意事项 #
1. github3.py 中引用了 OpenSSL 模块，其中 OpenSSL 的 _util.py 文件中这一处在 Windows 下会报错，同时也给出了我目前的修改做法。
```
    if PY3:
        def byte_string(s):
            # return s.encode("charmap")    # 报错代码
            return s.encode()               # 修改做法
    else:
        def byte_string(s):
            return s
```
2. 原书代码中 `tree = branch.commit.commit.tree.recurse()` 会提示没有 Attribute recurse，实际上通过调试发现最新的 github3.py 中，`branch.commit.commit.tree` 得到的将会是 `CommitTree` 对象，我们需要调用 `to_tree` 方法才能得到我们要的 `Tree` 对象，所以正确写法是：`tree = branch.commit.commit.tree.to_tree().recurse()`
3. 原书代码中 `exec self.current_module_code in module.__dict__` 没有问题，原因是在 Python2 中 `exec` 实际上是一个 [statement](https://docs.python.org/2.7/reference/simple_stmts.html#the-exec-statement) 而在 Python3 中则是内置 [function](https://docs.python.org/3/library/functions.html#exec)，所以正确的写法是：`exec(self.current_module_code, module.__dict__)`，才能在 `imp` 构造的新模块中加入我们的代码方法。至于为什么会这样，和 Import 机制相关。
