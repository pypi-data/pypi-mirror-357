from typing import Any, Dict, List, Generator
from mcp.server.fastmcp import FastMCP
import os
from win32file import CreateFile, SetFileTime, GetFileTime, CloseHandle
from win32file import GENERIC_READ, GENERIC_WRITE, OPEN_EXISTING
from pywintypes import Time  # 可以忽视这个 Time 报错（运行程序还是没问题的）
import time
import random
from datetime import datetime

# Initialize FastMCP server
mcp = FastMCP("essay_file_mcp_server_lc")


def modifyFileTime(filePath, createTime, modifyTime, accessTime, offset):
    """
    用来修改任意文件的相关时间属性，时间格式：YYYY-MM-DD HH:MM:SS 例如：2019-02-02 00:01:02
    :param filePath: 文件路径名
    :param createTime: 创建时间
    :param modifyTime: 修改时间
    :param accessTime: 访问时间
    :param offset: 时间偏移的秒数,tuple格式，顺序和参数时间对应
    """
    try:
        format = "%Y-%m-%d %H:%M:%S"  # 时间格式
        cTime_t = timeOffsetAndStruct(createTime, format, offset[0])
        mTime_t = timeOffsetAndStruct(modifyTime, format, offset[1])
        aTime_t = timeOffsetAndStruct(accessTime, format, offset[2])

        fh = CreateFile(filePath, GENERIC_READ | GENERIC_WRITE, 0, None, OPEN_EXISTING, 0, 0)
        createTimes, accessTimes, modifyTimes = GetFileTime(fh)

        createTimes = Time(time.mktime(cTime_t))
        accessTimes = Time(time.mktime(aTime_t))
        modifyTimes = Time(time.mktime(mTime_t))
        SetFileTime(fh, createTimes, accessTimes, modifyTimes)
        CloseHandle(fh)
        return 0
    except:
        return 1


def timeOffsetAndStruct(times, format, offset):
    return time.localtime(time.mktime(time.strptime(times, format)) + offset)


def random_datetime_str(date_str):
    hh = f"{random.randint(0, 23):02d}"
    mm = f"{random.randint(0, 59):02d}"
    ss = f"{random.randint(0, 59):02d}"
    return f"{date_str} {hh}:{mm}:{ss}"


@mcp.tool(name='update_file_attr', description='修改文件属性，ctime是创建时间，其格式为：2025-01-01，mtime是修改时间，其格式为：2025-01-01')
async def update_file_attr(fpath: str, ctime: str, mtime: str) -> str | dict[str, Any] | None:
    if os.path.exists(fpath):
        print(f"文件 {fpath} 存在")
    else:
        return ('文件不存在。\nwindows系统文件参数需要按照这个格式：C:\\Users\\Administrator\\Desktop\\test.txt。\nMac系统：/Users'
                '/Administrator/Desktop/test.txt')
    cyear, _, _ = ctime.split('-')  # 按 '-' 分割
    myear, _, _ = mtime.split('-')  # 按 '-' 分割

    random_cTime = random_datetime_str(ctime)
    random_mTime = random_datetime_str(mtime)
    random_aTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 访问时间，这个搞成默认当前时间即可

    offset = (0, 1, 2)  # 偏移的秒数（不知道干啥的）

    # 调用函数修改文件创建时间，并判断是否修改成功
    r = modifyFileTime(fpath, random_cTime, random_mTime, random_aTime, offset)

    if r == 0:
        return '修改完成'
    elif r == 1:
        return '修改失败'


def run():
    mcp.run(transport="sse")


if __name__ == "__main__":
    run()
