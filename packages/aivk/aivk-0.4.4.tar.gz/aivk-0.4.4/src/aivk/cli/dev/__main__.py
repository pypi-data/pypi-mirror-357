import os
from pathlib import Path
from logging import getLogger
import sys
from click import command
import asyncio
import toml
from aivk.api import AivkContext , AivkMod

logger = getLogger("aivk.dev")

@command()
def dev():
    """
    AIVK 开发者工具
    """
    dev_dir = os.getcwd()
    async def run():
        async with AivkContext.getContext().env("aivk", create_venv=True) as fs:
            src_path = Path(dev_dir) / "src"
            # 导入当前包
            info = toml.load(Path(dev_dir) / "pyproject.toml")

            if src_path.exists() and str(src_path) not in sys.path:
                sys.path.insert(0, str(src_path))
                logger.debug(f"已将 {src_path} 添加到 sys.path")

            package_name = info.get("project", {}).get("name", "")
            if not package_name:
                raise ValueError("pyproject.toml 中未找到项目名称")
            
            # 检查是否是aivk模块 
            if not AivkMod.is_aivk_mod(package_name):
                raise ValueError(f"{package_name} 不是 AIVK 模块！")

            # 美化输出项目基本信息
            logger.info(f"正在启动 AIVK 模块: {package_name}")
            logger.info(f"项目目录: {dev_dir}")
            logger.info(f"项目名称: {package_name}")
            logger.info(f"项目版本: {info.get('project', {}).get('version', '未知')}")
            logger.info(f"项目版本: {info.get('project', {}).get('version', '未知')}")
            logger.info(f"项目描述: {info.get('project', {}).get('description', '无描述')}")
            logger.info(f"项目作者: {info.get('project', {}).get('authors', [{'name': '未知'}])[0]['name']}")
            try:
                import importlib
                # 动态导入模块

                _ = importlib.import_module(package_name)
            
                mod = AivkMod.getMod(package_name)
                mod.load

            except ImportError as e:
                raise ImportError(f"导入模块 {package_name} 时发生错误: {e}")


    asyncio.run(run())