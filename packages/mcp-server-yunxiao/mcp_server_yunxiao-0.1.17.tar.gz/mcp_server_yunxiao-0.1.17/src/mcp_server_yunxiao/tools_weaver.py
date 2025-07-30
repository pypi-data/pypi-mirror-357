from typing import Annotated, Optional, List
from pydantic import Field
from .client import _call_api, _call_api_raw
from . import mcp
import re
import json
from datetime import datetime, timedelta


REGION_ALIAS_MAP = {
    "sheec": "ap-shenyang-ec",
    "sh": "ap-shanghai",
    "sao": "sa-saopaulo",
    "bjjr": "ap-beijing-fsi",
    "hzec": "ap-hangzhou-ec",
    "cgoec": "ap-zhengzhou-ec",
    "use": "na-ashburn",
    "xiyec": "ap-xian-ec",
    "cd": "ap-chengdu",
    "cq": "ap-chongqing",
    "shjr": "ap-shanghai-fsi",
    "szjr": "ap-shenzhen-fsi",
    "usw": "na-siliconvalley",
    "jkt": "ap-jakarta",
    "in": "ap-mumbai",
    "jnec": "ap-jinan-ec",
    "gz": "ap-guangzhou",
    "szsycft": "ap-shenzhen-sycft",
    "qyxa": "ap-qingyuan-xinan",
    "hk": "ap-hongkong",
    "sjwec": "ap-shijiazhuang-ec",
    "tpe": "ap-taipei",
    "gzopen": "ap-guangzhou-open",
    "jp": "ap-tokyo",
    "hfeec": "ap-hefei-ec",
    "qy": "ap-qingyuan",
    "bj": "ap-beijing",
    "whec": "ap-wuhan-ec",
    "csec": "ap-changsha-ec",
    "tsn": "ap-tianjin",
    "nj": "ap-nanjing",
    "de": "eu-frankfurt",
    "th": "ap-bangkok",
    "sg": "ap-singapore",
    "kr": "ap-seoul",
    "fzec": "ap-fuzhou-ec",
    "szx": "ap-shenzhen",
    "xbec": "ap-xibei-ec",
    "shadc": "ap-shanghai-adc",
    "shwxzf": "ap-shanghai-wxzf",
    "gzwxzf": "ap-guangzhou-wxzf",
    "szjxcft": "ap-shenzhen-jxcft",
    "shhqcft": "ap-shanghai-hq-cft",
    "shhqcftfzhj": "ap-shanghai-hq-uat-cft",
    "shwxzfjpyzc": "ap-shanghai-wxp-ops",
    "njxfcft": "ap-nanjing-xf-cft",
}

def _get_region_alias(region: str, region_alias: Optional[str] = None) -> str:
    """
    通用 region 到 regionAlias 的映射
    """
    if region_alias:
        return region_alias
    for k, v in REGION_ALIAS_MAP.items():
        if v == region:
            return k
    return ""

