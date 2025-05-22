import json
import sys
import os
from typing import Dict, List, Any, Set, Tuple

def parse_member_data(member_file: str) -> List[Dict[str, Any]]:
    """解析會員資料檔案，提取需要的欄位"""
    try:
        with open(member_file, 'r', encoding='utf-8') as f:
            members_data = json.load(f)

        # 確保資料是列表格式
        if not isinstance(members_data, list):
            print(f"錯誤：會員資料檔案格式不正確，應為列表格式")
            return []

        # 提取需要的欄位
        cleaned_members = []
        for member in members_data:
            if not isinstance(member, dict):
                continue

            cleaned_member = {
                "id": member.get("id", ""),
                "username": member.get("username", ""),
                "global_name": member.get("global_name", "")
            }
            cleaned_members.append(cleaned_member)

        print(f"成功解析 {len(cleaned_members)} 名會員資料")
        return cleaned_members

    except FileNotFoundError:
        print(f"錯誤：找不到檔案 '{member_file}'")
        return []
    except json.JSONDecodeError:
        print(f"錯誤：檔案 '{member_file}' 不是有效的JSON格式")
        return []
    except Exception as e:
        print(f"錯誤：解析會員資料時發生問題 - {str(e)}")
        return []

def parse_roles_data(roles_file: str) -> List[Dict[str, Any]]:
    """解析角色資料檔案，提取會員ID和擁有的角色"""
    try:
        with open(roles_file, 'r', encoding='utf-8') as f:
            roles_data = json.load(f)

        # 確保資料有正確的結構
        if not isinstance(roles_data, dict) or "members" not in roles_data:
            print(f"錯誤：角色資料檔案格式不正確，應包含 'members' 欄位")
            return []

        # 提取會員ID和角色資訊
        cleaned_roles = []
        for member_entry in roles_data.get("members", []):
            if not isinstance(member_entry, dict) or "member" not in member_entry:
                continue

            member_data = member_entry.get("member", {})
            user_data = member_data.get("user", {})
            user_id = user_data.get("id", "")

            if not user_id:
                continue

            roles = member_data.get("roles", [])

            cleaned_role = {
                "id": user_id,
                "username": user_data.get("username", ""),
                "global_name": user_data.get("global_name", ""),
                "roles": roles
            }
            cleaned_roles.append(cleaned_role)

        print(f"成功解析 {len(cleaned_roles)} 名會員的角色資料")
        return cleaned_roles

    except FileNotFoundError:
        print(f"錯誤：找不到檔案 '{roles_file}'")
        return []
    except json.JSONDecodeError:
        print(f"錯誤：檔案 '{roles_file}' 不是有效的JSON格式")
        return []
    except Exception as e:
        print(f"錯誤：解析角色資料時發生問題 - {str(e)}")
        return []

def create_role_mapping() -> Dict[str, str]:
    """創建角色ID到角色名稱的映射"""
    role_mapping = {
        "928548848442441749": "呢喃貓",
        "949943973022167050": "雙貓流",
        "940239876526317609": "三隻小貓",
        "1347041467964723230": "四貓打麻將",
        "1347041648080584814": "五貓戰隊",
        "1347041767144554497": "六親不認貓",
        "1347041779500716096": "七貓亂彈琴",
        "1347041932064460900": "八貓大逃殺",
        "928550308731293726": "九mint怪貓",
        "1370051375634841650": "十二金貓"
    }
    return role_mapping

def get_tickets_for_role(role_name: str) -> int:
    """根據角色名稱取得對應的籤數"""
    ticket_mapping = {
        "呢喃貓": 1,
        "雙貓流": 2,
        "三隻小貓": 3,
        "四貓打麻將": 4,
        "五貓戰隊": 5,
        "六親不認貓": 6,
        "七貓亂彈琴": 7,
        "八貓大逃殺": 8,
        "九mint怪貓": 9,
        "十二金貓": 12
    }
    return ticket_mapping.get(role_name, 0)

