
import time
import os
from pathlib import Path
from datetime import datetime, timedelta
from sqnethelper.ECSManager import ECSManager
from sqnethelper.VPCManager import VPCManager
from sqnethelper.ConfigManager import ConfigManager
from sqnethelper.ShellHelper import ShellHelper
from sqnethelper.SqLog import SQLOG


class SqNetHelper:

    @staticmethod
    def setup(access_key, access_secret):
        config = ConfigManager()
        config.set_config(
            access_key=access_key,
            access_secret=access_secret
        )
        return "配置已保存"

    @staticmethod
    def list_instances():
        config = ConfigManager()
        if not config.is_configured():
            SQLOG.error(f"请先设置阿里云凭证!")
            return None
        ecs_manager = ECSManager(config.access_key, config.access_secret, config.region)
        instances_result = ecs_manager.list_instances()
        return instances_result

    @staticmethod
    def list_regions():
        config = ConfigManager()
        if not config.is_configured():
            SQLOG.error(f"请先设置阿里云凭证!")
            return None
        ecs_manager = ECSManager(config.access_key, config.access_secret, config.region)
        return ecs_manager.get_regions()



    @staticmethod
    def set_region(selected_region_id):

        config = ConfigManager()
        config.set_config(
            region=selected_region_id
        )

        ecs_manager = ECSManager(config.access_key, config.access_secret, config.region)
        zones = ecs_manager.get_zones()
        zone_id = zones[0]['ZoneId']
        config.set_config(
            zone_id=zone_id
        )

        SQLOG.info(f"地区: {config.region}")
        SQLOG.info(f"可用区: {zone_id}")

        vpcmanager = VPCManager(config.access_key, config.access_secret, config.region)

        instance_type_info = vpcmanager.get_available_instance_types_with_price(zone_id=zone_id, cpu_count = config.instance_cpu_count, memory_size = config.instance_memory_size)
        if len(instance_type_info) >0   :
            instance_type = instance_type_info[0][0]
            config.set_config(
                instance_type=instance_type
            )

        SQLOG.info(f"创建虚拟机实例规格为: {config.instance_type}")

        disks_resources = vpcmanager.get_available_disk_categories(zone_id=zone_id, insance_type=config.instance_type)
        disk_types = ["cloud_efficiency", "cloud_essd_entry", "cloud_ssd", "cloud_essd"]
        disk_sure = False
        for disk_type in disk_types:
            for item in disks_resources:
                if item["Value"] == disk_type and item["Status"] == "Available":
                    disk_sure = True
                    config.set_config(
                        instance_disk_category=item["Value"],
                        instance_disk_size= max(item["Min"],20)
                    )
                    break  # 找到符合条件的就退出内层循环
            if disk_sure:  # 如果已经设置了磁盘类型，就退出外层循环
                break
        SQLOG.info(f"创建虚拟机磁盘类型为: {config.instance_disk_category}, 磁盘大小为: {config.instance_disk_size}")
       
        security_group_id = None
        vpc_id = None
        vswitch_id = None
        
        # 检查阿里云是否已存在密钥对
        key_name = vpcmanager.is_key_pair_exist_with_name("sqssh-")
        if key_name:
            user_home = os.path.expanduser('~')
            private_key_path = os.path.join(user_home, '.ssh', 'id_rsa')  
            config.set_config(
                ssh_keypair_name=key_name,
                ssh_local_path=private_key_path
            )
            SQLOG.info("云端已存在SSH密钥对: ", key_name)
        else:
            # 获取或创建本机SSH密钥
            private_key_path, content = ShellHelper.get_local_ssh_key_content()
            if private_key_path and content:
                time_str = time.strftime('%m%d-%H-%M-%S', time.localtime())
                key_name = f"sqssh-{time_str}"
                key_name = vpcmanager.import_ssh_key(key_name, content)
                if key_name:
                    config.set_config(
                        ssh_keypair_name=key_name,
                        ssh_local_path=private_key_path
                    )
                    SQLOG.info("✅ SSH密钥对上传成功: ", key_name)
                    SQLOG.info(f"   本地私钥: {private_key_path}")
                else:
                    SQLOG.error("❌ SSH密钥对上传失败")
            else:
                SQLOG.error("❌ 获取本机SSH密钥失败")
        
        
        if vpcmanager.is_security_group_exist(config.security_group_id):
            security_group_id = config.security_group_id
            SQLOG.info("已存在安全组: ", security_group_id)
            pass
        else:
            security_group_id = vpcmanager.is_security_group_exist_with_name(config.security_group_name)
            if security_group_id:
                SQLOG.info("已存在安全组: ", security_group_id)

        if security_group_id:
            vpc_id = vpcmanager.get_vpc_id_by_security_group_id(security_group_id)
            if vpc_id:
                SQLOG.info("已存在专有网络: ", vpc_id)
                vswitch_id = vpcmanager.get_vswitche_id_by_vpc_id(vpc_id)
                if vswitch_id:
                    SQLOG.info("已存在虚拟交换机: ", vswitch_id)
                else:
                    vswitch_id = vpcmanager.create_vswitch(vpc_id, zone_id) 
                    SQLOG.info("创建虚拟交换机成功: ", vswitch_id)

        if security_group_id and vpc_id and vswitch_id:
            pass 
        else:
            vpc_id = vpcmanager.is_vpc_exist_with_name(config.vpc_name)
            if not vpc_id:
                vpc_id = vpcmanager.create_vpc()
            if not vpc_id:
                SQLOG.info("创建专有网络失败！")
                return False

            SQLOG.info("创建专有网络成功: ", vpc_id)
            time.sleep(5)
            vswitch_id = vpcmanager.get_vswitche_id_by_vpc_id(vpc_id)
            if not vswitch_id:
                vswitch_id = vpcmanager.create_vswitch(vpc_id, zone_id) 
                pass
            if not vpc_id:
                SQLOG.info("创建虚拟交换机失败！")
                return False  

            SQLOG.info("创建虚拟交换机成功: ", vswitch_id)  
            security_group_id = vpcmanager.create_security_group(vpc_id)
            if not security_group_id:
                SQLOG.info("创建安全组失败！")
                return False
            SQLOG.info("创建安全组成功: ", security_group_id)

        if security_group_id:
            vpcmanager.add_security_group_rule(security_group_id, config)
                
        if security_group_id and vpc_id and vswitch_id:
            config.set_config(
                security_group_id=security_group_id,
                vpc_id=vpc_id,
                vswitch_id=vswitch_id
            )
            pass

         
        return True

    @staticmethod
    def create_instance(config):

        ecs_manager = ECSManager(config.access_key, config.access_secret, config.region)
        instance_details = ecs_manager.create_instance(config)
        if instance_details is None:
            SQLOG.debug("创建实例失败")
            return None
            
        instance_id = instance_details['InstanceId']
        if instance_id is None:
            SQLOG.debug("创建实例失败!")
            return None
        SQLOG.info("创建虚拟机成功: ", instance_id)
        time.sleep(2) 
        
        # ECS绑定密码
        ret = ecs_manager.reset_instance_password(instance_id, config.instance_login_password)
        if not ret:
            SQLOG.debug("设置实例密码失败")
            return None
        
        SQLOG.debug("设置实例密码成功!")
        ssh_attach_ret = False
        if config.ssh_keypair_name:
            vpcmanager = VPCManager(config.access_key, config.access_secret, config.region)
            if vpcmanager.is_key_pair_exist(config.ssh_keypair_name):
                ssh_attach_ret = ecs_manager.attach_key_pair(instance_id, config.ssh_keypair_name)
                if ssh_attach_ret :
                    SQLOG.debug("绑定ssh成功")
                    ssh_attach_ret = True
                    pass
                
        # 分配公网 IP
        hostname = ecs_manager.allocate_public_ip(instance_id)
        if hostname is None:
            SQLOG.error("分配公网 IP 失败")
            return None
        SQLOG.info(f"分配公网IP成功: {hostname}")
        # 启动 ECS 实例
        ecs_manager.start_instance(instance_id)
        # 等待实例状态为 Running
        ecs_manager.wait_instance_status(instance_id, 'Running')
        
        #1小时后自动释放
        SqNetHelper.modify_auto_release_time(config, instance_id, 60)
        return instance_details
        
    @staticmethod
    def confirm_delete_instance(instance_id):
        config = ConfigManager()
        ecs_manager = ECSManager(config.access_key, config.access_secret, config.region)
        return ecs_manager.delete_instance(instance_id)
    
    @staticmethod
    def modify_auto_release_time(config, instance_id, time_min_delay):
        # 计算UTC时间：当前UTC时间 + 指定分钟数
        from datetime import datetime, timedelta, timezone
        utc_now = datetime.now(timezone.utc)
        auto_release_time = (utc_now + timedelta(minutes=time_min_delay)).strftime('%Y-%m-%dT%H:%M:%SZ')
        SQLOG.info(f"设置自动释放时间(UTC): {auto_release_time}")
        ecs_manager = ECSManager(config.access_key, config.access_secret, config.region)
        return ecs_manager.modify_instance_auto_release_time(instance_id, auto_release_time)
        
    

    @staticmethod
    def install_ipsec_vpn(config, instance_id):
        SQLOG.info(f"正在安装 ipsec vpn ...")
        ecs_manager = ECSManager(config.access_key, config.access_secret, config.region)
        # 执行shell脚本
        shell_script = """
        #!/bin/bash
        
        wget https://get.vpnsetup.net -O vpn.sh && sudo VPN_IPSEC_PSK='{VPN_IPSEC_PSK}' VPN_USER='{VPN_USER}' VPN_PASSWORD='{VPN_PASSWORD}' bash vpn.sh
        
        """.format(VPN_IPSEC_PSK='greatpsk', VPN_USER='greatvpn', VPN_PASSWORD='greatpass')
        command_response = ecs_manager.run_command(instance_id, shell_script)
        invoke_id = command_response['InvokeId']
        res_details = ecs_manager.describe_invocation_results(instance_id, invoke_id, 100, 6)
        res_info = ecs_manager.base64_decode(res_details.get("Output",""))
        
        SQLOG.info(res_info)
            
    @staticmethod
    def install_singbox_protocol(config, instance_id, protocol, port):
        SQLOG.info(f"正在安装 {protocol}协议, 端口 {port}...")
        
        # 先添加防火墙端口规则
        vpcmanager = VPCManager(config.access_key, config.access_secret, config.region)
        if config.security_group_id:
            vpcmanager.add_vpn_port_rule(config.security_group_id, port)
        
        ecs_manager = ECSManager(config.access_key, config.access_secret, config.region)
        # 执行shell脚本
        shell_script = """
        #!/bin/bash
        if ! command -v sing-box &> /dev/null; then
            wget -qO- https://github.com/233boy/sing-box/raw/main/install.sh | bash > /dev/null 2>&1
        fi
        
        sb change {protocol} port {port}
        
        if ! command -v qrencode &> /dev/null; then
            sudo apt-get update -y > /dev/null 2>&1
            sudo apt-get install qrencode -y --quiet > /dev/null 2>&1
        fi
        sb qr {protocol}-{port}
        """.format(protocol=protocol, port=port)
        command_response = ecs_manager.run_command(instance_id, shell_script)
        invoke_id = command_response['InvokeId']
        res_details = ecs_manager.describe_invocation_results(instance_id, invoke_id, 100, 6)
        res_info = ecs_manager.base64_decode(res_details.get("Output",""))
        SQLOG.info(res_info)
        
        # 生成SingBox配置
        SqNetHelper.generate_and_display_singbox_config(config, instance_id, protocol, port, res_info)
        
    @staticmethod
    def install_xray_protocol(config, instance_id, protocol, port):
        SQLOG.info(f"正在安装 {protocol}协议, 端口 {port}...")
        
        # 先添加防火墙端口规则
        vpcmanager = VPCManager(config.access_key, config.access_secret, config.region)
        if config.security_group_id:
            vpcmanager.add_vpn_port_rule(config.security_group_id, port)
        
        ecs_manager = ECSManager(config.access_key, config.access_secret, config.region)
        # 执行shell脚本
        shell_script = """
        #!/bin/bash
        echo "🔧 开始安装Xray {protocol}协议，端口 {port}..."
        
        # 设置UTF-8环境变量
        if [ ! -f ~/.bashrc ]; then
            echo 'export LC_CTYPE=en_US.UTF-8' >> ~/.bashrc
            echo 'export LC_ALL=en_US.UTF-8' >> ~/.bashrc
            echo 'export LANG=en_US.UTF-8' >> ~/.bashrc
        fi
        source ~/.bashrc
        
        # 检查并安装Xray
        if ! command -v xray &> /dev/null; then
            echo "📥 正在下载和安装Xray..."
            wget -qO- https://github.com/233boy/Xray/raw/main/install.sh | bash
            echo "🗑️ 清理默认Reality配置..."
            xray del reality > /dev/null 2>&1 || true
        else
            echo "✅ Xray已安装"
        fi
        
        echo "⚙️ 配置Xray {protocol}协议..."
        xray add {protocol} {port}
        
        # 安装二维码工具
        if ! command -v qrencode &> /dev/null; then
            echo "📦 安装二维码生成工具..."
            sudo apt-get update -y > /dev/null 2>&1
            sudo apt-get install qrencode -y --quiet > /dev/null 2>&1
        fi
        
        echo "📱 生成二维码..."
        xray qr {protocol}-{port}
        
        echo "🎉 Xray {protocol}协议安装完成!"
        """.format(protocol=protocol, port=port)
        command_response = ecs_manager.run_command(instance_id, shell_script)
        invoke_id = command_response['InvokeId']
        res_details = ecs_manager.describe_invocation_results(instance_id, invoke_id, 100, 6)
        res_info = ecs_manager.base64_decode(res_details.get("Output",""))
        SQLOG.info(res_info)
        
        # 生成SingBox配置
        SqNetHelper.generate_and_display_singbox_config(config, instance_id, protocol, port, res_info)
    
    @staticmethod
    def get_instance_public_ip(config, instance_id):
        """获取实例的公网IP地址"""
        ecs_manager = ECSManager(config.access_key, config.access_secret, config.region)
        instance_array = ecs_manager.list_instances()
        for instance in instance_array:
            if instance['InstanceId'] == instance_id:
                return instance.get('PublicIpAddress', '')
        return None
    
    @staticmethod
    def generate_and_display_singbox_config(config, instance_id, protocol, port, vpn_output):
        """生成并显示SingBox客户端配置"""
        from sqnethelper.SqUtils import SqUtils
        
        # 获取实例的公网IP
        server_ip = SqNetHelper.get_instance_public_ip(config, instance_id)
        if not server_ip:
            SQLOG.error("❌ 无法获取服务器IP地址，跳过SingBox配置生成")
            return
        
        # 生成SingBox配置
        singbox_config = SqUtils.parse_vpn_output_and_generate_singbox_config(
            vpn_output, server_ip, protocol, port
        )
        
        if singbox_config:
            SQLOG.great("🔧 SingBox客户端配置:")
            SQLOG.great("=" * 60)
            formatted_config = SqUtils.format_singbox_config_output(singbox_config)
            
            # 按行输出配置，以便正确显示
            for line in formatted_config.split('\n'):
                SQLOG.info(line)
            
            SQLOG.great("=" * 60)
            SQLOG.info("💡 将上述配置复制到SingBox客户端的outbounds部分")
            
            # 生成完整的SingBox配置文件
            SqNetHelper.generate_complete_singbox_config(singbox_config, server_ip, protocol, port)
        else:
            SQLOG.error("❌ 无法生成SingBox配置")
    
    @staticmethod
    def generate_complete_singbox_config(outbound_config, server_ip, protocol, port):
        """生成完整的SingBox配置文件并保存到工作目录"""
        import json
        import os
        from datetime import datetime
        
        try:
            # 读取模板文件
            from sqnethelper.resources import load_template
            template_config = load_template()
            
            # 获取新的outbound配置
            new_outbound = outbound_config['outbounds'][1]  # 跳过selector，获取实际的协议配置
            new_tag = new_outbound['tag']
            
            # 检查是否已存在相同tag的outbound
            existing_outbounds = template_config['outbounds']
            updated = False
            
            # 更新或添加outbound
            for i, outbound in enumerate(existing_outbounds):
                if outbound.get('tag') == new_tag:
                    # 更新现有配置
                    existing_outbounds[i] = new_outbound
                    updated = True
                    SQLOG.info(f"🔄 更新现有配置: {new_tag}")
                    break
            
            if not updated:
                # 添加新的outbound（在dns-out之前插入）
                dns_index = next((i for i, outbound in enumerate(existing_outbounds) 
                                if outbound.get('tag') == 'dns-out'), len(existing_outbounds))
                existing_outbounds.insert(dns_index, new_outbound)
                SQLOG.info(f"➕ 添加新配置: {new_tag}")
            
            # 更新selector的outbounds列表
            for outbound in existing_outbounds:
                if outbound.get('type') == 'selector' and outbound.get('tag') == 'proxy':
                    if new_tag not in outbound['outbounds']:
                        outbound['outbounds'].append(new_tag)
                        SQLOG.info(f"📋 添加到selector: {new_tag}")
                    break
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sing-box_config_{protocol}_{port}_{timestamp}.json"
            
            # 保存配置文件
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(template_config, f, indent=4, ensure_ascii=False)
            
            SQLOG.great(f"📁 完整SingBox配置已保存: {filename}")
            SQLOG.info(f"📍 文件位置: {os.path.abspath(filename)}")
            SQLOG.info("💡 可直接导入SingBox客户端使用")
            
        except Exception as e:
            SQLOG.error(f"❌ 生成SingBox配置文件失败: {str(e)}")
            SQLOG.debug(f"错误详情: {e}")
        
    
    @staticmethod
    def exe_shell_command(hostname, config, use_key_login, shell_script, verbose=False):
        result = False
        try:
            if use_key_login:       
                result = ShellHelper.ssh_connect_and_execute_with_key(hostname, config.instance_login_name, config.ssh_local_path, shell_script, verbose=verbose)
            else:
                result = ShellHelper.ssh_connect_and_execute_with_password(hostname, config.instance_login_name, config.instance_login_password, shell_script, verbose=verbose)
            return result
        except Exception as e:
            SQLOG.error(f"安装v2ray VPN时发生错误: {str(e)}")
            return result
        