"""
OCR 전처리 효과 비교 (A/B) 테스트 — 실제 촬영 이미지

원본 이미지 vs 전처리(Grayscale + Contrast) 이미지의 OCR 결과를 비교합니다.
실제 사용자가 촬영할 법한 약봉지 사진으로 테스트합니다.

사용법:
  cd backend
  uv run python scripts/test_ocr_compare_real.py
"""

import asyncio
import json
import math
import os
import struct
import sys
import tempfile
import time
import zlib

from fastapi import UploadFile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tortoise import Tortoise

from app.db.databases import TORTOISE_ORM
from app.services.ocr_service import analyze_prescription_via_clova, upload_image_to_s3

# ──────────────────────────────────────────────
# 설정
# ──────────────────────────────────────────────
TEST_IMAGE_PATH = "/Users/admin/PycharmProjects/8_project/backend/ocr_test_image/image 복사본.png"

# 처방전에 있어야 하는 약물 정답 (Ground Truth) — 이미지에서 확인된 5종
GROUND_TRUTH = {
    "medications": [
        {"name": "펠루비정", "full_name": "펠루비정(펠루비프로)", "category": "비스테로이드성 소염진통제"},
        {"name": "베타디온정", "full_name": "베타디온정(베포타스", "category": "항히스타민 & 항알러지약"},
        {"name": "레보드롭정", "full_name": "레보드롭정(레보드로", "category": "진해거담제 & 기침감기약"},
        {"name": "모티리톤정", "full_name": "모티리톤정_(현호색·", "category": "위장운동조절 및 진경제"},
        {"name": "삼아탄통액", "full_name": "삼아탄통액(벤지다민", "category": "구내염, 구강살균소독제"},
    ]
}


