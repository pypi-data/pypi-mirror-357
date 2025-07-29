import asyncio
from pathlib import Path
from click import argument, command, option
from logging import getLogger

from ...api import AivkContext
logger = getLogger("aivk.install")

@command()
@argument("id")
@option("--index", "-i", default="", help="可选的 PyPI 索引 URL")
def install(id: str, index: str):
    """
    AIVK 模块安装命令
    :param id: AIVK 模块 ID / str | Path
    """
    if id == "aivk":
        logger.warning("AIVK 模块已安装，无需重复安装。")
        return
    logger.info(f"安装 AIVK 模块: {id}")
    if Path(id).is_file():
        logger.info(f"检测到 {id} 是一个文件路径，将尝试安装本地模块")
        _pypi = id
    else:
        _pypi = f"aivk_{id}"
    ctx = AivkContext.getContext()
    async def _install():
        async with ctx.env("aivk", create_venv=True) as fs:
            if index:
                logger.info(f"使用索引 {index} 安装模块 {id}")
                await fs.aexec("uv", "pip", "install", _pypi, "--index-url", index)
            else:
                logger.info(f"从默认索引安装模块 {id}")
                await fs.aexec("uv", "pip", "install", _pypi)
    asyncio.run(_install())