@mcp.tool(description="查询VStation任务列表（简称VS任务）")
def query_task_message(
    region: Annotated[str, Field(description="地域，如 ap-guangzhou")],
    task_id: Annotated[Optional[List[str]], Field(description="VStation任务ID")] = [],
    instance_id: Annotated[Optional[List[str]], Field(description="实例ID")] = [],
    uuid: Annotated[Optional[List[str]], Field(description="任务UUID")] = [],
    request_id: Annotated[Optional[List[str]], Field(description="请求ID")] = [],
    host_ip: Annotated[Optional[List[str]], Field(description="母机/宿主机的IP")] = [],
    owner: Annotated[Optional[List[str]], Field(description="客户Owner")] = [],
    start_time: Annotated[Optional[str], Field(description="起始时间，格式：YYYY-MM-DD HH:mm:ss")] = None,
    end_time: Annotated[Optional[str], Field(description="结束时间，格式：YYYY-MM-DD HH:mm:ss")] = None,
    limit: Annotated[int, Field(description="分页长度")] = 100,
    region_alias: Annotated[Optional[str], Field(description="地域别名")] = None
) -> str:
    """
    查询 VStation 任务列表
    Args:
        region: 地域，如 ap-guangzhou
        task_id: VStation任务ID
        instance_id: 实例ID
        uuid: 任务UUID
        request_id: 请求ID
        host_ip: 母机/宿主机 IP
        start_time: 起始时间，格式：YYYY-MM-DD HH:mm:ss（可选，默认当天 00:00:00）
        end_time: 结束时间，格式：YYYY-MM-DD HH:mm:ss（可选，默认当天 23:59:59）
        region_alias: 地域别名（可选，若未传则自动匹配）
    Returns:
        str: 查询结果的JSON字符串
    """
    # 自动补全时间
    if not start_time or not end_time:
        today = datetime.now().strftime("%Y-%m-%d")
        if not start_time:
            start_time = f"{today} 00:00:00"
        if not end_time:
            end_time = f"{today} 23:59:59"
    alias = _get_region_alias(region, region_alias)
    filters = []
    if task_id:
        filters.append({
            "Name": "task_id",
            "Values": task_id
        })
    if request_id:
        filters.append({
            "Name": "requestId",
            "Values": request_id
        })
    if uuid:
        filters.append({
            "Name": "uuid",
            "Values": uuid
        })
    if instance_id:
        filters.append({
            "Name": "uInstanceId",
            "Values": instance_id
        })
    if host_ip:
        filters.append({
            "Name": "hostIp",
            "Values": host_ip
        })
    if owner:
        filters.append({
            "Name": "owner",
            "Values": owner
        })
    params = {
        "Region": region,
        "Filters": filters,
        "StartTime": start_time,
        "EndTime": end_time,
        "Offset": 0,
        "Limit": limit,
        "Action": "QueryTaskMessage",
        "AppId": "251006228",
        "RequestSource": "YunXiao",
        "SubAccountUin": "493083759",
        "Uin": "493083759",
        "regionAlias": alias,
        "Fields": [
            "taskStatus",
            "code",
            "cursor",
            "errorMsg",
            "hostIp",
            "hypervisor",
            "mode",
            "owner",
            "parentTaskId",
            "region",
            "requestId",
            "startTime",
            "taskId",
            "taskName",
            "taskProgress",
            "taskState",
            "traceRequestId",
            "uInstanceId",
            "uuid",
            "finishTime",
            "updateTime",
            "delayExecSteps",
            "hasDelaySteps",
            "migrateHostIp",
            "stepsLength",
            "productCategory",
            "chcId",
            "dedicatedClusterId",
            "p2pFlow",
            "desTaskId",
            "dataDiskSerial",
            "rootDiskSerial",
            "vifSerial",
            "uImageId",
            "vpcId",
            "instanceType",
            "zoneId",
            "gridId"
        ]
    }
    return _call_api("/weaver/upstream/terra/QueryTaskMessage", params)

@mcp.tool(description="查询VStation错误码（VStation简称VS）")
def describe_error_codes(
    region: Annotated[str, Field(description="地域，如 ap-guangzhou")],
    region_alias: Annotated[Optional[str], Field(description="地域别名")] = None
) -> str:
    """
    查询 VStation 错误码
    Args:
        region: 地域，如 ap-guangzhou
        region_alias: 地域别名（可选，若未传则自动匹配）
    Returns:
        str: 查询结果的JSON字符串
    """
    alias = _get_region_alias(region, region_alias)
    params = {
        "Region": region,
        "AppId": "251006228",
        "Action": "DescribeErrorCodes",
        "Uin": "493083759",
        "SubAccountUin": "493083759",
        "RequestSource": "YunXiao",
        "regionAlias": alias
    }
    return _call_api("/weaver/upstream/terra/QueryTaskMessage", params)

@mcp.tool(description="查询母机Compute任务列表")
def describe_host_task(
    region: Annotated[str, Field(description="地域，如 ap-guangzhou")],
    host: Annotated[str, Field(description="宿主机IP")],
    vs_task_id: Annotated[int, Field(description="VStation任务ID")],
    region_alias: Annotated[Optional[str], Field(description="地域别名")] = None
) -> str:
    """
    查询 Compute 任务列表
    Args:
        region: 地域，如 ap-guangzhou
        host: 宿主机IP
        vs_task_id: VStation任务ID
        region_alias: 地域别名（可选，若未传则自动匹配）
    Returns:
        str: 查询结果的JSON字符串
    """
    alias = _get_region_alias(region, region_alias)
    params = {
        "TaskId": vs_task_id,
        "Host": host,
        "Region": region,
        "Action": "DescribeHostTask",
        "AppId": "251006228",
        "RequestSource": "QCLOUD_OP",
        "SubAccountUin": "493083759",
        "Uin": "493083759",
        "regionAlias": alias
    }
    return _call_api("/weaver/upstream/terra/DescribeHostTask", params)

