import random
import time
import os
import sys
import json
import csv

def clear_screen():
    """清除螢幕"""
    os.system('cls' if os.name == 'nt' else 'clear')

def animate_drawing(participants, duration=3):
    """動畫效果的抽獎"""
    # 設定動畫速度
    speed = 0.1
    end_time = time.time() + duration

    print("抽獎開始！")
    print("-" * 30)

    # 動畫效果
    while time.time() < end_time:
        clear_screen()
        # 從加權列表中選擇
        current_selection = random.choice(participants)
        if isinstance(current_selection, tuple):
            display_name = current_selection[0]  # 顯示名稱
        else:
            display_name = current_selection

        print(f"\n\n\n\n{'🎯 抽獎進行中 🎯':^40}")
        print(f"\n{'正在選擇...':^40}")
        print(f"\n{display_name:^40}")
        print(f"\n\n{'*' * 40}")
        time.sleep(speed)

        # 慢慢減緩速度
        if end_time - time.time() < 1:
            speed += 0.03

    # 最終結果
    clear_screen()
    winner = random.choice(participants)
    if isinstance(winner, tuple):
        display_winner = winner[0]  # 顯示名稱
        winner_info = winner[1]     # 其他資訊
    else:
        display_winner = winner
        winner_info = None

    print("\n" + "=" * 50)
    print(f"{'🎉 恭喜！抽獎結果 🎉':^46}")
    print("=" * 50)
    print(f"\n\n{'🏆 獲獎者 🏆':^46}")
    print(f"\n{display_winner:^46}\n")
    if winner_info:
        print(f"{'ID: ' + winner_info.get('id', 'N/A'):^46}\n")
    print("=" * 50)

    return winner

def get_tickets_for_role(role_name):
    """根據角色名稱獲取對應的籤數"""
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

def load_processed_data(data_file):
    """從處理後的JSON檔案載入抽獎資料"""
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, dict) or "members" not in data:
            print(f"錯誤：資料檔案格式不正確，應包含 'members' 欄位")
            return [], set()

        # 獲取會員列表
        members = data.get("members", [])

        # 建立加權名單
        weighted_participants = []
        true_duplicates = set()

        # 處理每個會員
        for member in members:
            user_id = member.get("id", "")
            tickets = member.get("tickets", 0)
            is_duplicate = member.get("is_duplicate", False)

            if is_duplicate and user_id:
                true_duplicates.add(user_id)

            # 跳過沒有籤數的會員
            if tickets <= 0:
                continue

            # 取得會員顯示名稱
            display_name = member.get("display_name", "") or member.get("global_name", "") or member.get("username", "")

            # 添加會員到加權抽獎列表
            for _ in range(tickets):
                weighted_participants.append((display_name, member))

        print(f"從 {data_file} 載入了 {len(weighted_participants)} 張籤，共 {data.get('eligible_members', 0)} 名符合資格的會員")

        return weighted_participants, true_duplicates

    except FileNotFoundError:
        print(f"錯誤：找不到檔案 '{data_file}'")
        return [], set()
    except json.JSONDecodeError:
        print(f"錯誤：檔案 '{data_file}' 不是有效的JSON格式")
        return [], set()
    except Exception as e:
        print(f"錯誤：{str(e)}")
        return [], set()

