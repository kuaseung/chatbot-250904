import streamlit as st
import pandas as pd
import os
import datetime
import csv

# ---- 페이지 설정 ----
st.set_page_config(page_title="부동산 임장 기록 챗봇 🏢", layout="centered")
st.title("🏠 부동산 임장 기록 챗봇")
st.markdown("<p style='opacity:0.7;'>방문한 부동산 기록을 체계적으로 CSV에 저장할 수 있습니다.</p>", unsafe_allow_html=True)

# ---- 대화 흐름(순차 질문) 설정 ----
# OpenAI 사용 대신 단계별 입력 방식을 사용합니다.
# ---- 세션 상태 초기화 ----
if "step" not in st.session_state:
    st.session_state.step = 0  # 현재 질문 단계 인덱스
if "answers" not in st.session_state:
    st.session_state.answers = {}  # 사용자가 입력한 값 저장
if "saved" not in st.session_state:
    st.session_state.saved = False  # 마지막 저장 완료 상태
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None  # 편집 중인 행 인덱스 (없으면 신규)
if "auto_save" not in st.session_state:
    st.session_state.auto_save = False  # 마지막 단계에서 즉시 저장 트리거

# ---- CSV 파일 경로 ----
csv_file = "real_estate_records.csv"
csv_columns = ["날짜","아파트 이름","주소","관심 평형","부동산 유형","건물 연식","층수",
               "매매가","월세","관리비","대출 가능 여부","교통 편의성","생활 편의시설",
               "개발 호재","내부 상태","외관 상태","안전/보안","예상 수익률",
               "공실 가능성","임대 수요","투자 적합성","개인 코멘트"]

# ---- 저장 데이터 보기(빠른 보기) 버튼 ----
if "show_records_top" not in st.session_state:
    st.session_state.show_records_top = False  # 상단 빠른 보기 토글 초기화
col_top_a, col_top_b = st.columns([0.6, 0.4])
with col_top_b:
    if st.button("📄 저장 데이터 보기", use_container_width=True):
        st.session_state.show_records_top = not st.session_state.get("show_records_top", False)
        st.rerun()

if st.session_state.show_records_top:
    st.markdown("### 📄 저장된 기록 (빠른 보기)")
    if os.path.isfile(csv_file):
        try:
            df_quick = pd.read_csv(csv_file, encoding="utf-8-sig")
            st.dataframe(df_quick, use_container_width=True)
            with open(csv_file, "rb") as f:
                st.download_button("⬇️ CSV 다운로드", f, file_name=csv_file, mime="text/csv")
            st.caption("상세 검색/필터/편집은 페이지 하단의 '현재 저장된 기록' 섹션을 이용하세요.")
        except Exception as e:
            st.error(f"저장된 기록을 불러오지 못했습니다: {e}")
    else:
        st.info("아직 저장된 기록이 없습니다.")

# ---- 질문 메타데이터 (csv_columns와 동일 순서 유지를 권장) ----
scale_opts = ["매우 좋음","좋음","보통","나쁨","모름"]
yn_opts = ["가능","불가","미정"]
type_opts = ["아파트","오피스텔","빌라","주택","상가","토지","기타"]

questions = [
    {"key": "날짜", "label": "방문 날짜", "type": "date", "default": datetime.date.today()},
    {"key": "아파트 이름", "label": "아파트/건물 이름", "type": "text"},
    {"key": "주소", "label": "주소", "type": "text"},
    {"key": "관심 평형", "label": "관심 평형(예: 84m²)", "type": "text"},
    {"key": "부동산 유형", "label": "부동산 유형", "type": "select", "options": type_opts},
    {"key": "건물 연식", "label": "건물 연식(년)", "type": "number", "visible_if": {"key": "부동산 유형", "exclude": ["토지"]}},
    {"key": "층수", "label": "층수", "type": "number", "visible_if": {"key": "부동산 유형", "exclude": ["토지"]}},
    {"key": "매매가", "label": "매매가(만원 단위 추천)", "type": "number"},
    {"key": "월세", "label": "월세(만원)", "type": "number", "visible_if": {"key": "부동산 유형", "exclude": ["토지"]}},
    {"key": "관리비", "label": "관리비(만원)", "type": "number", "visible_if": {"key": "부동산 유형", "exclude": ["토지"]}},
    {"key": "대출 가능 여부", "label": "대출 가능 여부", "type": "select", "options": yn_opts},
    {"key": "교통 편의성", "label": "교통 편의성", "type": "select", "options": scale_opts},
    {"key": "생활 편의시설", "label": "생활 편의시설", "type": "select", "options": scale_opts},
    {"key": "개발 호재", "label": "개발 호재(있다면 간단히)", "type": "text"},
    {"key": "내부 상태", "label": "내부 상태", "type": "select", "options": scale_opts, "visible_if": {"key": "부동산 유형", "exclude": ["토지"]}},
    {"key": "외관 상태", "label": "외관 상태", "type": "select", "options": scale_opts, "visible_if": {"key": "부동산 유형", "exclude": ["토지"]}},
    {"key": "안전/보안", "label": "안전/보안", "type": "select", "options": scale_opts, "visible_if": {"key": "부동산 유형", "exclude": ["토지"]}},
    {"key": "예상 수익률", "label": "예상 수익률(예: 4~5%)", "type": "text"},
    {"key": "공실 가능성", "label": "공실 가능성", "type": "select", "options": scale_opts},
    {"key": "임대 수요", "label": "임대 수요", "type": "select", "options": scale_opts},
    {"key": "투자 적합성", "label": "투자 적합성", "type": "select", "options": ["매우 적합","적합","보통","부적합"]},
    {"key": "개인 코멘트", "label": "개인 코멘트", "type": "textarea"},
]