@mcp.tool(description="查询母机Compute任务的执行日志")
def query_host_task_log(
    region: Annotated[str, Field(description="地域，如 ap-guangzhou")],
    host_ip: Annotated[str, Field(description="宿主机IP")],
    host_task_id: Annotated[str, Field(description="母机/宿主机/Compute组件的任务ID，为describe_host_task返回的taskid字段。注意这里不要和VS任务ID混淆。")],
    region_alias: Annotated[Optional[str], Field(description="地域别名")] = None
) -> str:
    """
    查询 Compute 任务的执行日志
    Args:
        region: 地域，如 ap-guangzhou
        host_task_id: 宿主机IP
        task_id: 母机/宿主机任务ID
        region_alias: 地域别名（可选，若未传则自动匹配）
    Returns:
        str: 查询结果的JSON字符串
    """
    alias = _get_region_alias(region, region_alias)
    params = {
        "TaskId": host_task_id,
        "HostIp": host_ip,
        "Region": region,
        "Action": "QueryTaskLog",
        "AppId": "1251783334",
        "RequestSource": "YunXiao",
        "SubAccountUin": "3205597606",
        "Uin": "3205597606",
        "regionAlias": alias
    }
    return _call_api("/weaver/upstream/terra/QueryTaskLog", params)


def _call_compute(ip: str, method: str, data: dict, check: bool = True) -> str:
    """
    发送请求到Compute服务
    Args:
        ip: 宿主机IP地址
        method: 请求方法名
        data: 请求数据
        check: 是否检查返回数据

    Returns:
        str: 返回的JSON字符串
    """
    req_params = {
        "username": "vstation",
        "password": "vstation",
        "data": data,
        "command": method,
        "ip": ip
    }
    return _call_api("/weaver/upstream/compute/CommonTools", req_params)


def _call_compute_log(ip: str, logname: str = 'procedure', timestr: Optional[str] = None) -> Optional[str]:
    """
    请求日志文件
    Args:
        ip: 宿主机IP地址
        logname: 日志名称
        timestr: 时间字符串

    Returns:
        Optional[str]: 日志内容或None
    """
    req_params = {
        "username": "vstation",
        "password": "vstation",
        "data": {'hostIp': ip},
        "ip": ip,
        "logname": logname,
        "timestr": timestr
    }
    return _call_api_raw("/weaver/upstream/compute/ComputeLog", req_params)


@mcp.tool(description="获取母机/宿主机/Compute状态信息和当前子机列表")
def get_host_stat(
        ip: Annotated[str, Field(description="宿主机IP地址")],
        raw: Annotated[bool, Field(description="是否返回原始数据")] = False
) -> str:
    """
    获取宿主机状态信息，包括CPU、内存、虚拟机列表等

    Args:
        ip: 宿主机IP地址
        raw: 是否返回原始数据（不进行格式化处理）

    Returns:
        str: JSON格式的宿主机状态信息
    """
    payload = {"debug": True}
    return _call_compute(ip, "get_host_stat", payload)


@mcp.tool(description="获取虚拟机/子机XML信息/配置")
def get_vm_xml(
        ip: Annotated[str, Field(description="宿主机IP地址")],
        uuid: Annotated[str, Field(description="虚拟机UUID")],
        static: Annotated[bool, Field(description="是否获取静态配置")] = False
) -> str:
    """
    获取虚拟机的XML配置信息

    Args:
        ip: 宿主机IP地址
        uuid: 虚拟机UUID
        static: 是否获取静态配置

    Returns:
        str: 虚拟机的XML配置
    """
    payload = {
        "username": "vstation",
        "uuid": [uuid],
        "static": static,
        "password": "vstation",
        "command": "get_vm_xml"
    }
    return _call_compute(ip, "get_vm_xml", payload)


@mcp.tool(description="查询母机/宿主机/Compute任务执行日志")
def query_task_log(
        ip: Annotated[str, Field(description="宿主机IP地址")],
        task_id: Annotated[str, Field(description="compute任务/taskID")]
) -> str:
    """
    查询指定任务的执行日志

    Args:
        ip: 宿主机IP地址
        task_id: 任务ID

    Returns:
        str: JSON格式的日志信息
    """
    payload = {
        "where": {"taskid": task_id}
    }
    rst = _call_compute(ip, "query_compute_task", payload)
    tasks = json.loads(rst).get("data", {}).get("data", {}).get("result")
    if not tasks:
        return json.dumps({"error": "Failed to retrieve compute task"})

    task = tasks[0]
    invoke_day = task['invoke_time']
    if not invoke_day:
        return json.dumps({"error": "Task seems not invoked, task invoke time is None"})

    invoke_day = invoke_day.split(" ")[0].replace("-", "")
    end_day = task['end_time'].split(" ")[0].replace("-", "")

    logs = []
    return _call_compute_log(ip, "procedure", invoke_day)
    if not pro_log:
        return json.dumps({"error": f"Failed to get log procedure_{invoke_day}"})

    pro_log = pro_log.split("\n")
    thread_id = None
    sticky = False

    for line in pro_log:
        if thread_id is None and line.find(f"taskid:{task_id},") >= 0:
            thread_id = line.split("[")[2][:-1]
        if thread_id is not None:
            if re.match(r'^\[[0-9\.\:]*\]\:\[.*\]\[', line):
                if re.match(f'^\[[0-9\.\:]*\]\:\[{thread_id}\]\[', line):
                    sticky = True
                    logs.append(line)
                else:
                    sticky = False
            else:
                if sticky:
                    logs.append(line)

    if not thread_id:
        return json.dumps({"error": "No thread ID found"})

    if invoke_day != end_day:
        pro_log = _call_compute_log(ip, "procedure", end_day)
        if pro_log:
            pro_log = pro_log.split("\n")
            for line in pro_log:
                if re.match(r'^\[[0-9\.\:]*\]\:\[.*\]\[', line):
                    if re.match(f'^\[[0-9\.\:]*\]\:\[{thread_id}\]\[', line):
                        sticky = True
                        logs.append(line)
                    else:
                        sticky = False
                else:
                    if sticky:
                        logs.append(line)

    return json.dumps({"logs": logs})


