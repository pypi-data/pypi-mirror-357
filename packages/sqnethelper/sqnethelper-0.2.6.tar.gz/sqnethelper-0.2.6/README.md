# 阿里云ECS助手工具

这是一个用于管理阿里云ECS实例的命令行工具。您可以使用此工具列出、停止和删除ECS实例，并设置阿里云凭证和区域。

## 安装

1. 克隆此仓库到本地：

    ```bash
    git clone <repository_url>
    cd sqnethelper
    ```

2. 安装依赖：

    ```bash
    pip install -r requirements.txt
    ```

3. 设置配置文件：

    在 `~/.sqnethelper/config.json` 文件中配置阿里云Access Key、Access Secret和默认区域。

## 使用

### 设置阿里云凭证和区域

运行以下命令来设置阿里云凭证和区域：

```bash
python sqnethelper.py setup
