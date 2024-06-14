from typing import List

immune_dict = {
    # 免疫「移动力降低」
    "xinbu": ["chihuan", "wucui_chihuan", "shuangdong"],
    "zhetianbiri": [
        "fengmai",
        "xuanyun",
        "jinbi",
        "weiyi",
        "chuansong",
        "fengjin",
        "fengjian",
        "chanli",
        "meihuo",
        "chaofeng",
        "yizhang",
        "nique",
        "mami",
        "duangu",
        "yixin",
        "tichu",
    ],
    "pie": ["fengmai"],
    "pihui": ["wuhui"],
    "zhi": ["juexin"],
    "exin1": ["kongxing", "baonu"],
    "boxunjianglin": ["xinnian"],
    "zhilu": ["juexin"],
    "shengqiangzhili": ["juexingzhili"],
    "wendulengque": ["zhuneng"],
    "chaozai": "hunpozhili",
}

# 阻止获得buff
immune_all_benefit_list: List[str] = ["wuhui"]
immune_all_harm_list: List[str] = [
    "bingqing",
    "tianjiyin",
    "wucui_tianjiyin",
    "fantian",
]
immune_xuanyun_list: List[str] = ["wuyouyu"]

# 免疫buff
prevent_all_benefit_list: List[str] = immune_all_benefit_list + ["duozui"]
prevent_all_harm_list: List[str] = immune_all_harm_list + [""]

# 免疫拉拽
immune_drag_list: List[str] = ["bixian"]

# 免疫物攻降低
immune_physical_attack_reduction_list: List[str] = ["pigong"]
# 免疫法攻降低
immune_physical_magic_reduction_list: List[str] = ["pigong"]
# 免疫物防降低
immune_physical_defense_reduction_list: List[str] = ["pifang"]
# 免疫法防降低
immune_magic_defense_reduction_list: List[str] = ["pifang"]

immune_dict_from_equipment = {
    # 免疫「移动力降低」
    "huanniaojie": ["jinliao"],
}