def verify_fairness(weighted_participants, simulations=10000):
    """驗證抽獎機率的公平性

    通過大量模擬抽獎來檢查每個會員被抽中的機率是否符合其籤數比例
    """
    if not weighted_participants:
        print("沒有參與者，無法驗證公平性")
        return

    # 獲取唯一會員和他們的籤數
    members = {}
    for name, info in weighted_participants:
        if info["id"] not in members:
            members[info["id"]] = {
                "name": name,
                "id": info["id"],
                "tickets": info["tickets"],
                "wins": 0
            }

    # 計算總籤數
    total_tickets = len(weighted_participants)

    # 模擬多次抽獎
    for _ in range(simulations):
        winner = random.choice(weighted_participants)
        winner_id = winner[1]["id"]
        members[winner_id]["wins"] += 1

    # 分析結果
    print(f"\n公平性驗證 (模擬 {simulations} 次抽獎):")
    print("-" * 80)
    print(f"{'會員名稱':<20} {'預期機率':<15} {'實際中獎次數':<15} {'實際機率':<15} {'誤差'}")
    print("-" * 80)

    fairness_results = []

    for member_id, data in members.items():
        expected_prob = data["tickets"] / total_tickets
        actual_prob = data["wins"] / simulations
        error = (actual_prob - expected_prob) / expected_prob * 100 if expected_prob > 0 else 0

        print(f"{data['name']:<20} {expected_prob:.4f} ({data['tickets']}張) {data['wins']:<15} {actual_prob:.4f} {error:+.2f}%")

        fairness_results.append({
            "id": member_id,
            "name": data["name"],
            "tickets": data["tickets"],
            "expected_probability": expected_prob,
            "actual_wins": data["wins"],
            "actual_probability": actual_prob,
            "error_percentage": error
        })

    # 計算平均絕對誤差
    total_error = sum(abs(data["error_percentage"]) for data in fairness_results)
    avg_error = total_error / len(fairness_results) if fairness_results else 0

    print("-" * 80)
    print(f"平均絕對誤差: {avg_error:.2f}%")

    # 保存驗證結果到檔案
    try:
        # 準備JSON格式數據
        fairness_data = {
            "simulation_count": simulations,
            "total_tickets": total_tickets,
            "total_members": len(members),
            "average_absolute_error": avg_error,
            "results": fairness_results
        }

        # 輸出JSON檔案
        with open("fairness_verification.json", "w", encoding="utf-8") as f:
            json.dump(fairness_data, f, ensure_ascii=False, indent=2)

        # 輸出CSV檔案
        with open("fairness_verification.csv", "w", encoding="utf-8", newline='') as f:
            csv_writer = csv.writer(f)
            # 寫入標題
            csv_writer.writerow(["會員名稱", "ID", "籤數", "預期機率", "實際中獎次數", "實際機率", "誤差百分比"])

            # 寫入每個會員的驗證結果
            for result in fairness_results:
                csv_writer.writerow([
                    result["name"],
                    result["id"],
                    result["tickets"],
                    f"{result['expected_probability']:.6f}",
                    result["actual_wins"],
                    f"{result['actual_probability']:.6f}",
                    f"{result['error_percentage']:.2f}%"
                ])

            # 寫入摘要資訊
            csv_writer.writerow([])
            csv_writer.writerow(["模擬次數", simulations])
            csv_writer.writerow(["總籤數", total_tickets])
            csv_writer.writerow(["參與會員數", len(members)])
            csv_writer.writerow(["平均絕對誤差", f"{avg_error:.2f}%"])

        print("公平性驗證結果已保存至 fairness_verification.json 和 fairness_verification.csv")
    except Exception as e:
        print(f"保存驗證結果時發生錯誤: {str(e)}")

    return avg_error < 5  # 如果平均誤差小於5%，認為是公平的

