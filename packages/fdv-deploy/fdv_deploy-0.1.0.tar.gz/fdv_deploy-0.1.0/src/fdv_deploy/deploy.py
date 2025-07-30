import asyncio
import json
import logging
import sys
import os
import re
import time

import mcp
import paramiko
from typing import Any, Dict, Optional, List
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource, LoggingLevel
)
import mcp.types as types

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fdv-tools")

# 机器配置 - 建议从环境变量读取
MACHINE_A = {
    "host": os.getenv("MACHINE_A_HOST", "10.68.80.166"),
    "username": os.getenv("MACHINE_A_USER", "root"),
    "password": os.getenv("MACHINE_A_PASSWORD", "dbapp@2018"),  # 生产环境应从环境变量读取
    "port": int(os.getenv("MACHINE_A_PORT", "22"))
}

MACHINE_B = {
    "host": os.getenv("MACHINE_B_HOST", "10.68.120.215"),
    "username": os.getenv("MACHINE_B_USER", "root"),
    "password": os.getenv("MACHINE_B_PASSWORD", "dbapp@2018"),  # 生产环境应从环境变量读取
    "port": int(os.getenv("MACHINE_B_PORT", "22"))
}

class SSHExecutor:
    """SSH执行器，用于执行远程命令"""

    @staticmethod
    def create_connection(machine_config: Dict[str, Any]) -> Optional[paramiko.SSHClient]:
        """创建SSH连接"""
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=machine_config["host"],
                username=machine_config["username"],
                password=machine_config["password"],
                port=machine_config["port"],
                timeout=30
            )
            logger.info(f"成功连接到 {machine_config['host']}")
            return client
        except Exception as e:
            logger.error(f"连接到 {machine_config['host']} 失败: {str(e)}")
            return None

    @staticmethod
    def execute_command_realtime(client: paramiko.SSHClient, command: str,
                                 working_dir: str = None, timeout: int = 600) -> Dict[str, Any]:
        """实时执行命令并返回结果"""
        try:
            # 如果指定了工作目录，则切换到该目录
            if working_dir:
                command = f"cd {working_dir} && {command}"

            logger.info(f"执行命令: {command}")

            # 创建新的通道执行命令
            transport = client.get_transport()
            channel = transport.open_session()
            channel.settimeout(timeout)
            channel.exec_command(command)

            output_lines = []
            error_lines = []
            start_time = time.time()

            while True:
                # 检查超时
                if time.time() - start_time > timeout:
                    logger.warning("命令执行超时")
                    break

                # 检查通道状态
                if channel.exit_status_ready():
                    # 读取剩余所有输出
                    while channel.recv_ready():
                        data = channel.recv(4096).decode('utf-8', errors='ignore')
                        if data:
                            for line in data.split('\n'):
                                if line.strip():
                                    output_lines.append(line.strip())

                    while channel.recv_stderr_ready():
                        data = channel.recv_stderr(4096).decode('utf-8', errors='ignore')
                        if data:
                            for line in data.split('\n'):
                                if line.strip():
                                    error_lines.append(line.strip())
                    break

                # 实时读取标准输出
                if channel.recv_ready():
                    data = channel.recv(4096).decode('utf-8', errors='ignore')
                    if data:
                        for line in data.split('\n'):
                            if line.strip():
                                output_lines.append(line.strip())
                                logger.info(f"输出: {line.strip()}")

                # 实时读取错误输出
                if channel.recv_stderr_ready():
                    data = channel.recv_stderr(4096).decode('utf-8', errors='ignore')
                    if data:
                        for line in data.split('\n'):
                            if line.strip():
                                error_lines.append(line.strip())
                                logger.error(f"错误: {line.strip()}")

                time.sleep(0.1)

            exit_code = channel.recv_exit_status()
            channel.close()

            return {
                "success": True,
                "output": '\n'.join(output_lines),
                "error": '\n'.join(error_lines),
                "exit_code": exit_code
            }

        except Exception as e:
            logger.error(f"执行命令失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "output": "",
                "exit_code": -1
            }