# 필수 항목 정의 (미입력 시 다음 단계 제한 및 사이드바 표시)
required_keys = {"날짜", "아파트 이름", "주소", "부동산 유형", "매매가"}

# ---- 초기화 버튼 ----
if st.sidebar.button("🧹 입력 초기화"):
    st.session_state.step = 0
    st.session_state.answers = {}
    st.session_state.saved = False
    st.rerun()

# ---- 순차 질문 UI ----
st.markdown("### 💬 오늘 방문한 곳 정보를 단계별로 입력하세요")

current = st.session_state.step
total = len(questions)

# ---- 가시성 규칙 처리 ----
def is_visible(idx: int, answers: dict) -> bool:
    q = questions[idx]
    cond = q.get("visible_if")
    if not cond:
        return True
    ref_key = cond.get("key")
    ref_val = answers.get(ref_key)
    if "include" in cond:
        return ref_val in cond["include"]
    if "exclude" in cond:
        return ref_val not in cond["exclude"]
    return True

def get_visible_indices() -> list:
    return [i for i in range(len(questions)) if is_visible(i, st.session_state.answers)]

# ---- 사이드바 진행 메뉴 (안 2: 그룹핑 + 필수 배지) ----
def _is_filled(key: str, qtype: str, val):
    if val is None:
        return False
    if qtype in ("text", "textarea", "select"):
        return str(val).strip() != ""
    if qtype == "number":
        try:
            return float(val) > 0
        except Exception:
            return False
    if qtype == "date":
        return bool(val)
    return False

# 인덱스 그룹핑 정의 (모든 질문 인덱스 포함)
groups = [
    ("기본 정보", [0, 1, 2, 3, 4]),         # 날짜~유형
    ("건물 정보", [5, 6]),                  # 연식, 층수
    ("금액 정보", [7, 8, 9]),               # 매매가~관리비
    ("상태/입지", [11, 12, 13, 14, 15, 16]),# 교통~안전/보안
    ("투자 판단", [17, 18, 19, 20, 21]),    # 수익률~개인 코멘트
]

# 전체 진행률 계산
filled_count = 0
for i, q in enumerate(questions):
    val = st.session_state.answers.get(q["key"])
    if _is_filled(q["key"], q["type"], val):
        filled_count += 1
progress_ratio = filled_count / total if total else 0

with st.sidebar:
    st.markdown("#### 진행 현황")
    st.progress(progress_ratio)
    st.caption(f"{filled_count}/{total} 완료")

    # 현재 가시성에 따라 필터링된 인덱스만 표시
    visible_set = set(get_visible_indices())
    for group_title, indices in groups:
        st.markdown(f"**{group_title}**")
        for i in indices:
            if i >= total:
                continue
            if i not in visible_set:
                continue
            q = questions[i]
            key = q["key"]
            qtype = q["type"]
            val = st.session_state.answers.get(key, "")
            # 상태 아이콘
            if i == current:
                icon = "●"
            else:
                is_filled = _is_filled(key, qtype, val)
                if is_filled:
                    icon = "✓"
                else:
                    # 과거 단계인데 비어있으면 '건너뜀' 표시, 그 외는 대기
                    icon = "⏭" if i < current else "○"

            # 값 미리보기 (최대 12자)
            preview = str(val)
            if isinstance(val, float) and val.is_integer():
                preview = str(int(val))
            if len(preview) > 12:
                preview = preview[:12] + "…"

            # 필수 배지
            badge = " (필수)" if key in required_keys else ""

            col_a, col_b = st.columns([0.22, 0.78])
            with col_a:
                st.write(icon)
            with col_b:
                if st.button(f"{i+1}. {q['label']}{badge}", key=f"nav_{i}"):
                    st.session_state.step = i
                    st.rerun()
                if preview:
                    st.caption(preview)