# ──────────────────────────────────────────────
# 순수 Python PNG 읽기/쓰기
# ──────────────────────────────────────────────
def read_png(file_path: str) -> tuple[int, int, list[list[tuple[int, int, int, int]]]]:
    """PNG 파일을 읽어 (width, height, pixels) 반환."""
    with open(file_path, "rb") as f:
        data = f.read()

    assert data[:8] == b"\x89PNG\r\n\x1a\n", "유효한 PNG 파일이 아닙니다."

    chunks = []
    pos = 8
    while pos < len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        chunk_type = data[pos + 4 : pos + 8]
        chunk_data = data[pos + 8 : pos + 8 + length]
        chunks.append((chunk_type, chunk_data))
        pos += 12 + length

    ihdr_data = [c[1] for c in chunks if c[0] == b"IHDR"][0]
    width, height, bit_depth, color_type = struct.unpack(">IIBB", ihdr_data[:10])
    assert bit_depth == 8, f"8비트 PNG만 지원합니다 (현재: {bit_depth}비트)"

    idat_data = b"".join(c[1] for c in chunks if c[0] == b"IDAT")
    raw = zlib.decompress(idat_data)

    if color_type == 2:
        channels = 3
    elif color_type == 6:
        channels = 4
    elif color_type == 0:
        channels = 1
    elif color_type == 4:
        channels = 2
    else:
        raise ValueError(f"지원하지 않는 PNG color_type: {color_type}")

    stride = 1 + width * channels
    pixels = []
    prev_row = bytes(width * channels)

    for y in range(height):
        row_start = y * stride
        filter_type = raw[row_start]
        row_data = bytearray(raw[row_start + 1 : row_start + stride])

        for x in range(len(row_data)):
            a = row_data[x - channels] if x >= channels else 0
            b = prev_row[x]
            c = prev_row[x - channels] if x >= channels else 0

            if filter_type == 0:
                pass
            elif filter_type == 1:
                row_data[x] = (row_data[x] + a) & 0xFF
            elif filter_type == 2:
                row_data[x] = (row_data[x] + b) & 0xFF
            elif filter_type == 3:
                row_data[x] = (row_data[x] + (a + b) // 2) & 0xFF
            elif filter_type == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                row_data[x] = (row_data[x] + pr) & 0xFF

        prev_row = bytes(row_data)

        row_pixels = []
        for x in range(width):
            offset = x * channels
            if channels == 4:
                row_pixels.append((row_data[offset], row_data[offset + 1], row_data[offset + 2], row_data[offset + 3]))
            elif channels == 3:
                row_pixels.append((row_data[offset], row_data[offset + 1], row_data[offset + 2], 255))
            elif channels == 1:
                v = row_data[offset]
                row_pixels.append((v, v, v, 255))
            elif channels == 2:
                v = row_data[offset]
                row_pixels.append((v, v, v, row_data[offset + 1]))
        pixels.append(row_pixels)

    return width, height, pixels


def write_png(file_path: str, width: int, height: int, pixels: list[list[tuple[int, int, int, int]]]):
    """RGBA pixels를 PNG 파일로 저장."""
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            r, g, b, a = pixels[y][x]
            raw.extend([r, g, b, a])

    compressed = zlib.compress(bytes(raw))

    def make_chunk(chunk_type: bytes, data: bytes) -> bytes:
        chunk = chunk_type + data
        crc = struct.pack(">I", zlib.crc32(chunk) & 0xFFFFFFFF)
        return struct.pack(">I", len(data)) + chunk + crc

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    out = b"\x89PNG\r\n\x1a\n"
    out += make_chunk(b"IHDR", ihdr)
    out += make_chunk(b"IDAT", compressed)
    out += make_chunk(b"IEND", b"")

    with open(file_path, "wb") as f:
        f.write(out)


# ──────────────────────────────────────────────
# 전처리 함수
# ──────────────────────────────────────────────
def preprocess_grayscale_contrast(pixels, width, height, contrast=30):
    """Grayscale + Contrast 전처리"""
    factor = (259 * (contrast + 255)) / (255 * (259 - contrast))
    result = []
    for y in range(height):
        row = []
        for x in range(width):
            r, g, b, a = pixels[y][x]
            gray = 0.2126 * r + 0.7152 * g + 0.0722 * b
            v = max(0, min(255, round(factor * (gray - 128) + 128)))
            row.append((v, v, v, a))
        result.append(row)
    return result


# ──────────────────────────────────────────────
# 비교 분석
# ──────────────────────────────────────────────
def calculate_match_score(extracted: list[dict], ground_truth: list[dict]) -> dict:
    """추출 결과를 Ground Truth와 비교."""
    matched = 0
    match_details = []

    for gt in ground_truth:
        gt_name = gt["name"]
        found = False
        for ext in extracted:
            ext_name = ext.get("name", "")
            # 부분 매칭: GT 이름이 추출 이름에 포함되거나 그 반대
            if gt_name in ext_name or ext_name in gt_name or (len(gt_name) >= 3 and gt_name[:3] in ext_name):
                matched += 1
                found = True
                match_details.append({
                    "gt_name": gt["name"],
                    "ext_name": ext_name,
                    "matched": True,
                })
                break
        if not found:
            match_details.append({
                "gt_name": gt["name"],
                "ext_name": "(누락)",
                "matched": False,
            })

    extra = max(0, len(extracted) - len(ground_truth))

    return {
        "total_gt": len(ground_truth),
        "matched": matched,
        "recall": matched / len(ground_truth) if ground_truth else 0,
        "precision": matched / len(extracted) if extracted else 0,
        "extra_extracted": extra,
        "details": match_details,
    }


def print_divider(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


async def run_ocr_test(image_path: str, label: str) -> dict | None:
    """이미지를 S3에 업로드하고 OCR 실행."""
    file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
    print(f"  • 이미지: {os.path.basename(image_path)} ({file_size_mb:.2f} MB)")

    try:
        file_name = os.path.basename(image_path)
        file_bytes = open(image_path, "rb").read()

        with tempfile.SpooledTemporaryFile() as tmp:
            tmp.write(file_bytes)
            tmp.seek(0)
            upload_file = UploadFile(filename=file_name, file=tmp)
            s3_url = await upload_image_to_s3(upload_file)

        print(f"  • S3 업로드: ✅ 완료")

        ocr_start = time.time()
        raw_json, parsed_medications = await analyze_prescription_via_clova(s3_url)
        ocr_time = time.time() - ocr_start

        print(f"  • OCR 분석: ✅ 완료 ({ocr_time:.1f}초)")
        print(f"  • 추출 약물 수: {len(parsed_medications)}개")

        for i, med in enumerate(parsed_medications, 1):
            print(f"    {i}. {med.name} | {med.dosage} | {med.frequency} | {med.timing}")

        return {
            "time": ocr_time,
            "medications": [
                {
                    "name": m.name,
                    "dosage": m.dosage,
                    "frequency": m.frequency,
                    "timing": m.timing,
                    "description": m.description or "",
                }
                for m in parsed_medications
            ],
        }
    except Exception as e:
        print(f"  ❌ {label} 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


async def run_comparison():
    """원본 vs 전처리 이미지 OCR 비교 테스트"""
    print("\n🔬 OCR 전처리 효과 A/B 비교 테스트 (실제 촬영 이미지)")
    print("   원본(사진) vs 전처리(Grayscale+Contrast)")
    print(f"   테스트 이미지: {os.path.basename(TEST_IMAGE_PATH)}")

    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"  ❌ 테스트 이미지 없음: {TEST_IMAGE_PATH}")
        return

    # Ground Truth 출력
    print(f"\n  📋 정답 약물 ({len(GROUND_TRUTH['medications'])}종):")
    for i, gt in enumerate(GROUND_TRUTH["medications"], 1):
        print(f"    {i}. {gt['name']} — {gt['category']}")

    # ── A: 원본 ──
    print_divider("테스트 A: 원본 이미지 (전처리 없음)")
    result_a = await run_ocr_test(TEST_IMAGE_PATH, "원본")

    # ── B: 전처리 ──
    print_divider("테스트 B: 전처리 이미지 (Grayscale + Contrast 30)")
    print("  ⏳ 전처리 적용 중...")
    preprocess_start = time.time()
    width, height, pixels = read_png(TEST_IMAGE_PATH)
    processed_pixels = preprocess_grayscale_contrast(pixels, width, height, contrast=30)
    preprocess_time = time.time() - preprocess_start
    print(f"  • 전처리 소요 시간: {preprocess_time:.2f}초 (Python — 브라우저에선 ~20ms)")

    preprocessed_path = os.path.join(
        os.path.dirname(TEST_IMAGE_PATH),
        "image_preprocessed.png",
    )
    write_png(preprocessed_path, width, height, processed_pixels)
    preprocessed_size = os.path.getsize(preprocessed_path) / (1024 * 1024)
    print(f"  • 전처리 이미지 저장: {preprocessed_path} ({preprocessed_size:.2f} MB)")

    result_b = await run_ocr_test(preprocessed_path, "전처리")

    # ── 비교 ──
    if result_a and result_b:
        print_divider("📊 비교 결과")

        score_a = calculate_match_score(result_a["medications"], GROUND_TRUTH["medications"])
        score_b = calculate_match_score(result_b["medications"], GROUND_TRUTH["medications"])

        print(f"\n  {'항목':<24} {'A (원본)':>14} {'B (전처리)':>14} {'비교':>10}")
        print(f"  {'─'*62}")
        print(f"  {'추출 약물 수':<22} {len(result_a['medications']):>12}개 {len(result_b['medications']):>12}개 {'':>10}")
        print(f"  {'정답 매칭 수':<22} {score_a['matched']:>12}개 {score_b['matched']:>12}개 {'':>10}")

        recall_a = f"{score_a['recall']*100:.0f}%"
        recall_b = f"{score_b['recall']*100:.0f}%"
        recall_diff = score_b['recall'] - score_a['recall']
        recall_comp = f"+{recall_diff*100:.0f}%" if recall_diff > 0 else f"{recall_diff*100:.0f}%" if recall_diff < 0 else "동일"
        print(f"  {'재현율 (Recall)':<22} {recall_a:>12} {recall_b:>12} {recall_comp:>10}")

        prec_a = f"{score_a['precision']*100:.0f}%"
        prec_b = f"{score_b['precision']*100:.0f}%"
        prec_diff = score_b['precision'] - score_a['precision']
        prec_comp = f"+{prec_diff*100:.0f}%" if prec_diff > 0 else f"{prec_diff*100:.0f}%" if prec_diff < 0 else "동일"
        print(f"  {'정밀도 (Precision)':<22} {prec_a:>12} {prec_b:>12} {prec_comp:>10}")

        time_a = f"{result_a['time']:.1f}초"
        time_b = f"{result_b['time']:.1f}초"
        time_diff = result_b['time'] - result_a['time']
        time_comp = f"+{time_diff:.1f}초" if time_diff > 0 else f"{time_diff:.1f}초"
        print(f"  {'OCR 처리 시간':<22} {time_a:>12} {time_b:>12} {time_comp:>10}")

        orig_size = os.path.getsize(TEST_IMAGE_PATH) / (1024 * 1024)
        print(f"  {'파일 크기':<22} {orig_size:>10.2f}MB {preprocessed_size:>10.2f}MB {'':>10}")
        print(f"  {'과잉 추출':<22} {score_a['extra_extracted']:>12}개 {score_b['extra_extracted']:>12}개 {'':>10}")

        # 세부 매칭
        print(f"\n  📋 약물별 매칭 상세:")
        print(f"  {'─'*62}")
        for i, gt_med in enumerate(GROUND_TRUTH["medications"]):
            gt_name = gt_med["name"]
            detail_a = score_a["details"][i]
            detail_b = score_b["details"][i]
            status_a = "✅" if detail_a["matched"] else "❌"
            status_b = "✅" if detail_b["matched"] else "❌"
            print(f"  {gt_name} ({gt_med['category']})")
            print(f"    A: {status_a} → {detail_a['ext_name']}")
            print(f"    B: {status_b} → {detail_b['ext_name']}")

        # 최종 판정
        print_divider("🏆 최종 판정")
        if score_b["recall"] > score_a["recall"]:
            diff_pct = (score_b["recall"] - score_a["recall"]) * 100
            print(f"  전처리(B)가 원본(A)보다 ✅ 재현율이 +{diff_pct:.0f}% 향상!")
            print("  → 실제 촬영 환경에서 전처리가 효과적입니다.")
        elif score_b["recall"] < score_a["recall"]:
            diff_pct = (score_a["recall"] - score_b["recall"]) * 100
            print(f"  전처리(B)가 원본(A)보다 ⚠️ 재현율이 -{diff_pct:.0f}% 하락")
            print("  → 이 이미지에서는 전처리가 역효과입니다.")
        else:
            print("  재현율 동일.")
            if score_b["precision"] > score_a["precision"]:
                print("  전처리(B)가 정밀도 면에서 더 나음 ✅")
            elif score_b["precision"] < score_a["precision"]:
                print("  전처리(B)가 정밀도 면에서 더 낮음 ⚠️")
            else:
                print("  정밀도도 동일 — 전처리 효과 없음")

        # JSON 저장
        comparison = {
            "test_image": os.path.basename(TEST_IMAGE_PATH),
            "image_type": "실제 촬영 (약봉지 사진)",
            "ground_truth_count": len(GROUND_TRUTH["medications"]),
            "A_original": {
                "extracted_count": len(result_a["medications"]),
                "recall": score_a["recall"],
                "precision": score_a["precision"],
                "time_seconds": result_a["time"],
                "medications": result_a["medications"],
            },
            "B_preprocessed": {
                "extracted_count": len(result_b["medications"]),
                "recall": score_b["recall"],
                "precision": score_b["precision"],
                "time_seconds": result_b["time"],
                "preprocessing": "Grayscale + Contrast(30)",
                "medications": result_b["medications"],
            },
        }
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_ocr_compare_real_result.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(comparison, f, ensure_ascii=False, indent=2)
        print(f"\n  💾 비교 결과 JSON: {output_path}")

    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(run_comparison())
