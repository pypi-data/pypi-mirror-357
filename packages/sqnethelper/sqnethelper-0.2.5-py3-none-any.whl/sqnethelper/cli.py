import click
import json
import asyncio
import threading
from sqnethelper.SqLog import SQLOG, LogLevel
from sqnethelper.SqNetHelper import SqNetHelper
from sqnethelper.ConfigManager import ConfigManager
from sqnethelper.SqUtils import SqUtils
from importlib.metadata import version



SQLOG.set_log_level(LogLevel.INFO)
SQLOG.set_console_output()
# SQLOG.set_websocket_output()

    
SQLOG.info("Hello, SqNetHelper!")

@click.group()
@click.version_option(version=version("sqnethelper"), prog_name="sqnethelper")
def cli():
    pass

@cli.command()
@click.option('--access-key', prompt=True, help='阿里云Access Key')
@click.option('--access-secret', prompt=True, help='阿里云Access Secret')
@click.option('--verbose', is_flag=True, help='打印输出log')
def setup(access_key, access_secret, verbose):
    """设置阿里云账号凭证"""
    if verbose:
        SQLOG.set_log_level(LogLevel.DEBUG)
        pass

    result = SqNetHelper.setup(access_key, access_secret)
    click.echo(result)

    # 重新加载配置
    config = ConfigManager()
    config.load_config()  # 确保重新加载配置
    if not config.is_configured():
        click.echo("Error: 请先设置阿里云凭证!")
        return False

    regions = SqNetHelper.list_regions()
    if not regions:
        click.echo("Error: 获取region列表失败!")
        return False

    region_dict = {region['RegionId']: region['LocalName'] for region in regions}
    output = ["Available regions:"]
    region_choices = []
    for i, (region_id, local_name) in enumerate(region_dict.items(), start=1):
        region_choices.append(region_id)
        output.append(f"{i}. {local_name} ({region_id})")

    click.echo("\n".join(output))
    if region_choices:
        choice = click.prompt("请选择需要操作的region序号：", type=int)
        if choice < 1 or choice > len(region_choices):
            click.echo("Error: 无效选择!")
            return False
        selected_region_id = region_choices[choice - 1]
        result = SqNetHelper.set_region(selected_region_id)
        if result:
            click.echo("设置region: 成功!")
        else:
            click.echo("设置region:{selected_region_id} 失败!")

@cli.command()
@click.option('--region', is_flag=True, help='配置region')
@click.option('--verbose', is_flag=True, help='打印输出log')
def config(region, verbose):
    """修改当前账号的网络配置"""
    if verbose:
        SQLOG.set_log_level(LogLevel.DEBUG)
        pass

    if region:
        config = ConfigManager()
        if not config.is_configured():
            click.echo("Error: 请先设置阿里云凭证!")
            return False

        regions = SqNetHelper.list_regions()
        if not regions:
            click.echo("Error: 获取region列表失败!")
            return False
        
        region_dict = {region['RegionId']: region['LocalName'] for region in regions}
        output = ["Available regions:"]
        region_choices = []
        for i, (region_id, local_name) in enumerate(region_dict.items(), start=1):
            region_choices.append(region_id)
            output.append(f"{i}. {local_name} ({region_id})")

        click.echo("\n".join(output))
        if region_choices:
            choice = click.prompt("请选择需要操作的region序号：", type=int)
            if choice < 1 or choice > len(region_choices):
                click.echo("Error: 无效选择!")
                return False
            selected_region_id = region_choices[choice - 1]
            result = SqNetHelper.set_region(selected_region_id)
            if result:
                SQLOG.info(f"设置region: {selected_region_id}成功!")
            else:
                SQLOG.info("设置region:{selected_region_id} 失败!")


@cli.command()
@click.option('--verbose', is_flag=True, help='打印输出log')
def list(verbose):
    """列出所有网络服务器"""
    if verbose:
        SQLOG.set_log_level(LogLevel.DEBUG)
        pass

    config = ConfigManager()
    if not config.is_configured():
        click.echo("Error: 请先设置阿里云凭证!")
        return False
    instance_array = SqNetHelper.list_instances()
    SQLOG.great("创建的虚拟机列表:")
    # SQLOG.info(f"共有{len(instance_array)}个虚拟机!")
    if len(instance_array) > 0:
        i = 1
        for instance in instance_array:
            SQLOG.great(f"{i}. ID: {instance['InstanceId']}, 名称: {instance['Name']}, IP: {instance['PublicIpAddress']}, 状态: {instance['Status']}, 释放时间:{instance['AutoReleaseTime']}")
            i += 1

    return True


@cli.command()
@click.option('--verbose', is_flag=True, help='打印输出log')
def create(verbose):
    """修改当前账号的网络配置"""
    if verbose:
        SQLOG.set_log_level(LogLevel.DEBUG)
        pass
    config = ConfigManager()
    if not config.is_configured():
        click.echo("Error: 请先设置阿里云凭证!")
        return False
    
    instance_details = SqNetHelper.create_instance(config)
    
    if instance_details and instance_details.get('InstanceId'):
        instance_id = instance_details.get('InstanceId')
        # SqNetHelper.install_singbox_protocol(config, instance_id, 'reality', 443)
        # SqNetHelper.install_xray_protocol(config, instance_id, 'reality', 5432)
        SqNetHelper.install_xray_protocol(config, instance_id, 'tcp', 3000)
        # SqNetHelper.install_singbox_protocol(config, instance_id, 'ss', 80)
    else:
        SQLOG.error("创建实例失败!")

