#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mcp.server.fastmcp import FastMCP
import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Optional

# 创建MCP服务器
mcp = FastMCP("广告数据查询服务")

# 从配置文件中获取token
def get_token_from_config():
    default_token = ""
    try:
        # 获取当前服务器的ID
        server_id = mcp.server_id
        
        # 尝试从环境变量或FastMCP获取配置
        if hasattr(mcp, 'config') and mcp.config and 'token' in mcp.config:
            return mcp.config['token']
        
        # 尝试从主目录的.cursor/mcp.json读取配置
        config_path = os.path.expanduser("~/.cursor/mcp.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                if 'mcpServers' in config and server_id in config['mcpServers']:
                    server_config = config['mcpServers'][server_id]
                    if 'config' in server_config and 'token' in server_config['config']:
                        return server_config['config']['token']
    except Exception as e:
        print(f"获取配置token失败: {str(e)}，使用默认token")
    
    return default_token

@mcp.tool()
def get_ad_count_list(
    token: str = None,
    version: str = "0.1.79", 
    appid: str = "59",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    zhibiao_list: Optional[List[str]] = None,
    media: Optional[List[str]] = None,
    group_key: Optional[str] = None,
    toushou: Optional[List[str]] = None,
    self_cid: Optional[List[str]] = None,
    ji_hua_id: Optional[List[str]] = None,
    ji_hua_name: Optional[str] = None,
    ad_status: Optional[List[str]] = None,
    creative_id: Optional[List[str]] = None,
    vp_adgroup_id: Optional[List[str]] = None,
) -> dict:
    """
    广告数据相关功能，包括查询广告数据、获取指标列表和媒体列表等。
    **重要提示**：
    1.如过用户没有指定指标要求,指标默认显式入参51个指标。
    2.如果用户只查询一天，需要把开始时间和结束时间都设为同一天。
    
    参数:
        token (str): 请求token
        version (str): 系统版本
        appid (str): 游戏ID，默认为"59"(正统三国)
        start_time (str): 开始时间，格式YYYY-MM-DD，例如:2025-06-24。
        end_time (str): 结束时间，格式YYYY-MM-DD，例如:2025-06-24。
        zhibiao_list (list): 需要查询的指标列表，必填，可选参数有：日期、创角成本、新增创角、广告计划名称、创意名称、项目名称、广告状态、备注、新增注册、创角率、点击率、激活率、点击成本、活跃用户、曝光次数、千次展现均价、点击数、一阶段花费、二阶段花费、当日充值、当日付费次数、当日充值人数、新增付费人数、首充付费人数、首充付费次数、老用户付费人数、新增付费金额、首充付费金额、老用户付费金额、新增付费率、活跃付费率、活跃arppu、新增arppu、小游戏注册首日广告变现金额、小游戏注册首日广告变现ROI、当月注册用户充值金额、消耗、新增付费成本、付费成本、注册成本、首日ROI、累计ROI、分成后首日ROI、分成后累计ROI、付费首日ROI、付费累计ROI、付费分成后首日ROI、付费分成后累计ROI、计算累计ROI所用金额、计算累计ROI所用消耗、24小时ROI。例如["日期","创角成本","新增创角"]代表查询日期、创角成本、新增创角三个指标。默认为["日期", "创角成本", "新增创角", "广告计划名称", "创意名称", "项目名称", "广告状态", "备注", "新增注册", "创角率", "点击率", "激活率", "点击成本", "活跃用户", "曝光次数", "千次展现均价", "点击数", "一阶段花费", "二阶段花费", "当日充值", "当日付费次数", "当日充值人数", "新增付费人数", "首充付费人数", "首充付费次数", "老用户付费人数", "新增付费金额", "首充付费金额", "老用户付费金额", "新增付费率", "活跃付费率", "活跃arppu", "新增arppu", "小游戏注册首日广告变现金额", "小游戏注册首日广告变现ROI", "当月注册用户充值金额", "消耗", "新增付费成本", "付费成本", "注册成本", "首日ROI", "累计ROI", "分成后首日ROI", "分成后累计ROI", "付费首日ROI", "付费累计ROI", "付费分成后首日ROI", "付费分成后累计ROI", "计算累计ROI所用金额", "计算累计ROI所用消耗", "24小时ROI"]。
        media (list): 媒体列表，选填，可选值有:全选(全选)、sphdr(视频号达人)、bd(百度)、xt(星图)、bdss(百度搜索)、gdt(广点通)、bz(b站)、zh(知乎)、dx(抖小广告量)、tt(今日头条)、uc(uc)、gg(谷歌)、nature(自然量)。例如:["gdt"]代表广点通。默认为空。
        group_key (str): 分组键，选填，枚举值：vp_advert_pitcher_id(投手)、dt_vp_fx_cid(self_cid)、vp_adgroup_id(项目id)、vp_advert_channame(媒体)、vp_campaign_id(广告id)、vp_originality_id(创意id)。例如:"vp_campaign_id"按广告ID分组。默认为空。
        toushou(list): 投手列表，选填，可选值有:lll(李霖林), dcx(戴呈翔), yxr(尹欣然), syf(施逸风), gyy(郭耀月), zp(张鹏)，zmn(宗梦男)。例如:["lll"]代表李霖林投手。默认为空。
        self_cid(list): 广告cid，选填，可选值有:ztsg_gdt_lll_3342,ztsg_xt_zp_1,yhzj_bdss_zp_01等参数。例如:["ztsg_gdt_lll_3342"，"ztsg_xt_zp_1"]代表正统三国广点通李霖林3342号广告和正统三国星图张鹏1号广告。默认为空。
        ji_hua_id(list): 广告id，选填，可选值有:41910413241,40159842292等参数。例如:["41910413241"，"40159842292"]代表41910413241号广告和40159842292号广告。默认为空。
        ji_hua_name(str): 广告名称，选填，可选值有:0617-公众号-首次付费2000-男-23,首次付费-20230628-正统三国-谢雨-HB-谢雨-1等参数。例如:"02-0515-站内-词包1-双出价-3977"代表广告名为"02-0515-站内-词包1-双出价-3977"的广告。默认为空。
        ad_status(list): 广告状态，选填，可选值有:ADGROUP_STATUS_FROZEN(已冻结), ADGROUP_STATUS_SUSPEND(暂停中), ADGROUP_STATUS_DELETED(已删除), ADGROUP_STATUS_NOT_IN_DELIVERY_TIME(广告未到投放时间), ADGROUP_STATUS_ACTIVE(投放中), ADGROUP_STATUS_ACCOUNT_BALANCE_NOT_ENOUGH(账户余额不足), ADGROUP_STATUS_DAILY_BUDGET_REACHED(广告达到日预算上限), ADGROUP_STATUS_STOP(投放结束)。例如:["ADGROUP_STATUS_STOP"，"ADGROUP_STATUS_ACTIVE"]代表投放结束状态的广告和投放中状态的广告。默认为空。
        creative_id(list): 创意id，选填，可选值有:413241,40159842292等参数。例如:["12"，"87"]代表12号创意和87号创意。默认为空。
        vp_adgroup_id(list): 项目id，选填可选值有:0,159842等参数。例如:["0"，"159842"]代表0号项目和159842号项目。默认为空。
    返回:
        dict: API响应数据或配置数据
    """
    
    # 如果没有提供token，从配置中获取
    if token is None:
        token = get_token_from_config()
    
    # 设置默认值
    if start_time is None:
        # 默认查询昨天的数据
        yesterday = datetime.now() - timedelta(days=1)
        start_time = yesterday.strftime("%Y-%m-%d")
    
    if end_time is None:
        # 默认查询到今天
        end_time = datetime.now().strftime("%Y-%m-%d")
    if zhibiao_list is None:
        zhibiao_list = ["日期", "创角成本", "新增创角", "广告计划名称", "创意名称", "项目名称", "广告状态", "备注", "新增注册", "创角率", "点击率", "激活率", "点击成本", "活跃用户", "曝光次数", "千次展现均价", "点击数", "一阶段花费", "二阶段花费", "当日充值", "当日付费次数", "当日充值人数", "新增付费人数", "首充付费人数", "首充付费次数", "老用户付费人数", "新增付费金额", "首充付费金额", "老用户付费金额", "新增付费率", "活跃付费率", "活跃arppu", "新增arppu", "小游戏注册首日广告变现金额", "小游戏注册首日广告变现ROI", "当月注册用户充值金额", "消耗", "新增付费成本", "付费成本", "注册成本", "首日ROI", "累计ROI", "分成后首日ROI", "分成后累计ROI", "付费首日ROI", "付费累计ROI", "付费分成后首日ROI", "付费分成后累计ROI", "计算累计ROI所用金额", "计算累计ROI所用消耗", "24小时ROI"]

    # API接口地址
    url = "https://bi.dartou.com/testapi/ad/GetAdCountList"
    
    # 设置请求头
    headers = {
        "X-Token": token,
        "X-Ver": version,
        "Content-Type": "application/json"
    }
    
    # 构建请求体
    payload = {
        "appid": appid,
        "start_time": start_time,
        "end_time": end_time,
        "zhibiao_list": zhibiao_list,
        "media": media,
        "group_key": group_key,
        "toushou": toushou,
        "self_cid": self_cid,
        "ji_hua_id": ji_hua_id,
        "ji_hua_name": ji_hua_name,
        "ad_status": ad_status,
        "creative_id": creative_id,
        "vp_adgroup_id": vp_adgroup_id
    }
    
    
    try:
        # 发送POST请求
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # 解析响应
        result = response.json()
        
        # 检查响应状态
        if result.get("code") == 0:
            print("请求成功!")
            return result
        else:
            print(f"请求失败: {result.get('msg')}")
            return result
    
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return {"code": -1, "msg": str(e)}


def main() -> None:
    mcp.run(transport="stdio") 
