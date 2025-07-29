import asyncio
from click import command , argument, confirm
from ...api import AivkContext
from logging import getLogger
logger = getLogger("aivk.uninstall")

@command()
@argument("id")
def uninstall(id: str):
    """
    AIVK 模块卸载命令
    """
    async def _uninstall(id: str):
        async with AivkContext.getContext().env("aivk", create_venv=True) as fs:
            if id == "aivk":
                if confirm("AIVK 模块是核心模块，卸载后可能导致系统不稳定，确定要卸载吗？",default=False):
                    logger.info("正在卸载 AIVK 模块...")
                    await fs.aexec("uv", "pip", "uninstall", "aivk")
                    logger.info("AIVK 模块已成功卸载")
            else:
                try:
                    await fs.aexec("uv", "pip", "uninstall", f"aivk_{id}")
                    logger.info(f"AIVK 模块 {id} 已成功卸载")
                except Exception as e:
                    logger.error(f"卸载 AIVK 模块 {id} 时发生错误: {e}")
                    return
    asyncio.run(_uninstall(id))