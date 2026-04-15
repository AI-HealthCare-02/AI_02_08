import os
import time

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("EYAK_API_KEY")
BASE_URL = "http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"


def fetch_eyak_data(page_no=1, num_of_rows=100):
    params = {"serviceKey": API_KEY, "pageNo": page_no, "numOfRows": num_of_rows, "type": "json"}
    try:
        response = requests.get(BASE_URL, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            items = data.get("body", {}).get("items", [])
            return items if items else []
        return []
    except Exception as e:
        print(f"[{page_no}페이지] 오류: {e}")
        return []


def main():
    output_dir = "data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    all_drugs = []
    page = 1
    rows_per_page = 100

    print("전체 데이터 수집 시작...")

    while True:
        print(f"현재 {page} 페이지 수집 중...", end="\r")  # 한 줄에서 숫자만 변경
        items = fetch_eyak_data(page, rows_per_page)

        if not items:
            print(f"\n{page - 1}페이지에서 수집 완료. 더 이상 데이터가 없습니다.")
            break

        all_drugs.extend(items)
        page += 1
        time.sleep(0.1)  # 4000건 이상이므로 속도를 위해 조금 줄임

    if all_drugs:
        df = pd.DataFrame(all_drugs)
        file_path = os.path.join(output_dir, "eyak_data_raw.csv")
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        print(f"성공! 총 {len(df)}건의 데이터를 '{file_path}'에 저장했습니다.")


if __name__ == "__main__":
    main()