def main():
    try:
        # 檔案路徑設定
        processed_data_file = input("請輸入處理後的抽獎資料JSON檔案路徑 (預設為 lottery_data.json): ")
        if not processed_data_file:
            processed_data_file = "lottery_data.json"

        # 載入處理後的資料
        weighted_participants, true_duplicates = load_processed_data(processed_data_file)

        if not weighted_participants:
            print("錯誤：沒有找到符合條件的參與者或檔案讀取錯誤！")
            return

        # 顯示參與者名單及其籤數
        clear_screen()

        # 使用集合來獲取唯一的參與者
        unique_participants = {}
        for participant, info in weighted_participants:
            user_id = info["id"]
            if user_id not in unique_participants:
                unique_participants[user_id] = info

        # 輸出抽籤資訊到檔案
        try:
            lottery_info = {
                "total_participants": len(unique_participants),
                "total_tickets": len(weighted_participants),
                "participants": [],
                "duplicates": []  # 儲存真正的重複會員資訊
            }

            # 添加所有參與者的資訊
            for user_id, info in unique_participants.items():
                participant_info = {
                    "id": user_id,
                    "display_name": info["display_name"],
                    "username": info["username"],
                    "global_name": info["global_name"],
                    "tickets": info["tickets"],
                    "max_role": info.get("max_role", "無特殊角色"),
                    "all_roles": info["roles"],
                    "is_duplicate": info.get("is_duplicate", False)  # 使用來源標記
                }
                lottery_info["participants"].append(participant_info)

            # 添加重複會員的資訊
            for user_id in true_duplicates:
                if user_id in unique_participants:
                    info = unique_participants[user_id]
                    duplicate_info = {
                        "id": user_id,
                        "display_name": info["display_name"],
                        "username": info["username"],
                        "global_name": info["global_name"],
                        "tickets": info["tickets"],
                        "max_role": info.get("max_role", "無特殊角色"),
                        "all_roles": info["roles"]
                    }
                    lottery_info["duplicates"].append(duplicate_info)

            # 排序參與者列表，籤數多的排前面
            lottery_info["participants"].sort(key=lambda x: x["tickets"], reverse=True)

            # 輸出 JSON 檔案
            with open("lottery_info.json", "w", encoding="utf-8") as f:
                json.dump(lottery_info, f, ensure_ascii=False, indent=2)

            # 輸出 CSV 檔案
            with open("lottery_tickets.csv", "w", encoding="utf-8") as f:
                # 寫入標題
                f.write("會員名稱,DC ID,籤數\n")

                # 寫入每位會員資料
                for participant_info in lottery_info["participants"]:
                    # 使用 global_name 作為會員名稱
                    global_name = participant_info.get("global_name") or participant_info["display_name"]
                    # 處理名稱中的逗號，避免CSV格式錯誤
                    global_name = global_name.replace(",", "，") if global_name else ""
                    username = participant_info["username"].replace(",", "，") if participant_info["username"] else ""

                    f.write(f"{global_name},{username},{participant_info['tickets']}\n")

            print("抽籤資訊已保存至 lottery_info.json\n")
            print("會員籤數已保存至 lottery_tickets.csv\n")
        except Exception as e:
            print(f"保存抽籤資訊時發生錯誤: {str(e)}\n")

        print(f"共有 {len(unique_participants)} 人參與抽獎：")
        if true_duplicates:
            print(f"在來源資料中發現 {len(true_duplicates)} 個重複ID")

        print("-" * 60)
        print(f"{'名稱':<20} {'ID':<20} {'籤數':<5} {'最高等級角色'} {'重複'}")
        print("-" * 60)

        for user_id, info in unique_participants.items():
            is_duplicate = info.get("is_duplicate", False)
            duplicate_mark = "✓" if is_duplicate else ""
            print(f"{info['display_name']:<20} {user_id:<20} {info['tickets']:<5} {info.get('max_role', '無特殊角色')} {duplicate_mark}")

        print("-" * 60)
        print(f"總籤數: {len(weighted_participants)}")

        # 驗證抽獎公平性
        choice = input("\n是否要進行抽獎公平性驗證？(y/n): ")
        if choice.lower() == 'y':
            simulations = 100000
            try:
                sim_input = input(f"請輸入模擬次數 (預設為 {simulations}): ")
                if sim_input.strip():
                    simulations = int(sim_input)
            except ValueError:
                print(f"輸入無效，使用預設模擬次數 {simulations}")

            verify_fairness(weighted_participants, simulations)

        input("\n按下 Enter 開始抽獎...")

        # 執行抽獎動畫
        winner = animate_drawing(weighted_participants)

        # 顯示勝利者詳細資訊
        if isinstance(winner, tuple):
            winner_name, winner_info = winner
            print(f"\n勝利者資訊:")
            print(f"名稱: {winner_name}")
            print(f"ID: {winner_info['id']}")
            print(f"使用者名稱: {winner_info['username']}")
            if winner_info['roles']:
                print(f"角色: {', '.join(winner_info['roles'])}")
            print(f"籤數: {winner_info['tickets']}")
        else:
            print(f"\n再次恭喜 {winner}！")

        # 保存抽獎結果到檔案
        try:
            if isinstance(winner, tuple):
                result = {
                    "winner": {
                        "name": winner_name,
                        "id": winner_info['id'],
                        "username": winner_info['username'],
                        "global_name": winner_info.get('global_name', ''),
                        "tickets": winner_info['tickets'],
                        "max_role": winner_info.get('max_role', '無特殊角色'),
                        "all_roles": winner_info['roles'],
                        "is_duplicate": winner_info.get('is_duplicate', False)
                    },
                    "total_participants": len(unique_participants),
                    "total_tickets": len(weighted_participants),
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                }

                with open("lottery_result.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

                print("\n抽獎結果已保存至 lottery_result.json")
        except Exception as e:
            print(f"\n保存結果時發生錯誤: {str(e)}")

    except KeyboardInterrupt:
        print("\n\n抽獎已取消。")
        sys.exit(0)
    except Exception as e:
        print(f"發生錯誤: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()