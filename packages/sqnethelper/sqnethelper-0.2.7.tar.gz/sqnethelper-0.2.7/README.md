# sqnethelper - 阿里云ECS助手工具

这是一个用于管理阿里云ECS实例的命令行工具。您可以使用此工具快速创建、管理ECS实例，自动安装VPN协议，并生成SingBox客户端配置。

## ✨ 主要功能

- 🚀 **一键创建ECS实例**：自动创建、配置网络和安全组
- 🔒 **多协议VPN支持**：支持Reality、VMess、Shadowsocks等协议
- 📱 **SingBox配置生成**：自动生成完整的SingBox客户端配置文件
- ⏰ **自动释放管理**：设置实例自动销毁时间，避免忘记关机
- 🔧 **SSH密钥管理**：自动创建和管理SSH密钥对

## 📦 安装方式

### 方式一：使用pipx安装（推荐 - macOS）

pipx是安装Python命令行工具的最佳方式，它会为每个工具创建独立的虚拟环境。

#### 1. 安装pipx

```bash
# 使用Homebrew安装pipx（推荐）
brew install pipx

# 或者使用pip安装
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

#### 2. 使用pipx安装sqnethelper

```bash
pipx install sqnethelper
```

#### 3. 验证安装

```bash
sqnethelper --version
```

#### 4. pipx管理命令

```bash
# 升级到最新版本
pipx upgrade sqnethelper

# 强制重新安装
pipx install --force sqnethelper

# 卸载
pipx uninstall sqnethelper

# 查看已安装的包
pipx list
```

### 方式二：使用pip安装

#### 在虚拟环境中安装（推荐）

```bash
# 创建虚拟环境
python3 -m venv sqnethelper-env
source sqnethelper-env/bin/activate

# 安装sqnethelper
pip install sqnethelper
```

#### 用户级安装

```bash
pip install --user sqnethelper
```

### 方式三：从源码安装

```bash
git clone https://github.com/weishq/sqnethelper.git
cd sqnethelper
pip install -e .
```

## 🚀 快速开始

### 1. 设置阿里云凭证

首次使用需要配置阿里云Access Key和Secret：

```bash
sqnethelper setup
```

按提示输入您的阿里云Access Key和Secret。如果您还没有，请访问 [阿里云控制台](https://ram.console.aliyun.com/manage/ak) 创建。

### 2. 一键创建VPN服务器

```bash
sqnethelper create
```

这个命令会：
- 自动创建ECS实例（默认1小时后自动销毁）
- 配置安全组和网络
- 安装Xray VPN协议
- 生成SingBox客户端配置文件

### 3. 查看现有实例

```bash
sqnethelper list
```

## 📋 命令参考

### 基础命令

```bash
# 查看帮助
sqnethelper --help

# 查看版本
sqnethelper --version

# 设置阿里云凭证
sqnethelper setup

# 查看/修改配置
sqnethelper config
sqnethelper config --region  # 修改区域设置
```

### 实例管理

```bash
# 创建新实例（自动安装VPN）
sqnethelper create

# 列出所有实例
sqnethelper list

# 修改自动释放时间
sqnethelper autodel

# 删除实例
sqnethelper delete
```

### VPN管理

```bash
# 为现有实例添加VPN协议
sqnethelper addvpn
```

支持的VPN协议：
- **Reality**: 最新的抗审查协议
- **Xray TCP**: 轻量级TCP协议  
- **Xray Reality**: Reality协议的Xray实现
- **SingBox SS**: Shadowsocks协议
- **SingBox Reality**: Reality协议的SingBox实现

## 📱 SingBox客户端配置

每次安装VPN后，sqnethelper会自动：

1. 显示协议配置信息
2. 生成SingBox客户端配置
3. 在工作目录保存完整配置文件（格式：`sing-box_config_{protocol}_{port}_{timestamp}.json`）

### 使用配置文件

1. 将生成的JSON配置文件导入SingBox客户端
2. 或者复制outbounds部分到您现有的SingBox配置中

### 配置文件特点

- 🌐 智能分流：中国网站直连，国外网站代理
- 🔒 DNS安全：国内外DNS分离
- ⚡ 性能优化：启用缓存和连接复用
- 🛡️ 隐私保护：防DNS泄露

## ⚠️ 注意事项

### 安全建议

- 定期更换Access Key
- 使用RAM子账号，不要使用主账号
- 及时删除不用的实例，避免产生费用

### 成本控制

- 创建的实例默认1小时后自动销毁
- 可使用`sqnethelper autodel`命令修改自动销毁时间
- 建议设置阿里云账单提醒

### 网络说明

- 默认创建的安全组只开放必要端口
- 自动配置防火墙规则
- 支持多种VPN协议和端口

## 🔧 高级配置

### 自定义配置

配置文件位置：`~/.sqnethelper/config.json`

主要配置项：
```json
{
  "access_key": "您的AccessKey",
  "access_secret": "您的AccessSecret", 
  "region": "地域ID",
  "instance_type": "实例规格",
  "instance_login_password": "登录密码",
  "xray_tcp_port": 3000,
  "xray_reality_port": 443,
  "singbox_ss_port": 8080,
  "singbox_reality_port": 443
}
```

### VPN端口配置

可以在配置文件中自定义各协议的默认端口，或在安装时手动指定端口。

## 🆘 故障排除

### 常见问题

**Q: 提示"externally-managed-environment"错误？**
A: 这是Python环境保护机制，建议使用pipx安装：`pipx install sqnethelper`

**Q: 无法连接阿里云API？**
A: 检查网络连接和Access Key是否正确，确认已开通ECS服务权限

**Q: VPN安装失败？**
A: 检查实例状态是否为Running，安全组规则是否正确配置

**Q: SingBox配置无法连接？**
A: 确认服务器IP、端口、协议参数是否正确，检查本地网络和防火墙设置

### 日志调试

使用`--verbose`参数查看详细日志：

```bash
sqnethelper create --verbose
sqnethelper list --verbose