@mcp.tool(description="查询虚拟机cpu/cpuset/Pico信息")
def query_vm_pico(
        ip: Annotated[str, Field(description="宿主机IP地址")],
        uuid: Annotated[str, Field(description="虚拟机UUID")],
        date_str: Annotated[str, Field(description="日期字符串，格式: YYYYMMDD")],
        time_str: Annotated[str, Field(description="时间字符串，格式: HH:MM:SS")]
) -> str:
    """
    查询虚拟机的Pico信息

    Args:
        ip: 宿主机IP地址
        uuid: 虚拟机UUID
        date_str: 日期字符串
        time_str: 时间字符串

    Returns:
        str: JSON格式的Pico信息
    """

    def _parse_date(date_str: str) -> datetime:
        try:
            return datetime.strptime(date_str, "%Y%m%d")
        except:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except:
                try:
                    return datetime.strptime(date_str, "%Y_%m_%d")
                except:
                    raise ValueError("Invalid date format")

    def _parse_time(time_str: str) -> datetime:
        try:
            return datetime.strptime(time_str, "%H:%M:%S")
        except:
            try:
                return datetime.strptime(time_str, "%H%M%S")
            except:
                raise ValueError("Invalid time format")

    counter = 0
    date_obj = _parse_date(date_str)
    while True:
        the_log = _call_compute_log(ip, "dump", datetime.strftime(date_obj, "%Y%m%d"))
        if the_log is None:
            return json.dumps({"error": "Date not found"})

        the_log = the_log.strip().split("\n")
        for line in the_log[::-1]:
            if not line:
                break
            if (_parse_time(time_str) >= _parse_time(line[1:9]) and
                    uuid in line):
                ghs_data = eval(line[line.find("{"):])
                return json.dumps({
                    "found_at": f"{datetime.strftime(date_obj, '%Y-%m-%d')} {line[1:9]}",
                    "data": ghs_data
                }, indent=4)

        time_str = "23:59:59"
        date_obj = date_obj - timedelta(days=1)
        counter += 1
        if counter >= 10:
            return json.dumps({"error": "Reached max search depth"})


@mcp.tool(description="查询母机/宿主机/Compute健康状态")
def health_check(
        ip: Annotated[str, Field(description="宿主机IP地址")],
        version: Annotated[Optional[int], Field(description="版本号")] = None
) -> str:
    """
    查询宿主机的健康状态

    Args:
        ip: 宿主机IP地址
        version: 版本号

    Returns:
        str: JSON格式的健康状态信息
    """
    payload = {"debug": True}
    return _call_compute(ip, "health_check", payload)


@mcp.tool(description="查询母机/宿主机/Compute守护进程历史")
def query_daemon_history(
        ip: Annotated[str, Field(description="宿主机IP地址")],
        version: Annotated[Optional[int], Field(description="版本号")] = None
) -> str:
    """
    查询宿主机守护进程的历史记录

    Args:
        ip: 宿主机IP地址
        version: 版本号

    Returns:
        str: JSON格式的历史记录
    """
    payload = {
        "debug": True,
        "version": version if version else 999
    }
    return _call_compute(ip, "query_daemon_history", payload, check=False)


@mcp.tool(description="查询母机/宿主机/Compute线程状态")
def thread_check(
        ip: Annotated[str, Field(description="宿主机IP地址")]
) -> str:
    """
    查询宿主机的线程状态

    Args:
        ip: 宿主机IP地址

    Returns:
        str: JSON格式的线程状态信息
    """
    payload = {
        "username": "vstation",
        "data": {"version": 999},
        "password": "vstation",
        "command": "thread_check"
    }
    return _call_compute(ip, "thread_check", payload)