@cli.command()
@click.option('--verbose', is_flag=True, help='打印输出log')
def autodel(verbose):
    """修改远程虚拟机自动释放的时间"""
    if verbose:
        SQLOG.set_log_level(LogLevel.DEBUG)
        pass
    
    config = ConfigManager()
    if not config.is_configured():
        click.echo("Error: 请先设置阿里云凭证!")
        return False

    instance_array = SqNetHelper.list_instances()
    SQLOG.great("创建的虚拟机列表:")
    # SQLOG.info(f"共有{len(instance_array)}个虚拟机!")
    if len(instance_array) > 0:
        i = 1
        for instance in instance_array:
            SQLOG.great(f"{i}. ID: {instance['InstanceId']}, 名称: {instance['Name']}, IP: {instance['PublicIpAddress']}, 状态: {instance['Status']}, 释放时间:{instance['AutoReleaseTime']}")
            i += 1


        SQLOG.great(f"请输入需要销毁的虚拟机序号:")
        choice = click.prompt("", type=int)

        if choice < 1 or choice > len(instance_array):
            SQLOG.error("错误: 无效选择!")
            return False
        else:
            instance_id = instance_array[choice - 1]['InstanceId']
            SQLOG.great(f"请输入自动师傅删除的时间间隔(分钟),大于 5分钟:")
            time_min_delay = click.prompt("", type=int)
            result = SqNetHelper.modify_auto_release_time(config, instance_id, time_min_delay)
            if result:
                SQLOG.great(f"远程虚拟机{instance_id}将在{time_min_delay}分钟后自动释放")
            else:
                SQLOG.great(f"远程虚拟机{instance_id}设置自动释放时间失败!")
            
            
@cli.command()
@click.option('--verbose', is_flag=True, help='打印输出log')
def delete(verbose):
    """删除网络服务器"""
    if verbose:
        SQLOG.set_log_level(LogLevel.DEBUG)
        pass

    config = ConfigManager()
    if not config.is_configured():
        click.echo("Error: 请先设置阿里云凭证!")
        return False
    instance_array = SqNetHelper.list_instances()
    SQLOG.great("创建的虚拟机列表:")
    # SQLOG.info(f"共有{len(instance_array)}个虚拟机!")
    if len(instance_array) > 0:
        i = 1
        for instance in instance_array:
            SQLOG.great(f"{i}. ID: {instance['InstanceId']}, 名称: {instance['Name']}, IP: {instance['PublicIpAddress']}, 状态: {instance['Status']}, 释放时间:{instance['AutoReleaseTime']}")
            i += 1


        SQLOG.great(f"请输入需要销毁的虚拟机序号:")
        choice = click.prompt("", type=int)

        if choice < 1 or choice > len(instance_array):
            SQLOG.error("错误: 无效选择!")
            return False
        else:
            instance_id = instance_array[choice - 1]['InstanceId']
            SQLOG.info(f"正在销毁虚拟机: {instance_id}")
            result = SqNetHelper.confirm_delete_instance(instance_id)
            if result:
                SQLOG.info(f"销毁虚拟机: {instance_id} 成功!")
            else:
                SQLOG.error(f"销毁虚拟机: {instance_id} 失败!")


@cli.command()
@click.option('--verbose', is_flag=True, help='打印输出log')
def addvpn(verbose):
    """安装vpn协议"""
    if verbose:
        SQLOG.set_log_level(LogLevel.DEBUG)
        pass

    config = ConfigManager()
    if not config.is_configured():
        click.echo("Error: 请先设置阿里云凭证!")
        return False
    instance_array = SqNetHelper.list_instances()
    SQLOG.great("创建的虚拟机列表:")
    # SQLOG.info(f"共有{len(instance_array)}个虚拟机!")
    if len(instance_array) > 0:
        i = 1
        for instance in instance_array:
            SQLOG.great(f"{i}. ID: {instance['InstanceId']}, 名称: {instance['Name']}, IP: {instance['PublicIpAddress']}, 状态: {instance['Status']}, 释放时间:{instance['AutoReleaseTime']}")
            i += 1

        SQLOG.great(f"请输入需要操作的虚拟机序号:")
        choice = click.prompt("", type=int)

        if choice < 1 or choice > len(instance_array):
            SQLOG.error("错误: 无效选择!")
            return False
        else:
            instance_id = instance_array[choice - 1]['InstanceId']
            SqNetHelper.install_ipsec_vpn(config, instance_id)
            # SqNetHelper.install_xray_protocol(config, instance_id, 'tcp', 3000)
            # SqNetHelper.install_xray_protocol(config, instance_id, 'reality', 5432)
            

                
# @cli.command()
# def delete_all():
#     """删除当前所有资源"""

if __name__ == '__main__':
    cli()



# # 主程序示例
# if __name__ == "__main__":
#     SQLOG.set_console_output()
#     SQLOG.set_websocket_output()

#     # 模拟定期发送消息
#     async def send_periodic_message():
#         while True:
#             await asyncio.sleep(5)
#             SQLOG.info("Periodic message")

#     # 运行WebSocket服务器和定期发送消息
#     loop = asyncio.get_event_loop()
#     loop.create_task(send_periodic_message())
#     loop.run_forever()



