from time import time
from random import uniform
from re import findall
from json import dumps
from urllib.parse import urlencode
from requests import session
from lxml import etree
from rsa import strEnc
from info import infos

"""
参考: https://github.com/AxisZql/Automatic-clock-in

0.拿csrfToken、lt、execution https://yqtb.gzhu.edu.cn/infoplus/form/XNYQSB/start
    GET请求

1.可以拿到stepid和问卷url, https://yqtb.gzhu.edu.cn/infoplus/interface/start
    请求POST, 需要携带idc, release, csrfToken, formData, lang

2.可以拿到个人所有信息 https://yqtb.gzhu.edu.cn/infoplus/interface/render
    请求POST, 需要携带stepId, instanceId, admin, rand, width, lang, csrfToken

3.提交问卷 
    https://yqtb.gzhu.edu.cn/infoplus/interface/listNextStepsUsers
        请求POST, 需要携带actionId, formData, rand, nextUsers, stepId, timestamp, boundFields, csfrToken, lang
    
    https://yqtb.gzhu.edu.cn/infoplus/interface/doAction
        请求POST, 需要携带actionId, formData, remark, rand, nextUsers, stepId, timestamp, boundFields, csfrToken, lang

"""


class GZHU(object):
    def __init__(self, username, password):
        """
        初始化
        """
        self.username = str(username)
        self.password = str(password)

        # url接口
        self.urls = {
            'login_url': 'https://newcas.gzhu.edu.cn/cas/login',
            'get_csrfToken': 'https://yqtb.gzhu.edu.cn/infoplus/form/XNYQSB/start',
            'get_wj_url': 'https://yqtb.gzhu.edu.cn/infoplus/interface/start',
            'get_infos': 'https://yqtb.gzhu.edu.cn/infoplus/interface/render',
            'wj_post_1': 'https://yqtb.gzhu.edu.cn/infoplus/interface/listNextStepsUsers',
            'wj_post_2': 'https://yqtb.gzhu.edu.cn/infoplus/interface/doAction'
        }

        # xpath匹配规则
        self.xpath_rules = {
            'lt': '//input[@id="lt"]/@value',
            'csrfToken': '//meta[@itemscope="csrfToken"]/@content',
            'execution': '//input[@name="execution"]/@value'
        }

        self.headers = {
            'Referer': 'https://yqtb.gzhu.edu.cn/infoplus/form/XNYQSB/start',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
        }

        self.rr = session()
        self.csrfToken = ''
        self.stepId = ''

    def login(self):
        """
        登录
        """
        res = self.rr.get(url=self.urls['login_url'])
        html = etree.HTML(res.text)

        lt = html.xpath(self.xpath_rules['lt'])[0]
        execution = html.xpath(self.xpath_rules['execution'])[0]
        rsa = strEnc(self.username + self.password + lt)

        data = {
            'rsa': rsa,
            'ul': len(self.username),
            'pl': len(self.password),
            'lt': lt,
            'execution': execution,
            '_eventId': 'submit',
        }
        res = self.rr.post(url=self.urls['login_url'], data=data)

        if '融合门户' not in res.text:
            return False

        return True

    def get_csrfToken(self):
        """
        从HTML中获取csrfToken
        """
        res_csrfToken = self.rr.post(url=self.urls['get_csrfToken'])

        res_csrfToken_html = etree.HTML(res_csrfToken.text)
        self.csrfToken = res_csrfToken_html.xpath(self.xpath_rules['csrfToken'])[0]
        print('csrfToken是：', self.csrfToken)

    def get_wenjuan_url(self):
        """
        获取问卷url，里面有stepId
        """
        stepid_data = {
            "idc": "XNYQSB",
            "release": "",
            "csrfToken": self.csrfToken,
            "lang": "zh"
        }

        stepid_res = self.rr.post(
            url=self.urls['get_wj_url'],
            data=stepid_data
        )
        print('问卷url：', stepid_res.json().get('entities')[0])
        return stepid_res.json().get('entities')[0]

    def get_infos(self):
        """
        获取个人表单填写信息
        """
        stepurl = self.get_wenjuan_url()
        self.stepId = findall('\d+', stepurl)[0]
        infos_data = {
            "stepId": self.stepId,
            "instanceId": "",
            "admin": "false",
            "rand": uniform(0, 999),
            "width": "1920",
            "lang": "zh",
            "csrfToken": self.csrfToken
        }

        infos_res = self.rr.post(url=self.urls['get_infos'], headers=self.headers, data=infos_data)

        return infos_res.json().get('entities')[0].get('data')

    def post_wenjuan(self, data):
        """
        提交问卷
        """

        """
         "fieldJBXXdrsfwc": '2', 当日是否外出
         "fieldYQJLsfjcqtbl": "2",是否接触过半个月内有疫情重点地区旅居史的人员
         "fieldJKMsfwlm": "1", 健康码是否为绿码
         "fieldCXXXsftjhb": "2",半个月内是否到过国内疫情重点地区
         "fieldCNS": 'true', 确定按钮 
        """

        form = {
            'stepId': self.stepId,
            'actionId': 1,
            'formData':
                {
                    "_VAR_EXECUTE_INDEP_ORGANIZE_Name": data.get('_VAR_EXECUTE_INDEP_ORGANIZE_Name', ''),
                    "_VAR_ACTION_REALNAME": data.get('_VAR_ACTION_REALNAME', ''),
                    "_VAR_EXECUTE_ORGANIZES_Names": data.get('_VAR_EXECUTE_ORGANIZES_Names', ''),
                    "_VAR_RELEASE": data.get('_VAR_RELEASE', ''),
                    "_VAR_NOW_MONTH": str(data.get('_VAR_NOW_MONTH', '')),
                    "_VAR_ACTION_USERCODES": data.get('_VAR_ACTION_USERCODES', ''),
                    "_VAR_ACTION_ACCOUNT": data.get('_VAR_ACTION_ACCOUNT', ''),
                    "_VAR_ACTION_ORGANIZES_Names": data.get('_VAR_ACTION_ORGANIZES_Names', ''),
                    "_VAR_EXECUTE_ORGANIZES_Codes": data.get('_VAR_EXECUTE_ORGANIZES_Codes', ''),
                    "_VAR_PARTICIPANTS": f",{data.get('_VAR_ACTION_USERCODES', '')},",
                    "_VAR_URL_Attr": "{}",
                    "_VAR_EXECUTE_INDEP_ORGANIZES_Names": data.get('_VAR_EXECUTE_INDEP_ORGANIZES_Names', ''),
                    "_VAR_POSITIONS": data.get('_VAR_POSITIONS', ''),
                    "_VAR_EXECUTE_INDEP_ORGANIZES_Codes": data.get('_VAR_EXECUTE_INDEP_ORGANIZES_Codes', ''),
                    "_VAR_EXECUTE_POSITIONS": data.get('_VAR_POSITIONS', ''),
                    "_VAR_ACTION_ORGANIZES_Codes": data.get('_VAR_ACTION_ORGANIZES_Codes', ''),
                    "_VAR_EXECUTE_INDEP_ORGANIZE": data.get('_VAR_EXECUTE_INDEP_ORGANIZE', ''),
                    "_VAR_NOW_YEAR": str(data.get('_VAR_NOW_YEAR', '')),
                    "_VAR_ACTION_INDEP_ORGANIZES_Codes": data.get('_VAR_ACTION_INDEP_ORGANIZES_Codes', ''),
                    "_VAR_ACTION_ORGANIZE": data.get('_VAR_ACTION_ORGANIZE', ''),
                    "_VAR_EXECUTE_ORGANIZE": data.get('_VAR_EXECUTE_ORGANIZE', ''),
                    "_VAR_ACTION_INDEP_ORGANIZE": data.get('_VAR_ACTION_INDEP_ORGANIZE', ''),
                    "_VAR_ACTION_INDEP_ORGANIZE_Name": data.get('_VAR_ACTION_INDEP_ORGANIZE_Name', ''),
                    "_VAR_ACTION_ORGANIZE_Name": data.get('_VAR_ACTION_ORGANIZE_Name', ''),
                    "_VAR_OWNER_ORGANIZES_Codes": data.get('_VAR_OWNER_ORGANIZES_Codes', ''),
                    "_VAR_ADDR": data.get('_VAR_ADDR', ''),
                    "_VAR_OWNER_ORGANIZES_Names": data.get('_VAR_OWNER_ORGANIZES_Names', ''),
                    "_VAR_URL": "https://yqtb.gzhu.edu.cn/infoplus/form/" + self.stepId + "/render",
                    "_VAR_EXECUTE_ORGANIZE_Name": data.get('_VAR_EXECUTE_ORGANIZE_Name'),
                    "_VAR_ACTION_INDEP_ORGANIZES_Names": data.get('_VAR_ACTION_INDEP_ORGANIZES_Names'),
                    "_VAR_OWNER_ACCOUNT": data.get('_VAR_OWNER_ACCOUNT'),
                    "_VAR_STEP_CODE": data.get('_VAR_STEP_CODE'),
                    "_VAR_OWNER_USERCODES": data.get('_VAR_OWNER_USERCODES'),
                    "_VAR_NOW_DAY": data.get('_VAR_NOW_DAY'),
                    "_VAR_OWNER_REALNAME": data.get('_VAR_OWNER_REALNAME'),
                    "_VAR_ENTRY_TAGS": "疫情应用,移动端",
                    "_VAR_NOW": data.get('_VAR_NOW'),  # attention
                    "_VAR_ENTRY_NUMBER": data.get('_VAR_ENTRY_NUMBER'),
                    "_VAR_ENTRY_NAME": "学生健康状况申报_",
                    "_VAR_STEP_NUMBER": data.get('_VAR_STEP_NUMBER'),
                    "fieldFLid": data.get('fieldFLid'),
                    "fieldHQRQ": "",
                    "fieldDQSJ": int(time()),
                    "fieldSQSJ": int(time()),
                    "fieldJBXXxm": data.get('fieldJBXXxm'),
                    "fieldJBXXxm_Name": data.get('fieldJBXXxm_Name'),
                    "fieldJBXXgh": data.get('fieldJBXXgh'),
                    "fieldJBXXnj": data.get('fieldJBXXnj'),
                    "fieldJBXXbj": data.get('fieldJBXXbj'),
                    "fieldJBXXxb": data.get('fieldJBXXxb'),
                    "fieldJBXXxb_Name": data.get('fieldJBXXxb'),
                    "fieldJBXXlxfs": data.get('fieldJBXXlxfs'),
                    "fieldJBXXcsny": data.get('fieldJBXXcsny', ''),
                    "fieldJBXXdw": data.get('fieldJBXXdw'),
                    "fieldJBXXdw_Name": data.get('fieldJBXXdw_Name', ''),
                    "fieldJBXXbz": data.get('fieldJBXXbz', ''),
                    "fieldJBXXbz_Name": data.get('fieldJBXXbz_Name', ''),
                    "fieldJBXXbz_Attr": dumps({"_parent": data.get('fieldJBXXbj', '')}),
                    "fieldJBXXfdy": data.get('fieldJBXXfdy', ''),
                    "fieldJBXXfdy_Name": data.get('fieldJBXXfdy_Name', ''),
                    "fieldJBXXfdy_Attr": f'{{"_parent":"{data.get("fieldJBXXdw", "")}:*"}}',
                    "fieldjgs": data.get('fieldjgs', ''),
                    "fieldjgs_Name": data.get('fieldjgs_Name', ''),
                    "fieldjgshi": data.get('fieldjgshi', ''),
                    "fieldjgshi_Name": data.get('fieldjgshi_Name', ''),
                    "fieldjgshi_Attr": f'{{"_parent":"{data.get("fieldjgs", "")}"}}',
                    "fieldJBXXxnjzbgdz": data.get('fieldJBXXxnjzbgdz', ''),
                    "fieldJBXXJG": data.get('fieldJBXXJG', ''),
                    "fieldJBXXjgs": data.get('fieldJBXXjgs', ''),
                    "fieldJBXXjgs_Name": data.get('fieldJBXXjgs_Name', ''),
                    "fieldJBXXjgshi": data.get('fieldJBXXjgshi', ''),
                    "fieldJBXXjgshi_Name": data.get('fieldJBXXjgshi_Name', ''),
                    "fieldJBXXjgshi_Attr": f'{{"_parent":"{data.get("fieldJBXXjgs", "")}"}}',
                    "fieldJBXXjgq": data.get('fieldJBXXjgq', ''),  # ------------------
                    "fieldJBXXjgq_Name": data.get('fieldJBXXjgq_Name', ''),
                    "fieldJBXXjgq_Attr": f'{{"_parent":"{data.get("fieldJBXXjgshi", "")}"}}',
                    "fieldJBXXjgsjtdz": data.get('fieldJBXXjgsjtdz', ''),
                    "fieldJBXXdrsfwc": '2',  # 当日是否外出
                    "fieldJBXXsheng": data.get('fieldJBXXsheng', ''),
                    "fieldJBXXsheng_Name": data.get('fieldJBXXsheng_Name', ''),
                    "fieldJBXXshi": data.get('fieldJBXXshi', ''),
                    "fieldJBXXshi_Name": data.get('fieldJBXXshi_Name', ''),
                    "fieldJBXXshi_Attr": "{\"_parent\":\"\"}",
                    "fieldJBXXqu": data.get('fieldJBXXqu', ''),
                    "fieldJBXXqu_Name": data.get('fieldJBXXqu_Name', ''),
                    "fieldJBXXqu_Attr": "{\"_parent\":\"\"}",
                    "fieldJBXXqjtxxqk": data.get('fieldJBXXqjtxxqk', ''),
                    "fieldSTQKbrstzk1": data.get('fieldSTQKbrstzk1', ''),
                    "fieldSTQKfs": bool(data.get('fieldSTQKfs', '')),
                    "fieldSTQKks": bool(data.get('fieldSTQKks', '')),
                    "fieldSTQKxm": bool(data.get('fieldSTQKxm', '')),
                    "fieldSTQKfl": bool(data.get('fieldSTQKfl', '')),
                    "fieldSTQKhxkn": bool(data.get('fieldSTQKhxkn', '')),
                    "fieldSTQKfx": bool(data.get('fieldSTQKfx', '')),
                    "fieldSTQKlt": bool(data.get('fieldSTQKlt', '')),
                    "fieldSTQKxjwjjt": bool(data.get('fieldSTQKxjwjjt', '')),
                    "fieldSTQKfxx": bool(data.get('fieldSTQKfxx', '')),
                    "fieldSTQKjmy": bool(data.get('fieldSTQKjmy', '')),
                    "fieldSTQKqt": bool(data.get('fieldSTQKqt', '')),
                    "fieldSTQKqtms": data.get('fieldSTQKqtms', ''),
                    "fieldZJYCHSJCYXJGRQzd": data.get('fieldZJYCHSJCYXJGRQzd', ''),
                    "fieldSTQKfrtw": data.get('fieldSTQKfrtw', ''),
                    "fieldSTQKfrsj": data.get('fieldSTQKfrsj', ''),
                    "fieldSTQKclfs": data.get('fieldSTQKclfs', ''),
                    "fieldSTQKzd": data.get('fieldSTQKzd', ''),
                    "fieldSTQKbrstzk": data.get('fieldSTQKbrstzk', ''),
                    "fieldSTQKglfs": data.get('fieldSTQKglfs', ''),
                    "fieldSTQKgldd": data.get('fieldSTQKgldd', ''),
                    "fieldSTQKglkssj": data.get('fieldSTQKglkssj', ''),
                    "fieldSTQKxgqksm": data.get('fieldSTQKxgqksm', ''),
                    "fieldSTQKzdjgmc": data.get('fieldSTQKzdjgmc', ''),
                    "fieldSTQKzdmc": data.get('fieldSTQKzdmc', ''),
                    "fieldSTQKzdkssj": data.get('fieldSTQKzdkssj', ''),
                    "fieldSTQKzljgmc": data.get('fieldSTQKzljgmc', ''),
                    "fieldSTQKzysj": data.get('fieldSTQKzysj', ''),
                    "fieldSTQKzdjgmcc": data.get('fieldSTQKzdjgmcc', ''),
                    "fieldSTQKpcsj": data.get('fieldSTQKpcsj', ''),
                    "fieldSTQKjtcystzk1": data.get('fieldSTQKjtcystzk1', ''),
                    "fieldSTQKjtcyfs": bool(data.get('fieldSTQKjtcyfs', '')),
                    "fieldSTQKjtcyks": bool(data.get('fieldSTQKjtcyks', '')),
                    "fieldSTQKjtcyxm": bool(data.get('fieldSTQKjtcyxm', '')),
                    "fieldSTQKjtcyfl": bool(data.get('fieldSTQKjtcyfl', '')),
                    "fieldSTQKjtcyhxkn": bool(data.get('fieldSTQKjtcyhxkn', '')),
                    "fieldSTQKjtcyfx": bool(data.get('fieldSTQKjtcyfx', '')),
                    "fieldSTQKjtcylt": bool(data.get('fieldSTQKjtcylt', '')),
                    "fieldSTQKjtcyxjwjjt": bool(data.get('fieldSTQKjtcyxjwjjt', '')),
                    "fieldSTQKjtcyfxx": bool(data.get('fieldSTQKjtcyfxx', '')),
                    "fieldSTQKjtcyjmy": bool(data.get('fieldSTQKjtcyjmy', '')),
                    "fieldSTQKjtcyqt": bool(data.get('fieldSTQKjtcyqt', '')),
                    "fieldSTQKjtcyqtms": "",
                    "fieldSTQKjtcyfrtw": "",
                    "fieldSTQKjtcyfrsj": "",
                    "fieldSTQKjtcyclfs": "",
                    "fieldSTQKjtcyzd": "",
                    "fieldSTQKjtcystzk": "6",
                    "fieldSTQKjtcyglfs": "",
                    "fieldSTQKjtcygldd": "",
                    "fieldSTQKjtcyglkssj": "",
                    "fieldSTQKjtcyzdjgmc": "",
                    "fieldSTQKjtcyzdmc": "",
                    "fieldSTQKjtcyzdkssj": "",
                    "fieldSTQKjtcyzljgmc": "",
                    "fieldSTQKjtcyzysj": "",
                    "fieldSTQKjtcyzdjgmcc": "",
                    "fieldSTQKjtcypcsj": "",
                    "fieldSTQKrytsqkqsm": "",
                    "fieldCXXXszsqsfyyshqzbl": "2",
                    "fieldCXXXqjymsxgqk": "",
                    "fieldCXXXsfjcgyshqzbl": "2",
                    "fieldCXXXksjcsj": "",
                    "fieldCXXXzhycjcsj": "",
                    "fieldJCDDs": "",
                    "fieldJCDDs_Name": "",
                    "fieldJCDDshi": "",
                    "fieldJCDDshi_Name": "",
                    "fieldJCDDshi_Attr": "{\"_parent\":\"\"}",
                    "fieldJCDDq": "",
                    "fieldJCDDq_Name": "",
                    "fieldJCDDq_Attr": "{\"_parent\":\"\"}",
                    "fieldJCDDqmsjtdd": "",
                    "fieldCXXXjcdr": "",
                    "fieldCXXXjcdqk": "",
                    "fieldYQJLsfjcqtbl": "2",  # 是否接触过半个月内有疫情重点地区旅居史的人员
                    "fieldYQJLksjcsj": "",
                    "fieldYQJLzhycjcsj": "",
                    "fieldYQJLjcdry": "",
                    "fieldYQJLjcdds": "",
                    "fieldYQJLjcdds_Name": "",
                    "fieldYQJLjcddshi": "",
                    "fieldYQJLjcddshi_Name": "",
                    "fieldYQJLjcddshi_Attr": "{\"_parent\":\"\"}",
                    "fieldYQJLjcddq": "",
                    "fieldYQJLjcddq_Name": "",
                    "fieldYQJLjcddq_Attr": "{\"_parent\":\"\"}",
                    "fieldYQJLjcdryjkqk": "",
                    "fieldqjymsjtqk": "",
                    "fieldJKMsfwlm": "1",  # 健康码是否为绿码
                    "fieldJKMjt": "",
                    "fieldCXXXsftjhb": "2",  # 半个月内是否到过国内疫情重点地区
                    "fieldCXXXsftjhbjtdz": "",
                    "fieldCXXXsftjhbjtdz_Name": "",
                    "fieldCXXXsftjhbs": "",
                    "fieldCXXXsftjhbs_Name": "",
                    "fieldCXXXsftjhbs_Attr": "{\"_parent\":\"\"}",
                    "fieldCXXXsftjhbq": "",
                    "fieldCXXXsftjhbq_Name": "",
                    "fieldCXXXsftjhbq_Attr": "{\"_parent\":\"\"}",
                    "fieldCXXXddsj": "",
                    "fieldCXXXsfylk": "",
                    "fieldCXXXlksj": "",
                    "fieldSFJZYM": "1",
                    "fieldJZDZC": "3",
                    "fieldYMJZRQzd": data.get('fieldYMJZRQzd', ''),
                    "fieldYMTGSzd": "1",
                    "fieldYMTGSzd_Name": "生物",
                    "fieldYMTGSzdqt": "",
                    "fieldSFJZYMyczd": "",
                    "fieldCNS": True,  # 确认按钮
                    "fieldJKHDDzt": "1",
                    "fieldJKHDDzt_Name": "健康",
                    "fieldzgzjzdzq": "",
                    "fieldzgzjzdzq_Name": "",
                    "fieldzgzjzdzq_Attr": "{\"_parent\":\"\"}",
                    "fieldzgzjzdzjtdz": "",
                    "fieldzgzjzdzshi": "",
                    "fieldzgzjzdzshi_Name": "",
                    "fieldzgzjzdzshi_Attr": "{\"_parent\":\"\"}",
                    "fieldzgzjzdzs": "",
                    "fieldzgzjzdzs_Name": "",
                    "fieldCXXXcxzt": "",
                    "fieldCXXXjtgjbc": "",
                    "fieldCXXXjtfsqtms": "",
                    "fieldCXXXjtfsqt": bool(data.get('fieldCXXXjtfsqt', '')),
                    "fieldCXXXjtfslc": bool(data.get('fieldCXXXjtfslc', '')),
                    "fieldCXXXjtfspc": bool(data.get('fieldCXXXjtfspc', '')),
                    "fieldCXXXjtfsdb": bool(data.get('fieldCXXXjtfsdb', '')),
                    "fieldCXXXjtfshc": bool(data.get('fieldCXXXjtfshc', '')),
                    "fieldCXXXjtfsfj": bool(data.get('fieldCXXXjtfsfj', '')),
                    "fieldCXXXfxcfsj": "",
                    "fieldCXXXcqwdq": "",
                    "fieldCXXXdqszd": "",
                    "fieldCXXXssh": "",
                    "fieldCXXXfxxq": "",
                    "fieldCXXXfxxq_Name": "",
                    "fieldCXXXjtjtzz": "",
                    "fieldCXXXjtzzq": "",
                    "fieldCXXXjtzzq_Name": "",
                    "fieldCXXXjtzzs": "",
                    "fieldCXXXjtzzs_Name": "",
                    "fieldCXXXjtzz": "",
                    "fieldCXXXjtzz_Name": "",
                    "fieldSTQKqtqksm": "",
                    "fieldSHENGYC": data.get('fieldSHENGYC', ''),
                    "fieldYCFDY": data.get('fieldYCFDY', ''),
                    "fieldYCBZ": data.get('fieldYCBZ', ''),
                    "fieldYCBJ": "",
                    "fieldLYYZM": data.get('fieldLYYZM', '')
                },
            'timestamp': int(time()),
            'rand': uniform(0, 999),
            'boundFields': 'fieldSTQKzdjgmc,fieldSTQKjtcyglkssj,fieldYMTGSzd,fieldCXXXsftjhb,fieldzgzjzdzjtdz,fieldJCDDqmsjtdd,fieldSHENGYC,fieldYQJLksjcsj,fieldSTQKjtcyzd,fieldJBXXjgsjtdz,fieldSTQKbrstzk,fieldSTQKfrtw,fieldSTQKjtcyqt,fieldCXXXjtfslc,fieldJBXXlxfs,fieldSTQKxgqksm,fieldSTQKpcsj,fieldJKMsfwlm,fieldJKHDDzt,fieldYQJLsfjcqtbl,fieldYQJLzhycjcsj,fieldSTQKfl,fieldSTQKhxkn,fieldJBXXbz,fieldCXXXsfylk,fieldFLid,fieldjgs,fieldSTQKglfs,fieldCXXXsfjcgyshqzbl,fieldSTQKjtcyfx,fieldCXXXszsqsfyyshqzbl,fieldJCDDshi,fieldSTQKrytsqkqsm,fieldJCDDs,fieldSTQKjtcyfs,fieldSTQKjtcyzljgmc,fieldSQSJ,fieldzgzjzdzs,fieldzgzjzdzq,fieldJZDZC,fieldJBXXnj,fieldSTQKjtcyzdkssj,fieldSTQKfx,fieldSTQKfs,fieldYQJLjcdry,fieldCXXXjtfsdb,fieldCXXXcxzt,fieldYQJLjcddshi,fieldCXXXjtjtzz,fieldCXXXsftjhbs,fieldHQRQ,fieldSTQKjtcyqtms,fieldCXXXksjcsj,fieldSTQKzdkssj,fieldSTQKfxx,fieldSTQKjtcyzysj,fieldjgshi,fieldSTQKjtcyxm,fieldJBXXsheng,fieldZJYCHSJCYXJGRQzd,fieldJBXXdrsfwc,fieldqjymsjtqk,fieldJBXXdw,fieldCXXXjcdr,fieldCXXXsftjhbjtdz,fieldJCDDq,fieldSFJZYM,fieldSTQKjtcyclfs,fieldSTQKxm,fieldCXXXjtgjbc,fieldSTQKjtcygldd,fieldzgzjzdzshi,fieldSTQKjtcyzdjgmcc,fieldSTQKzd,fieldSTQKqt,fieldCXXXlksj,fieldSTQKjtcyfrsj,fieldCXXXjtfsqtms,fieldSTQKjtcyzdmc,fieldCXXXjtfsfj,fieldJBXXfdy,fieldSTQKjtcyjmy,fieldJBXXxm,fieldJKMjt,fieldSTQKzljgmc,fieldCXXXzhycjcsj,fieldCXXXsftjhbq,fieldSTQKqtms,fieldYCFDY,fieldJBXXxb,fieldSTQKglkssj,fieldCXXXjtfspc,fieldSTQKbrstzk1,fieldYCBJ,fieldCXXXssh,fieldSTQKzysj,fieldLYYZM,fieldJBXXgh,fieldCNS,fieldCXXXfxxq,fieldSTQKclfs,fieldSTQKqtqksm,fieldCXXXqjymsxgqk,fieldYCBZ,fieldSTQKjmy,fieldSTQKjtcyxjwjjt,fieldJBXXxnjzbgdz,fieldSTQKjtcyfl,fieldSTQKjtcyzdjgmc,fieldCXXXddsj,fieldSTQKfrsj,fieldSTQKgldd,fieldCXXXfxcfsj,fieldJBXXbj,fieldSTQKjtcyfxx,fieldSTQKks,fieldJBXXcsny,fieldCXXXjtzzq,fieldJBXXJG,fieldCXXXdqszd,fieldCXXXjtzzs,fieldJBXXshi,fieldSTQKjtcyfrtw,fieldSTQKjtcystzk1,fieldCXXXjcdqk,fieldSTQKzdmc,fieldSFJZYMyczd,fieldSTQKjtcyks,fieldSTQKjtcystzk,fieldCXXXjtfshc,fieldYMTGSzdqt,fieldCXXXcqwdq,fieldSTQKxjwjjt,fieldSTQKjtcypcsj,fieldJBXXqu,fieldSTQKlt,fieldYMJZRQzd,fieldJBXXjgshi,fieldYQJLjcddq,fieldYQJLjcdryjkqk,fieldYQJLjcdds,fieldSTQKjtcyhxkn,fieldCXXXjtzz,fieldJBXXjgq,fieldCXXXjtfsqt,fieldJBXXjgs,fieldSTQKjtcylt,fieldSTQKzdjgmcc,fieldJBXXqjtxxqk,fieldDQSJ,fieldSTQKjtcyglfs',
            'csrfToken': self.csrfToken,
            'lang': 'zh',
        }

        end_form = {
            'actionId': 1,
            'formData': form['formData'],
            'remark': '',
            'rand': uniform(0, 9999),
            'nextUsers': {},
            'stepId': self.stepId,
            'timestamp': int(time()),
            'boundFields': 'fieldSTQKzdjgmc,fieldSTQKjtcyglkssj,fieldYMTGSzd,fieldCXXXsftjhb,fieldzgzjzdzjtdz,fieldJCDDqmsjtdd,fieldSHENGYC,fieldYQJLksjcsj,fieldSTQKjtcyzd,fieldJBXXjgsjtdz,fieldSTQKbrstzk,fieldSTQKfrtw,fieldSTQKjtcyqt,fieldCXXXjtfslc,fieldJBXXlxfs,fieldSTQKxgqksm,fieldSTQKpcsj,fieldJKMsfwlm,fieldJKHDDzt,fieldYQJLsfjcqtbl,fieldYQJLzhycjcsj,fieldSTQKfl,fieldSTQKhxkn,fieldJBXXbz,fieldCXXXsfylk,fieldFLid,fieldjgs,fieldSTQKglfs,fieldCXXXsfjcgyshqzbl,fieldSTQKjtcyfx,fieldCXXXszsqsfyyshqzbl,fieldJCDDshi,fieldSTQKrytsqkqsm,fieldJCDDs,fieldSTQKjtcyfs,fieldSTQKjtcyzljgmc,fieldSQSJ,fieldzgzjzdzs,fieldzgzjzdzq,fieldJZDZC,fieldJBXXnj,fieldSTQKjtcyzdkssj,fieldSTQKfx,fieldSTQKfs,fieldYQJLjcdry,fieldCXXXjtfsdb,fieldCXXXcxzt,fieldYQJLjcddshi,fieldCXXXjtjtzz,fieldCXXXsftjhbs,fieldHQRQ,fieldSTQKjtcyqtms,fieldCXXXksjcsj,fieldSTQKzdkssj,fieldSTQKfxx,fieldSTQKjtcyzysj,fieldjgshi,fieldSTQKjtcyxm,fieldJBXXsheng,fieldZJYCHSJCYXJGRQzd,fieldJBXXdrsfwc,fieldqjymsjtqk,fieldJBXXdw,fieldCXXXjcdr,fieldCXXXsftjhbjtdz,fieldJCDDq,fieldSFJZYM,fieldSTQKjtcyclfs,fieldSTQKxm,fieldCXXXjtgjbc,fieldSTQKjtcygldd,fieldzgzjzdzshi,fieldSTQKjtcyzdjgmcc,fieldSTQKzd,fieldSTQKqt,fieldCXXXlksj,fieldSTQKjtcyfrsj,fieldCXXXjtfsqtms,fieldSTQKjtcyzdmc,fieldCXXXjtfsfj,fieldJBXXfdy,fieldSTQKjtcyjmy,fieldJBXXxm,fieldJKMjt,fieldSTQKzljgmc,fieldCXXXzhycjcsj,fieldCXXXsftjhbq,fieldSTQKqtms,fieldYCFDY,fieldJBXXxb,fieldSTQKglkssj,fieldCXXXjtfspc,fieldSTQKbrstzk1,fieldYCBJ,fieldCXXXssh,fieldSTQKzysj,fieldLYYZM,fieldJBXXgh,fieldCNS,fieldCXXXfxxq,fieldSTQKclfs,fieldSTQKqtqksm,fieldCXXXqjymsxgqk,fieldYCBZ,fieldSTQKjmy,fieldSTQKjtcyxjwjjt,fieldJBXXxnjzbgdz,fieldSTQKjtcyfl,fieldSTQKjtcyzdjgmc,fieldCXXXddsj,fieldSTQKfrsj,fieldSTQKgldd,fieldCXXXfxcfsj,fieldJBXXbj,fieldSTQKjtcyfxx,fieldSTQKks,fieldJBXXcsny,fieldCXXXjtzzq,fieldJBXXJG,fieldCXXXdqszd,fieldCXXXjtzzs,fieldJBXXshi,fieldSTQKjtcyfrtw,fieldSTQKjtcystzk1,fieldCXXXjcdqk,fieldSTQKzdmc,fieldSFJZYMyczd,fieldSTQKjtcyks,fieldSTQKjtcystzk,fieldCXXXjtfshc,fieldYMTGSzdqt,fieldCXXXcqwdq,fieldSTQKxjwjjt,fieldSTQKjtcypcsj,fieldJBXXqu,fieldSTQKlt,fieldYMJZRQzd,fieldJBXXjgshi,fieldYQJLjcddq,fieldYQJLjcdryjkqk,fieldYQJLjcdds,fieldSTQKjtcyhxkn,fieldCXXXjtzz,fieldJBXXjgq,fieldCXXXjtfsqt,fieldJBXXjgs,fieldSTQKjtcylt,fieldSTQKzdjgmcc,fieldJBXXqjtxxqk,fieldDQSJ,fieldSTQKjtcyglfs',
            'csrfToken': self.csrfToken,
            'lang': 'zh'
        }

        res1 = self.rr.post(url=self.urls['wj_post_1'], headers=self.headers, data=urlencode(form))
        res2 = self.rr.post(url=self.urls['wj_post_2'], headers=self.headers, data=urlencode(end_form))
        res1 = res1.json()
        res2 = res2.json()
        print('问卷提交1：', res1)
        print('问卷提交1：', res2)
        if res1.get('errno') != 0 and res1.get('ecode') != 'SUCCEED':
            return False

        if res2.get('errno') != 0 and res2.get('ecode') != 'SUCCEED':
            return False

        return True


    def run(self):
        """
        启动
        """
        self.login()  # 登录
        self.get_csrfToken()  # 提取csrfToken
        data = self.get_infos()  # 获取个人信息
        self.post_wenjuan(data)  # 提交问卷


if __name__ == '__main__':
    for stu in infos:
        g = GZHU(stu['sno'], stu['pwd'])
        g.run()
        print(stu['sno'], '打卡成功\n')