def combine_data(members: List[Dict[str, Any]], roles: List[Dict[str, Any]],
                role_mapping: Dict[str, str]) -> Dict[str, Any]:
    """將會員資料和角色資料結合，計算籤數"""
    # 將角色資料轉為以ID為鍵的字典，方便查詢
    roles_dict = {role["id"]: role for role in roles}

    # 檢查重複ID
    member_ids = [member["id"] for member in members]
    duplicate_ids = set([id for id in member_ids if member_ids.count(id) > 1])

    if duplicate_ids:
        print(f"警告：在會員資料中發現 {len(duplicate_ids)} 個重複的ID")

    # 合併資料
    result = {
        "total_members": len(members),
        "eligible_members": 0,
        "total_tickets": 0,
        "members": []
    }

    for member in members:
        member_id = member["id"]
        roles_info = roles_dict.get(member_id, {})

        # 獲取該會員的角色列表
        member_roles = roles_info.get("roles", [])

        # 計算該會員的籤數
        max_tickets = 0
        member_role_names = []
        max_role = None

        for role_id in member_roles:
            if role_id in role_mapping:
                role_name = role_mapping[role_id]
                tickets = get_tickets_for_role(role_name)
                member_role_names.append(f"{role_name} ({tickets})")

                if tickets > max_tickets:
                    max_tickets = tickets
                    max_role = role_name

        # 添加會員資料
        display_name = member.get("global_name", "") or member.get("username", "")
        if display_name == "slipknot" or display_name == "slipknot9527":
          display_name = "Dante"

        member_info = {
            "id": member_id,
            "username": member.get("username", ""),
            "global_name": member.get("global_name", ""),
            "display_name": display_name,
            "tickets": max_tickets,
            "max_role": max_role or "無特殊角色",
            "roles": member_role_names,
            "is_duplicate": member_id in duplicate_ids
        }

        result["members"].append(member_info)

        # 更新計數
        if max_tickets > 0:
            result["eligible_members"] += 1
            result["total_tickets"] += max_tickets

    # 按籤數從多到少排序
    result["members"].sort(key=lambda x: x["tickets"], reverse=True)

    return result

def save_data(data: Dict[str, Any], output_file: str) -> None:
    """保存處理後的資料到檔案"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"資料已保存至 {output_file}")
    except Exception as e:
        print(f"保存資料時發生錯誤: {str(e)}")

def save_csv(data: Dict[str, Any], output_file: str) -> None:
    """將會員資料保存為CSV檔案"""
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            f.write("會員名稱,DC ID,籤數,最高等級角色\n")
            for member in data["members"]:
                global_name = member.get("global_name", "") or member.get("display_name", "")
                global_name = global_name.replace(",", "，") if global_name else ""
                username = member.get("username", "").replace(",", "，") if member.get("username") else ""
                tickets = member.get("tickets", 0)
                max_role = member.get("max_role", "無特殊角色")

                if tickets > 0:  # 只輸出有籤數的會員
                    f.write(f"{global_name},{username},{tickets},{max_role}\n")
        print(f"CSV資料已保存至 {output_file}")
    except Exception as e:
        print(f"保存CSV資料時發生錯誤: {str(e)}")

def main():
    print("===== 抽籤資料解析工具 =====")

    # 設定檔案路徑
    member_file = input("請輸入會員資料檔案路徑 (預設: raffle_member.json): ") or "raffle_member.json"
    roles_file = input("請輸入角色資料檔案路徑 (預設: member_role.json): ") or "member_role.json"
    output_file = input("請輸入輸出檔案路徑 (預設: lottery_data.json): ") or "lottery_data.json"
    csv_output = input("請輸入CSV輸出檔案路徑 (預設: lottery_tickets.csv): ") or "lottery_tickets.csv"

    # 解析會員資料
    members = parse_member_data(member_file)
    if not members:
        print("無法繼續：會員資料為空")
        return

    # 解析角色資料
    roles = parse_roles_data(roles_file)
    if not roles:
        print("無法繼續：角色資料為空")
        return

    # 創建角色映射
    role_mapping = create_role_mapping()

    # 合併資料
    result = combine_data(members, roles, role_mapping)

    # 保存結果
    save_data(result, output_file)
    save_csv(result, csv_output)

    # 顯示統計資訊
    print("\n===== 資料統計 =====")
    print(f"總會員數: {result['total_members']}")
    print(f"符合抽獎資格的會員數: {result['eligible_members']}")
    print(f"總籤數: {result['total_tickets']}")

    # 顯示籤數分布
    tickets_distribution = {}
    for member in result["members"]:
        tickets = member["tickets"]
        if tickets > 0:
            tickets_distribution[tickets] = tickets_distribution.get(tickets, 0) + 1

    print("\n籤數分布:")
    for tickets, count in sorted(tickets_distribution.items()):
        print(f"  {tickets}張籤: {count}人")

if __name__ == "__main__":
    main()