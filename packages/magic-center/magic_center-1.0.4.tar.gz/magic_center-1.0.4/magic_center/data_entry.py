from magic_center.service.math.shu_xue_ti import (auto_less_than_100,
                                     auto_less_than_20,
                                     auto_num_comparation_less_than_100,
                                     auto_num_comparation_less_than_20,
                                     auto_shushi_less_than_100,
                                     auto_less_than_100_pmm,
                                     auto_less_than_100_pmmd,
                                     auto_less_than_100_pmmdv)
from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler
from mcp.server.fastmcp import FastMCP


logger = logging.Logger("data_entry_logger")
log_handler = RotatingFileHandler("maginc_center/log/data_entry.log",
                                  maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
log_handler.setLevel(logging.DEBUG)
log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s")
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)


load_dotenv()
mcp = FastMCP()


@mcp.tool()
async def kousuanti(limit: int):
    """
    生成{limit}以内的数学加减法混合计算口算题
    params: limit: 指定题目中数字的范围，取值为20或100
    return: 如果status是success，则返回文件的完整路径；否则只返回error
    """
    environment = os.environ.get("ENVIRONMENT")
    logger.debug("environment --> " + environment)
    if environment == "prod":
        sheet_path = os.environ.get("CLOUD_SHEET_PATH")
    else:
        sheet_path = os.environ.get("LOCAL_SHEET_PATH")
    logger.debug("sheet_path --> " + sheet_path)
    logger.debug("limit is --> " + str(limit))
    if limit == 100:
        file_path = auto_less_than_100(sheet_path)
        logger.debug("Generated 100以内混合加减法 exercises successfully!")
    elif limit == 20:
        file_path = auto_less_than_20(sheet_path)
        logger.debug("Generated 20以内混合加减法 exercises successfully!")
    return {
        "file_path": file_path,
        "status": "success"
    }


@mcp.tool()
async def kousuanti_pmm(limit: int):
    """
    生成{limit}以内的数学加减乘法混合计算口算题
    params: limit: 指定题目中数字的范围，取值为100
    return: 如果status是success，则返回文件的完整路径；否则只返回error
    """
    environment = os.environ.get("ENVIRONMENT")
    logger.debug("environment --> " + environment)
    if environment == "prod":
        sheet_path = os.environ.get("CLOUD_SHEET_PATH")
    else:
        sheet_path = os.environ.get("LOCAL_SHEET_PATH")
    logger.debug("sheet_path --> " + sheet_path)
    logger.debug("limit is --> " + str(limit))
    if limit == 100:
        file_path = auto_less_than_100_pmm(sheet_path)
        logger.debug("Generated 100以内混合加减乘法 exercises successfully!")
    return {
        "file_path": file_path,
        "status": "success"
    }


@mcp.tool()
async def kousuanti_pmmd(limit: int):
    """
    生成{limit}以内的数学加减乘除法混合计算口算题
    params: limit: 指定题目中数字的范围，取值为100
    return: 如果status是success，则返回文件的完整路径；否则只返回error
    """
    environment = os.environ.get("ENVIRONMENT")
    logger.debug("environment --> " + environment)
    if environment == "prod":
        sheet_path = os.environ.get("CLOUD_SHEET_PATH")
    else:
        sheet_path = os.environ.get("LOCAL_SHEET_PATH")
    logger.debug("sheet_path --> " + sheet_path)
    logger.debug("limit is --> " + str(limit))
    if limit == 100:
        file_path = auto_less_than_100_pmmd(sheet_path)
        logger.debug("Generated 100以内混合加减乘除法 exercises successfully!")
    return {
        "file_path": file_path,
        "status": "success"
    }


@mcp.tool()
async def shushijisuan(limit: int):
    """
    生成{limit}以内的数学列竖式混合加减法计算口算题
    params: limit: 指定题目中数字的范围，取值为100
    return: 如果status是success，则返回文件的完整路径；否则只返回error
    """
    environment = os.environ.get("ENVIRONMENT")
    logger.debug("environment --> " + environment)
    if environment == "prod":
        sheet_path = os.environ.get("CLOUD_SHEET_PATH")
    else:
        sheet_path = os.environ.get("LOCAL_SHEET_PATH")
    logger.debug("sheet_path --> " + sheet_path)
    logger.debug("limit is --> " + str(limit))
    if limit == 100:
        file_path = auto_shushi_less_than_100(sheet_path)
        logger.debug("Generated 100以内列竖式混合加减法 exercises successfully!")
    return {
        "file_path": file_path,
        "status": "success"
    }


@mcp.tool()
async def kousuanti_pmmdv(limit: int, pages: int = 1):
    """
    生成{limit}以内的数学混合加减乘除法和竖式计算口算题
    params: limit: 指定题目中数字的范围，取值为100
            pages: 指定生成的题目页数，默认为1页
    return: 如果status是success，则返回文件的完整路径；否则只返回error
    """
    environment = os.environ.get("ENVIRONMENT")
    logger.debug("environment --> " + environment)
    if environment == "prod":
        sheet_path = os.environ.get("CLOUD_SHEET_PATH")
    else:
        sheet_path = os.environ.get("LOCAL_SHEET_PATH")
    logger.debug("sheet_path --> " + sheet_path)
    logger.debug("limit is --> " + str(limit))
    if limit == 100:
        file_path = auto_less_than_100_pmmdv(sheet_path, pages=pages)
        logger.debug("Generated 100以内混合加减乘除法和竖式 exercises successfully!")
    return {
        "file_path": file_path,
        "status": "success"
    }


@mcp.tool()
async def bijiaodaxiao(limit: int):
    """
    生成{limit}以内的数学比较大小计算口算题
    params: limit: 指定题目中数字的范围，取值为20或100
    return: 如果status是success，则返回文件的完整路径；否则只返回error
    """
    environment = os.environ.get("ENVIRONMENT")
    logger.debug("environment --> " + environment)
    if environment == "prod":
        sheet_path = os.environ.get("CLOUD_SHEET_PATH")
    else:
        sheet_path = os.environ.get("LOCAL_SHEET_PATH")
    logger.debug("sheet_path --> " + sheet_path)
    logger.debug("limit is --> " + str(limit))
    if limit == 100:
        file_path = auto_num_comparation_less_than_100(sheet_path)
        logger.debug("Generated 100以内比较大小 exercises successfully!")
    elif limit == 20:
        file_path = auto_num_comparation_less_than_20(sheet_path)
        logger.debug("Generated 20以内比较大小 exercises successfully!")
    return {
        "file_path": file_path,
        "status": "success"
    }


if __name__ == '__main__':
    mcp.run(
        transport="stdio"
    )
