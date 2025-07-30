
import time
import json
import base64
import paramiko
from sqnethelper.SqLog import SQLOG
from pathlib import Path
import os

# 检查文件是否存在


# 这里假设 ~/.ssh/id_rsa.pub 是在用户的主目录下
# 如果是在其他目录下，可以根据实际情况调整文件路径


class ShellHelper:

    @staticmethod
    def get_local_ssh_key_content(key_name = 'id_rsa'):        
        public_key_name = key_name + '.pub'
        private_key_path = Path.home() / '.ssh' / key_name
        public_key_path = Path.home() / '.ssh' / public_key_name
            
        if not private_key_path.exists():
            # 如果文件存在，读取内容
            ShellHelper.create_local_ssh_key(key_name)
        
        if private_key_path.exists():
            with open(public_key_path, 'r') as file:
                content = file.read()
                return str(private_key_path), content
        else:
            return None, None
             
    @staticmethod
    def create_local_ssh_key(key_name = 'id_rsa'):
        public_key_name = key_name + '.pub'
        private_key_path = Path.home() / '.ssh' / key_name
        public_key_path = Path.home() / '.ssh' / public_key_name
        if not private_key_path.exists():
            key = paramiko.RSAKey.generate(bits=2048)
            # 保存私钥
            key.write_private_key_file(private_key_path)
            # 保存公钥
            with open(public_key_path, 'w') as f:
                f.write(f'{key.get_name()} {key.get_base64()}')
                f.close()
                
        
    @staticmethod
    def ssh_connect_and_execute_with_password(hostname, username, password, command, verbose=False):
        # 创建 SSH 客户端对象
        client = paramiko.SSHClient()
        
        # 设置自动添加主机密钥策略
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        result = False
        try:
            # 连接到远程服务器
            client.connect(hostname=hostname, username=username, password=password)
            SQLOG.debug(f"成功连接到 {hostname}")

            # 执行命令
            time.sleep(1)
            stdin, stdout, stderr = client.exec_command(command)
            
            # 实时输出结果
            while True:
                line = stdout.readline()
                if not line:
                    break
                if verbose:
                    SQLOG.debug(line, end='')
            
            # 输出错误信息（如果有）
            if verbose:
                for line in stderr:
                    SQLOG.debug(line, end='')

            # 获取命令执行的返回码
            exit_status = stdout.channel.recv_exit_status()
            if exit_status == 0:
                SQLOG.debug("命令执行成功")
                result = True
            else:
                SQLOG.debug(f"命令执行失败，退出状态码：{exit_status}")
                result = False
                
            return result;
        except paramiko.AuthenticationException:
            SQLOG.debug("认证失败，请检查你的用户名和密码")
        except paramiko.SSHException as ssh_exception:
            SQLOG.debug(f"SSH连接失败: {str(ssh_exception)}")
        finally:
            # 关闭连接
            client.close()
            return result

    @staticmethod
    def ssh_download_file_with_password(hostname, username, password, remote_file_path, local_file_path):
        # 创建SSH客户端对象
        ssh_client = paramiko.SSHClient()
        
        # 设置自动添加主机密钥策略
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        result = None
        try:
            # 连接到远程服务器
            ssh_client.connect(hostname=hostname, username=username, password=password)
            SQLOG.debug(f"成功连接到 {hostname}")
            # 创建SFTP客户端对象
            sftp_client = ssh_client.open_sftp()
            # 下载文件
            sftp_client.get(remote_file_path, local_file_path)
            result = local_file_path
            SQLOG.debug(f"文件成功下载到: {local_file_path}")

        except paramiko.AuthenticationException:
            SQLOG.debug("认证失败，请检查你的用户名和密码")
        except paramiko.SSHException as ssh_exception:
            SQLOG.debug(f"SSH连接失败: {str(ssh_exception)}")
        except IOError as io_error:
            SQLOG.debug(f"文件传输错误: {str(io_error)}")
        finally:
            # 关闭SFTP连接
            if 'sftp_client' in locals():
                sftp_client.close()
            # 关闭SSH连接
            ssh_client.close()
            return result 

    @staticmethod
    def ssh_connect_and_execute_with_key(hostname, username, private_key_path, command, verbose=False):
        # 创建 SSH 客户端对象
        time.sleep(5)
        client = paramiko.SSHClient()
        
        # 设置自动添加主机密钥策略
        time.sleep(5)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        result = False
        try:
            # 连接到远程服务器
            SQLOG.debug(f"尝试连接到 {hostname} 使用用户名 {username} 和密钥 {private_key_path}")
            time.sleep(10)
            client.connect(hostname=hostname, username=username, key_filename=private_key_path)
            SQLOG.debug(f"成功连接到 {hostname}")
            time.sleep(3)
            # 执行命令
            SQLOG.debug(f"执行命令: {command}")
            stdin, stdout, stderr = client.exec_command(command)
            
            # 实时输出结果
            if verbose:
                while True:
                    line = stdout.readline()
                    if not line:
                        break
                    SQLOG.debug(line.strip())
            
            # 输出错误信息（如果有）
            # if verbose:
            for line in stderr:
                SQLOG.error(line.strip())

            # 获取命令执行的返回码
            exit_status = stdout.channel.recv_exit_status()
            if exit_status == 0:
                result = True
                SQLOG.debug(f"命令 {command} 执行成功")
            else:
                SQLOG.debug(f"命令执行失败，退出状态码：{exit_status}")
                result = False

        except paramiko.AuthenticationException:
            SQLOG.debug("认证失败，请检查你的用户名和密钥")
        except paramiko.SSHException as ssh_exception:
            SQLOG.debug(f"SSH连接失败: {str(ssh_exception)}")
        except Exception as e:
            SQLOG.debug(f"出现未知错误: {str(e)}")
        finally:
            # 延迟一会再关闭连接
            time.sleep(1)
            client.close()
            SQLOG.debug(f"关闭与 {hostname} 的连接")
        
        return result

    @staticmethod
    def ssh_download_file_with_key(hostname, username, private_key_path, remote_file_path, local_file_path):
        # 创建SSH客户端对象
        ssh_client = paramiko.SSHClient()
        
        # 设置自动添加主机密钥策略
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        result = None
        try:
            # 连接到远程服务器
            ssh_client.connect(hostname=hostname, username=username, key_filename=private_key_path)
            SQLOG.debug(f"成功连接到 {hostname}")

            # 创建SFTP客户端对象
            sftp_client = ssh_client.open_sftp()
            
            # 下载文件
            sftp_client.get(remote_file_path, local_file_path)
            
            SQLOG.debug(f"文件成功下载到: {local_file_path}")
            result = local_file_path
        except paramiko.AuthenticationException:
            SQLOG.debug("认证失败，请检查你的用户名和密钥")
        except paramiko.SSHException as ssh_exception:
            SQLOG.debug(f"SSH连接失败: {str(ssh_exception)}")
        except IOError as io_error:
            SQLOG.debug(f"文件传输错误: {str(io_error)}")
        finally:
            # 关闭SFTP连接
            if 'sftp_client' in locals():
                sftp_client.close()
            # 关闭SSH连接
            ssh_client.close()
            return result

