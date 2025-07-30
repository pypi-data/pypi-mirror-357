## 📦 `live_studio_open_service`

一个轻量级 Python 客户端，用于通过 TCP 协议与LIVE Studio进行交互。

---

### ✅ 安装方式

你可以使用 pip 安装（发布到 PyPI 后）：

```bash
pip install live_studio_open_service
```

---

### 🚀 快速上手

#### 示例一：使用默认地址

```python
from live_studio_open_service import call

result = call("say_hello", ["world"])
print("结果:", result)
```

默认连接到 `127.0.0.1:60080`。

#### 示例二：指定服务器地址和端口

```python
from live_studio_open_service import call

result = call("say_hello", ["world"], host="10.71.157.126", port=60080)
print("结果:", result)
```

---

### ⚙️ 接口说明

```python
call(
    name: str,
    args: list[str],
    host: str = "127.0.0.1",
    port: int = 60080,
    timeout: float = 5.0
) -> Any
```

| 参数        | 类型          | 说明            |
| --------- | ----------- | ------------- |
| `name`    | `str`       | 远程调用的方法名      |
| `args`    | `list[str]` | 传入参数列表（字符串数组） |
| `host`    | `str`       | 目标服务器地址（可选）   |
| `port`    | `int`       | 目标服务器端口（可选）   |
| `timeout` | `float`     | 超时时间（单位秒）     |

---

### 💡 返回值说明

函数返回远程调用返回的内容。如果网络错误或服务器未响应，将抛出 `RuntimeError`。

---

### 📄 协议约定

* 通信协议基于 TCP。
* 消息采用 JSON 格式，末尾使用 `\f` 分隔。
* 请求结构：

```json
{
  "type": "call",
  "id": "timestamp_method",
  "data": {
    "type": "serviceMethod",
    "name": "method_name",
    "args": ["arg1", "arg2"]
  }
}
```

---

### 🛠 开发测试

```bash
# 构建包
python -m build

# 上传到测试 PyPI
twine upload --repository testpypi dist/*
```

---