visible_indices = get_visible_indices()
if current not in visible_indices and visible_indices:
    # 가시성 변경으로 현재 단계가 숨겨졌다면, 가장 가까운 다음 가시 단계로 이동
    st.session_state.step = visible_indices[0]
    st.rerun()

if visible_indices and current in visible_indices:
    q = questions[current]
    req_badge = " <span style='color:#d9534f'>(필수)</span>" if q["key"] in required_keys else ""
    st.markdown(f"**단계 {current+1}/{total}** — {q['label']}{req_badge}", unsafe_allow_html=True)

    # 기존 입력값 불러오기
    prev_val = st.session_state.answers.get(q["key"], None)

    # 위젯 렌더링
    widget_key = f"q_{current}"
    value = None
    if q["type"] == "text":
        value = st.text_input(q["label"], value=prev_val if isinstance(prev_val, str) else None, key=widget_key)
    elif q["type"] == "textarea":
        value = st.text_area(q["label"], value=prev_val if isinstance(prev_val, str) else None, key=widget_key)
    elif q["type"] == "number":
        value = st.number_input(q["label"], value=float(prev_val) if isinstance(prev_val, (int,float)) else 0.0, step=1.0, key=widget_key)
    elif q["type"] == "select":
        options = q.get("options", [])
        default_index = options.index(prev_val) if (prev_val in options) else 0
        value = st.selectbox(q["label"], options=options, index=default_index, key=widget_key)
    elif q["type"] == "date":
        default_date = prev_val if isinstance(prev_val, datetime.date) else q.get("default", datetime.date.today())
        value = st.date_input(q["label"], value=default_date, key=widget_key)

    # 마지막 가시 단계인지 여부
    is_last_step = (current == max(visible_indices)) if visible_indices else False

    # 버튼 영역 (마지막 단계에서 저장 버튼 추가)
    if is_last_step:
        col1, col2, col3, col4 = st.columns(4)
    else:
        col1, col2, col3 = st.columns(3)

    with col1:
        # 이전 가시 단계로 이동
        prev_vis = [i for i in visible_indices if i < current]
        if st.button("⬅️ 이전", disabled=(len(prev_vis) == 0)):
            st.session_state.step = prev_vis[-1] if prev_vis else current
            st.rerun()

    with col2:
        if st.button("⏭️ 건너뛰기"):
            next_vis = [i for i in visible_indices if i > current]
            st.session_state.step = next_vis[0] if next_vis else current
            st.rerun()

    with col3:
        if st.button("➡️ 다음"):
            # 값 저장 (date는 문자열로 저장)
            if isinstance(value, datetime.date):
                st.session_state.answers[q["key"]] = value.isoformat()
            else:
                st.session_state.answers[q["key"]] = value
            # 필수 검증
            valid = True
            if q["key"] in required_keys:
                v = st.session_state.answers.get(q["key"])
                if q["type"] in ("text", "textarea"):
                    valid = bool(str(v).strip())
                elif q["type"] == "number":
                    # 매매가 등은 0보다 큰 값 권장
                    try:
                        valid = float(v) > 0
                    except Exception:
                        valid = False
                elif q["type"] == "select":
                    valid = v is not None and str(v).strip() != ""
                elif q["type"] == "date":
                    valid = bool(v)
            if not valid:
                st.warning("필수 항목을 입력해 주세요.")
            else:
                next_vis = [i for i in visible_indices if i > current]
                if next_vis:
                    st.session_state.step = next_vis[0]
                else:
                    # 마지막 단계였다면 완료 화면으로 전환되도록 현재를 벗어나게 함
                    st.session_state.step = current + 1
                    st.session_state.auto_save = True
                st.rerun()
    if is_last_step:
        with col4:
            if st.button("💾 저장하기(바로)"):
                # 현재 값 저장 후 유효성 검사, 완료 화면으로 이동하여 자동 저장 진행
                if isinstance(value, datetime.date):
                    st.session_state.answers[q["key"]] = value.isoformat()
                else:
                    st.session_state.answers[q["key"]] = value
                # 필수 검증
                valid = True
                if q["key"] in required_keys:
                    v = st.session_state.answers.get(q["key"])
                    if q["type"] in ("text", "textarea"):
                        valid = bool(str(v).strip())
                    elif q["type"] == "number":
                        try:
                            valid = float(v) > 0
                        except Exception:
                            valid = False
                    elif q["type"] == "select":
                        valid = v is not None and str(v).strip() != ""
                    elif q["type"] == "date":
                        valid = bool(v)
                if not valid:
                    st.warning("필수 항목을 입력해 주세요.")
                else:
                    st.session_state.step = current + 1
                    st.session_state.auto_save = True
                    st.rerun()