# 创建MCP服务器实例
server = Server("fdv-tools")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """返回可用工具列表"""
    return [
        Tool(
            name="sim_login",
            description="在机器10.68.80.166上执行SIM登录",
            inputSchema={
                "type": "object",
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "description": "手机号码（必需）"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "超时时间（秒）",
                        "default": 30000
                    }
                },
                "required": ["phone_number"]
            }
        ),
        Tool(
            name="sim_logout",
            description="在机器10.68.80.166上执行SIM退出登录",
            inputSchema={
                "type": "object",
                "properties": {
                    "timeout": {
                        "type": "integer",
                        "description": "超时时间（秒）",
                        "default": 6000
                    }
                }
            }
        ),
        Tool(
            name="fdv_frontend_build",
            description="在机器10.68.80.166上执行FDV前端镜像打包",
            inputSchema={
                "type": "object",
                "properties": {
                    "timeout": {
                        "type": "integer",
                        "description": "超时时间（秒）",
                        "default": 180000
                    }
                }
            }
        ),
        Tool(
            name="fdv_frontend_deploy",
            description="在机器10.68.120.215上执行FDV前端部署",
            inputSchema={
                "type": "object",
                "properties": {
                    "timeout": {
                        "type": "integer",
                        "description": "超时时间（秒）",
                        "default": 60000
                    }
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
    """处理工具调用"""
    try:
        result = await handle_tool_call(name, arguments)

        # 格式化返回结果
        response_text = f"工具: {name}\n"
        response_text += f"状态: {'✅ 成功' if result.get('success') else '❌ 失败'}\n"
        response_text += f"消息: {result.get('message', '')}\n"

        if result.get('output'):
            response_text += f"\n输出:\n{result['output']}\n"

        return [types.TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"工具调用失败: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(type="text", text=error_msg)]

# 工具实现函数
async def sim_login(phone_number: str, timeout: int = 30000) -> Dict[str, Any]:
    """SIM登录工具"""
    if not phone_number:
        return {
            "success": False,
            "message": "手机号码不能为空",
            "output": ""
        }

    # 验证手机号格式
    if not re.match(r'^1[3-9]\d{9}$', phone_number):
        return {
            "success": False,
            "message": "手机号码格式不正确",
            "output": ""
        }

    # 连接到机器A
    client = SSHExecutor.create_connection(MACHINE_A)
    if not client:
        return {
            "success": False,
            "message": "无法连接到机器A",
            "output": ""
        }

    try:
        command = f"sim --login {phone_number}"
        logger.info(f"在机器A上执行SIM登录: {command}")

        result = SSHExecutor.execute_command_realtime(client, command, timeout=timeout)

        if not result["success"]:
            return {
                "success": False,
                "message": f"命令执行失败: {result['error']}",
                "output": result.get("output", "")
            }

        output = result.get("output", "")
        error = result.get("error", "")
        full_output = f"{output}\n{error}".strip()

        # 检查登录结果
        if "用户登录成功" in full_output:
            return {
                "success": True,
                "message": "SIM登录成功",
                "output": full_output,
                "status": "logged_in"
            }
        elif "请在" in full_output and "的手机上进行SIM快捷认证确认" in full_output:
            return {
                "success": False,
                "message": "等待手机验证码确认中，请在手机上完成认证...",
                "output": full_output,
                "status": "waiting_verification"
            }
        else:
            return {
                "success": False,
                "message": "SIM登录失败或超时",
                "output": full_output,
                "status": "failed"
            }

    finally:
        client.close()

async def sim_logout(timeout: int = 6000) -> Dict[str, Any]:
    """SIM退出登录工具"""
    # 连接到机器A
    client = SSHExecutor.create_connection(MACHINE_A)
    if not client:
        return {
            "success": False,
            "message": "无法连接到机器A",
            "output": ""
        }

    try:
        command = "sim --logout"
        logger.info(f"在机器A上执行SIM退出登录: {command}")

        result = SSHExecutor.execute_command_realtime(client, command, timeout=timeout)

        if not result["success"]:
            return {
                "success": False,
                "message": f"命令执行失败: {result['error']}",
                "output": result.get("output", "")
            }

        output = result.get("output", "")
        error = result.get("error", "")
        full_output = f"{output}\n{error}".strip()

        # SIM退出通常会立即完成
        if "正在退出登录" in full_output or result["exit_code"] == 0:
            return {
                "success": True,
                "message": "SIM退出登录成功",
                "output": full_output
            }
        else:
            return {
                "success": True,  # 即使没有明确信息也认为成功
                "message": "SIM退出登录完成",
                "output": full_output
            }

    finally:
        client.close()

async def fdv_frontend_build(timeout: int = 180000) -> Dict[str, Any]:
    """FDV前端镜像打包工具"""
    # 连接到机器A
    client = SSHExecutor.create_connection(MACHINE_A)
    if not client:
        return {
            "success": False,
            "message": "无法连接到机器A",
            "output": ""
        }

    try:
        working_dir = "/root/venus/fdv/services/fdv-html"
        command = "./build.sh"

        logger.info(f"在机器A的{working_dir}目录下执行前端打包")

        result = SSHExecutor.execute_command_realtime(
            client, command, working_dir=working_dir, timeout=timeout
        )

        if not result["success"]:
            return {
                "success": False,
                "message": f"命令执行失败: {result['error']}",
                "output": result.get("output", "")
            }

        output = result.get("output", "")
        error = result.get("error", "")
        full_output = f"{output}\n{error}".strip()

        # 检查是否需要SIM登录
        if "❌ SIM未登录，请先登录SIM" in full_output:
            return {
                "success": False,
                "message": "❌ SIM未登录，请先执行sim_login工具进行SIM登录",
                "output": full_output,
                "need_sim_login": True
            }

        # 根据退出码判断是否成功
        exit_code = result.get("exit_code", -1)
        if exit_code == 0:
            return {
                "success": True,
                "message": "✅ FDV前端镜像打包完成",
                "output": full_output
            }
        else:
            return {
                "success": False,
                "message": "❌ FDV前端镜像打包失败",
                "output": full_output
            }

    finally:
        client.close()

async def fdv_frontend_deploy(timeout: int = 60000) -> Dict[str, Any]:
    """FDV前端部署工具"""
    # 连接到机器B
    client = SSHExecutor.create_connection(MACHINE_B)
    if not client:
        return {
            "success": False,
            "message": "无法连接到机器B",
            "output": ""
        }

    try:
        working_dir = "/home/www"
        command = "./fdv-html.sh"

        logger.info(f"在机器B的{working_dir}目录下执行前端部署")

        result = SSHExecutor.execute_command_realtime(
            client, command, working_dir=working_dir, timeout=timeout
        )

        if not result["success"]:
            return {
                "success": False,
                "message": f"命令执行失败: {result['error']}",
                "output": result.get("output", "")
            }

        output = result.get("output", "")
        error = result.get("error", "")
        full_output = f"{output}\n{error}".strip()

        # 根据退出码判断是否成功
        exit_code = result.get("exit_code", -1)
        if exit_code == 0:
            return {
                "success": True,
                "message": "✅ FDV前端部署完成",
                "output": full_output
            }
        else:
            return {
                "success": False,
                "message": "❌ FDV前端部署失败",
                "output": full_output
            }

    finally:
        client.close()

# 工具调用处理器
async def handle_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """处理工具调用的统一入口"""
    try:
        if tool_name == "sim_login":
            phone_number = arguments.get("phone_number")
            timeout = arguments.get("timeout", 30000)
            return await sim_login(phone_number, timeout)

        elif tool_name == "sim_logout":
            timeout = arguments.get("timeout", 6000)
            return await sim_logout(timeout)

        elif tool_name == "fdv_frontend_build":
            timeout = arguments.get("timeout", 180000)
            return await fdv_frontend_build(timeout)

        elif tool_name == "fdv_frontend_deploy":
            timeout = arguments.get("timeout", 60000)
            return await fdv_frontend_deploy(timeout)

        else:
            return {
                "success": False,
                "message": f"未知工具: {tool_name}"
            }

    except Exception as e:
        logger.error(f"工具调用出错: {str(e)}")
        return {
            "success": False,
            "message": f"工具调用出错: {str(e)}"
        }

async def main():
    """启动MCP服务器"""
    # 读取标准输入输出进行MCP通信
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        print("Starting MCP server for fdv-tools...")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="fdv-tools",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())