elif not visible_indices or current >= max(visible_indices) + 1:
    st.success("모든 항목 입력이 완료되었습니다. 아래 요약을 확인하고 CSV로 저장하세요.")

    # 요약 테이블 생성
    row_values = []
    for col in csv_columns:
        v = st.session_state.answers.get(col, "")
        # 숫자형은 int로 표시 가능
        if isinstance(v, float) and v.is_integer():
            v = int(v)
        row_values.append(v)

    df_preview = pd.DataFrame([row_values], columns=csv_columns)
    st.dataframe(df_preview, use_container_width=True)

    # 마지막 단계에서 '바로 저장'을 누른 경우 자동 저장 처리
    if st.session_state.auto_save:
        try:
            file_exists = os.path.isfile(csv_file)
            if st.session_state.edit_index is not None and os.path.isfile(csv_file):
                df_all = pd.read_csv(csv_file)
                idx = st.session_state.edit_index
                if 0 <= idx < len(df_all):
                    for c, v in zip(csv_columns, row_values):
                        df_all.at[idx, c] = v
                    df_all.to_csv(csv_file, index=False, encoding="utf-8-sig")
                else:
                    with open(csv_file, "a", newline="", encoding="utf-8-sig") as f:
                        writer = csv.writer(f)
                        if not file_exists:
                            writer.writerow(csv_columns)
                        writer.writerow([str(v) if v is not None else "" for v in row_values])
            else:
                with open(csv_file, "a", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        writer.writerow(csv_columns)
                    writer.writerow([str(v) if v is not None else "" for v in row_values])
            st.success("✅ 기록이 CSV에 저장되었습니다!")
            st.session_state.saved = True
            st.session_state.edit_index = None
            st.rerun()
        except Exception as e:
            st.error(f"❌ 저장 중 오류가 발생했습니다: {e}")
        finally:
            st.session_state.auto_save = False

    colA, colB = st.columns(2)
    with colA:
        if st.button("✏️ 수정하기"):
            # 마지막 항목으로 이동하여 필요한 항목 수정하도록 유도
            vis = get_visible_indices()
            st.session_state.step = vis[-1] if vis else 0
            st.rerun()
    with colB:
        if st.button("💾 CSV 저장"):
            try:
                file_exists = os.path.isfile(csv_file)
                # 편집 모드면 해당 행을 업데이트, 아니면 append
                if st.session_state.edit_index is not None and os.path.isfile(csv_file):
                    df_all = pd.read_csv(csv_file)
                    idx = st.session_state.edit_index
                    if 0 <= idx < len(df_all):
                        for c, v in zip(csv_columns, row_values):
                            df_all.at[idx, c] = v
                        df_all.to_csv(csv_file, index=False, encoding="utf-8-sig")
                    else:
                        # 인덱스 범위 밖이면 append
                        with open(csv_file, "a", newline="", encoding="utf-8-sig") as f:
                            writer = csv.writer(f)
                            if not file_exists:
                                writer.writerow(csv_columns)
                            writer.writerow([str(v) if v is not None else "" for v in row_values])
                else:
                    with open(csv_file, "a", newline="", encoding="utf-8-sig") as f:
                        writer = csv.writer(f)
                        if not file_exists:
                            writer.writerow(csv_columns)
                        writer.writerow([str(v) if v is not None else "" for v in row_values])
                st.success("✅ 기록이 CSV에 저장되었습니다!")
                # 저장 완료 상태 표시 후, 신규 매물 추가 버튼 제공
                st.session_state.saved = True
                # 편집 종료
                st.session_state.edit_index = None
                st.rerun()
            except Exception as e:
                st.error(f"❌ 저장 중 오류가 발생했습니다: {e}")

    # 저장 완료 후 신규 매물 추가 흐름
    if st.session_state.saved:
        st.info("저장이 완료되었습니다. 다른 매물을 계속 추가하시겠습니까?")
        if st.button("➕ 신규 매물 추가"):
            st.session_state.step = 0
            st.session_state.answers = {}
            st.session_state.saved = False
            st.rerun()
        # 이전 답변 복사하여 신규 입력 시작 (날짜는 오늘로, 개인 코멘트는 공백)
        if st.button("📋 이전 답변 복사하여 신규 매물"):
            new_answers = {k: v for k, v in zip(csv_columns, row_values)}
            new_answers["날짜"] = datetime.date.today().isoformat()
            new_answers["개인 코멘트"] = ""
            st.session_state.answers = new_answers
            st.session_state.step = 0
            st.session_state.saved = False
            st.rerun()

# ---- CSV 기록 확인 + 필터/검색 + CRUD ----
st.markdown("### 📊 현재 저장된 기록")
if os.path.isfile(csv_file):
    df_records = pd.read_csv(csv_file, encoding="utf-8-sig")

    with st.expander("🔍 검색/필터"):
        colf1, colf2 = st.columns(2)
        with colf1:
            date_from = st.date_input("시작일", value=None, key="flt_from")
        with colf2:
            date_to = st.date_input("종료일", value=None, key="flt_to")
        colf3, colf4 = st.columns(2)
        with colf3:
            type_sel = st.multiselect("유형", options=type_opts, default=[])
        with colf4:
            name_text = st.text_input("이름/주소 검색")
        colf5, colf6 = st.columns(2)
        with colf5:
            price_min = st.number_input("최소 매매가(만원)", value=0, step=100)
        with colf6:
            price_max = st.number_input("최대 매매가(만원)", value=0, step=100)

    # 필터 적용
    df_view = df_records.copy()
    try:
        if date_from is not None:
            df_view = df_view[df_view["날짜"] >= date_from.isoformat()]
        if date_to is not None:
            df_view = df_view[df_view["날짜"] <= date_to.isoformat()]
    except Exception:
        pass
    if type_sel:
        df_view = df_view[df_view["부동산 유형"].isin(type_sel)]
    if name_text:
        m = df_view["아파트 이름"].astype(str).str.contains(name_text, case=False, na=False) | \
            df_view["주소"].astype(str).str.contains(name_text, case=False, na=False)
        df_view = df_view[m]
    if price_min and price_min > 0:
        with pd.option_context('mode.chained_assignment', None):
            df_view["매매가_num"] = pd.to_numeric(df_view["매매가"], errors='coerce')
        df_view = df_view[df_view["매매가_num"] >= price_min]
    if price_max and price_max > 0:
        if "매매가_num" not in df_view.columns:
            with pd.option_context('mode.chained_assignment', None):
                df_view["매매가_num"] = pd.to_numeric(df_view["매매가"], errors='coerce')
        df_view = df_view[df_view["매매가_num"] <= price_max]
    if "매매가_num" in df_view.columns:
        df_view = df_view.drop(columns=["매매가_num"])

    st.dataframe(df_view, use_container_width=True)

    # CRUD 영역
    st.markdown("#### ✏️ 레코드 수정 / 🗑 삭제")
    if not df_records.empty:
        options = [f"{i}: {row['아파트 이름']} | {row['주소']}" for i, row in df_records.iterrows()]
        sel_label = st.selectbox("수정/삭제할 항목 선택", options=options, index=0)
        try:
            sel_index = int(sel_label.split(":", 1)[0])
        except Exception:
            sel_index = 0

        colc1, colc2 = st.columns(2)
        with colc1:
            if st.button("✏️ 선택 항목 수정 로드"):
                # answers에 로드하고 편집 모드로 전환
                rec = df_records.loc[sel_index]
                st.session_state.answers = {c: rec.get(c, "") for c in csv_columns}
                st.session_state.step = 0
                st.session_state.saved = False
                st.session_state.edit_index = sel_index
                st.success("선택한 항목을 편집 모드로 불러왔습니다. 위 입력 단계를 통해 수정 후 저장하세요.")
        with colc2:
            if st.button("🗑 선택 항목 삭제"):
                try:
                    df_after = df_records.drop(index=sel_index)
                    df_after.to_csv(csv_file, index=False, encoding="utf-8-sig")
                    st.success("삭제되었습니다. 새로고침 후 반영됩니다.")
                except Exception as e:
                    st.error(f"삭제 중 오류: {e}")

    try:
        with open(csv_file, "rb") as f:
            st.download_button("⬇️ CSV 다운로드", f, file_name=csv_file, mime="text/csv")
    except Exception:
        pass
else:
    st.info("아직 기록이 없습니다.")
