# korean_text_matcher_package/korean_text_matcher/similarity_matcher.py
import os
import sys
from difflib import SequenceMatcher
import math
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
import numpy as np
import pickle
import subprocess
try:
    from rapidfuzz import fuzz
except:
    subprocess.check_call([sys.executable,'-m', 'pip', 'install', '--upgrade', 'rapidfuzz'])

# from rapidfuzz import process # process 모듈은 지금 당장 필요 없을 수 있음, 필요 시 사용

# --- 상수 정의 ---
CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅝ', 'ㅙ', 'ㅞ', 'ㅛ', 'ㅜ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
JONGSUNG_LIST = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

# --- 전역 변수 (TF-IDF Vectorizer 인스턴스를 저장) ---
# 이제 이 변수는 캐시 파일 경로를 직접 저장하지 않고, Vectorizer 객체 자체를 저장합니다.
_global_tfidf_vectorizer_for_cosine = None
CACHE_DIR = 'cache' # 캐시 파일을 저장할 기본 디렉토리

# --- 헬퍼 함수 (이전과 동일) ---
def _decompose_korean_char(char):
    if not ('가' <= char <= '힣'):
        return char
    char_code = ord(char) - ord('가')
    chosung_idx = char_code // 588
    jungsung_idx = (char_code - (chosung_idx * 588)) // 28
    jongsung_idx = char_code % 28
    if not (0 <= chosung_idx < len(CHOSUNG_LIST) and
            0 <= jungsung_idx < len(JUNGSUNG_LIST) and
            0 <= jongsung_idx < len(JONGSUNG_LIST)):
        return char
    chosung = CHOSUNG_LIST[chosung_idx]
    jungsung = JUNGSUNG_LIST[jungsung_idx]
    jongsung = JONGSUNG_LIST[jongsung_idx]
    return chosung + jungsung + jongsung if jongsung else chosung + jungsung

def _decompose_korean_string(s):
    if not isinstance(s, str):
        return str(s).strip() if s is not None else ""
    decomposed_chars = []
    for char in s:
        decomposed_chars.append(_decompose_korean_char(char))
    return "".join(decomposed_chars)

def _get_first_meaningful_char_for_weight(s):
    for char in s:
        if '가' <= char <= '힣':
            char_code = ord(char) - ord('가')
            chosung_idx = char_code // 588
            return CHOSUNG_LIST[chosung_idx]
        elif 'a' <= char <= 'z' or 'A' <= char <= 'Z' or '0' <= char <= '9':
            return char.lower()
    return None

def _split_string_by_type(s):
    chunks = []
    if not isinstance(s, str) or not s:
        return chunks
    current_chunk = ""
    current_type = None
    for char in s:
        char_type = None
        if '가' <= char <= '힣':
            char_type = 'korean'
        elif 'a' <= char <= 'z' or 'A' <= char <= 'Z' or '0' <= char <= '9':
            char_type = 'alnum'
        else:
            char_type = 'other'
        
        if current_type is None:
            current_type = char_type
            current_chunk = char
        elif char_type == current_type:
            current_chunk += char
        else:
            chunks.append((current_type, current_chunk))
            current_type = char_type
            current_chunk = char
    if current_chunk:
        chunks.append((current_type, current_chunk))
    return chunks

def _calculate_part_similarity(s1_part, s2_part, part_type, adjust_korean_weights=False):
    if not s1_part and not s2_part:
        return 100
    if not s1_part or not s2_part:
        return 0
    if part_type == 'korean':
        s1_proc = _decompose_korean_string(s1_part.lower())
        s2_proc = _decompose_korean_string(s2_part.lower())
    else:
        s1_proc = s1_part.lower()
        s2_proc = s2_part.lower()
    if not s1_proc and not s2_proc:
        return 100
    if not s1_proc or not s2_proc:
        return 0
    #matcher = SequenceMatcher(None, s1_proc, s2_proc)
    #base_score = 100 * matcher.ratio()
    base_score = fuzz.ratio(s1_proc, s2_proc)
    current_part_adjustment = 0
    if part_type == 'korean' and adjust_korean_weights:
        first_char_s1 = _get_first_meaningful_char_for_weight(s1_part.lower())
        first_char_s2 = _get_first_meaningful_char_for_weight(s2_part.lower())
        if first_char_s1 is not None and first_char_s2 is not None:
            if first_char_s1 == first_char_s2:
                current_part_adjustment += 10
            else:
                current_part_adjustment -= 20
        len_s1_proc = len(s1_proc)
        len_s2_proc = len(s2_proc)
        len_diff_ratio = 0
        if max(len_s1_proc, len_s2_proc) > 0:
            len_diff_ratio = abs(len_s1_proc - len_s2_proc) / max(len_s1_proc, len_s2_proc)
        if len_diff_ratio < 0.1:
            current_part_adjustment += 8 
        elif len_diff_ratio < 0.3:
            current_part_adjustment += 0 
        else:
            current_part_adjustment -= 10 
    return max(0, min(100, base_score + current_part_adjustment))

# --- TF-IDF Vectorizer 초기화 함수 (캐싱 로직 포함) ---
# cache_filename 인수를 추가하여 캐시 파일명을 동적으로 지정할 수 있도록 함
def initialize_tfidf_vectorizer_for_cosine(corpus: list, cache_filename: str = 'tfidf_vectorizer.pkl'):
    """
    TF-IDF Vectorizer를 초기화하고 주어진 코퍼스에 학습시킵니다.
    주어진 cache_filename으로 캐시 파일을 존재하면 로드하고, 없으면 새로 학습시킨 후 파일로 저장합니다.

    Args:
        corpus (list): 학습에 사용할 문서(전처리된 약품명 문자열) 리스트.
        cache_filename (str): TF-IDF Vectorizer를 저장/로드할 캐시 파일의 이름.
                               기본값은 'tfidf_vectorizer.pkl'.
    """
    global _global_tfidf_vectorizer_for_cosine

    # 캐시 파일 경로 설정
    tfidf_cache_file_path = os.path.join(CACHE_DIR, cache_filename)

    # 1. 캐시 파일이 존재하는지 확인
    if os.path.exists(tfidf_cache_file_path):
        print(f"Loading TF-IDF Vectorizer from cache: {tfidf_cache_file_path}")
        try:
            with open(tfidf_cache_file_path, 'rb') as f:
                _global_tfidf_vectorizer_for_cosine = pickle.load(f)
            print("TF-IDF Vectorizer loaded from cache successfully.")
            return
        except Exception as e:
            print(f"Error loading TF-IDF Vectorizer from cache '{tfidf_cache_file_path}': {e}. Re-training...")
            # 캐시 파일 로드 중 오류가 발생하면, 다시 학습하도록 폴백

    # 2. 캐시 파일이 없거나 로드에 실패한 경우, 새로 학습
    print(f"TF-IDF Vectorizer cache '{tfidf_cache_file_path}' not found or corrupted. Training from corpus...")
    if not corpus:
        print("경고: TF-IDF Vectorizer를 학습할 코퍼스가 비어있습니다.")
        _global_tfidf_vectorizer_for_cosine = None
        return

    # analyzer를 _decompose_korean_string으로 설정하여 한글 음소 분해를 벡터화 단계에 통합
    _global_tfidf_vectorizer_for_cosine = TfidfVectorizer(analyzer=_decompose_korean_string, token_pattern=None)
    _global_tfidf_vectorizer_for_cosine.fit(corpus) # 코퍼스에 학습

    print("TF-IDF Vectorizer가 코퍼스에 성공적으로 학습되었습니다.")
    
    # 3. 학습된 Vectorizer를 캐시에 저장
    try:
        os.makedirs(CACHE_DIR, exist_ok=True) # 캐시 디렉토리가 없으면 생성
        with open(tfidf_cache_file_path, 'wb') as f:
            pickle.dump(_global_tfidf_vectorizer_for_cosine, f)
        print(f"TF-IDF Vectorizer saved to cache: {tfidf_cache_file_path}")
    except Exception as e:
        print(f"Error saving TF-IDF Vectorizer to cache '{tfidf_cache_file_path}': {e}")

# --- 문자열을 벡터로 변환하는 헬퍼 함수 ---
def get_tfidf_vector(text: str):
    global _global_tfidf_vectorizer_for_cosine
    if _global_tfidf_vectorizer_for_cosine is None:
        print("오류: TF-IDF Vectorizer가 초기화되지 않았습니다. `initialize_tfidf_vectorizer_for_cosine`을 먼저 호출하세요.")
        return np.array([]).reshape(0, 0)
    return _global_tfidf_vectorizer_for_cosine.transform([text.lower().strip()])

# --- 다중 벡터의 코사인 유사도를 계산하는 함수 ---
def get_cosine_similarities(query_vector, candidate_vectors_matrix):
    if query_vector.shape[0] == 0 or candidate_vectors_matrix.shape[0] == 0:
        return np.array([])
    similarity_scores = sklearn_cosine_similarity(query_vector, candidate_vectors_matrix)[0]
    return similarity_scores.astype(float)

# --- 메인 유사도 함수 (SequenceMatcher 기반, 변경 없음) ---
def korean_word_matching_ratio(s1, s2):
    s1_str = str(s1).strip() if s1 is not None else ""
    s2_str = str(s2).strip() if s2 is not None else ""
    if not s1_str or not s2_str:
        return 0
    chunks1 = _split_string_by_type(s1_str)
    chunks2 = _split_string_by_type(s2_str)
    total_weighted_score = 0
    total_effective_weight = 0
    
    # SequenceMatcher 대신 rapidfuzz.fuzz.ratio를 사용하기 위해 직접 루프를 돌림
    # chunks1과 chunks2의 순회 및 매칭 로직은 그대로 유지
    chunk_matcher = SequenceMatcher(None, chunks1, chunks2) # 여전히 chunk matching에는 SequenceMatcher가 유용

    for tag, i1_start, i1_end, i2_start, i2_end in chunk_matcher.get_opcodes():
        len_matched_chunks_s1 = i1_end - i1_start
        len_matched_chunks_s2 = i2_end - i2_start
        
        if tag == 'equal':
            for k in range(len_matched_chunks_s1):
                type1, val1 = chunks1[i1_start + k]
                weight_multiplier = 0
                if type1 == 'korean': weight_multiplier = 0.6
                elif type1 == 'alnum': weight_multiplier = 0.3
                else: weight_multiplier = 0.1
                part_score = 100
                current_char_length = max(len(val1), len(val1))
                total_weighted_score += (part_score * weight_multiplier * current_char_length)
                total_effective_weight += (weight_multiplier * current_char_length)
        elif tag == 'replace':
            val1_segment = "".join([c[1] for c in chunks1[i1_start:i1_end]])
            val2_segment = "".join([c[1] for c in chunks2[i2_start:i2_end]])
            segment_type = 'other'
            if any(c[0] == 'korean' for c in chunks1[i1_start:i1_end]) or any(c[0] == 'korean' for c in chunks2[i2_start:i2_end]):
                segment_type = 'korean'
            elif any(c[0] == 'alnum' for c in chunks1[i1_start:i1_end]) or any(c[0] == 'alnum' for c in chunks2[i2_start:i2_end]):
                segment_type = 'alnum'
            weight_multiplier = 0
            if segment_type == 'korean': weight_multiplier = 0.6 
            elif segment_type == 'alnum': weight_multiplier = 0.3
            else: weight_multiplier = 0.1
            
            # _calculate_part_similarity에서 이미 rapidfuzz 사용
            part_score = _calculate_part_similarity(val1_segment, val2_segment, segment_type, adjust_korean_weights=True)
            current_char_length = max(len(val1_segment), len(val2_segment))
            total_weighted_score += (part_score * weight_multiplier * current_char_length)
            total_effective_weight += (weight_multiplier * current_char_length)
        elif tag == 'insert':
            for k_s2 in range(len_matched_chunks_s2):
                type2, val2 = chunks2[i2_start + k_s2]
                weight_multiplier = 0
                if type2 == 'korean': weight_multiplier = 0.6 
                elif type2 == 'alnum': weight_multiplier = 0.3
                else: weight_multiplier = 0.1
                part_score = 0 
                current_char_length = len(val2)
                total_weighted_score += (part_score * weight_multiplier * current_char_length)
                total_effective_weight += (weight_multiplier * current_char_length)
        elif tag == 'delete':
            for k_s1 in range(len_matched_chunks_s1):
                type1, val1 = chunks1[i1_start + k_s1]
                weight_multiplier = 0
                if type1 == 'korean': weight_multiplier = 0.6 
                elif type1 == 'alnum': weight_multiplier = 0.3
                else: weight_multiplier = 0.1
                part_score = 0
                current_char_length = len(val1)
                total_weighted_score += (part_score * weight_multiplier * current_char_length)
                total_effective_weight += (weight_multiplier * current_char_length)
    if total_effective_weight == 0:
        return 0
    final_score = total_weighted_score / total_effective_weight
    return math.trunc(max(0, min(100, final_score)))

# --- 메인 함수: 유사도 검색 및 최고점 선택 ---
def find_best_match(query_string: str, candidates: list):
    """
    주어진 쿼리 문자열에 대해 후보 리스트에서 가장 유사한 항목을 찾습니다.
    SequenceMatcher 기반 유사도와 TF-IDF 코사인 유사도를 결합하여 사용합니다.

    Args:
        query_string (str): 검색할 쿼리 문자열 (예: OCR로 읽은 약품명).
        candidates (list): {'code': 'DRG001', 'name': '타이레놀500mg'} 형태의 약품명 후보 리스트.

    Returns:
        dict: 가장 높은 점수를 가진 후보 딕셔너리. 점수가 0이면 빈 딕셔너리 반환.
              {'code': '...', 'name': '...', 'combined_score': float, 'lev_score': int, 'cosine_score': float}
    """
    if not candidates:
        return {}

    # 1. 쿼리 문자열 전처리 및 벡터화
    query_string_processed = query_string.lower().strip()
    query_vector = get_tfidf_vector(query_string_processed)

    # 2. 모든 후보의 'name' 필드 추출 및 벡터화
    candidate_names_for_vectorization = [c['name'].lower().strip() for c in candidates]
    
    # 후보군 전체를 한 번에 벡터화 (get_tfidf_vector는 단일 문자열을 받으므로, 이 부분은 직접 Vectorizer를 사용)
    # _global_tfidf_vectorizer_for_cosine이 이미 initialize_tfidf_vectorizer_for_cosine에서 설정되어 있어야 함.
    if _global_tfidf_vectorizer_for_cosine is None:
        print("경고: TF-IDF Vectorizer가 초기화되지 않았습니다. 후보 벡터화를 건너_.")
        return {} # Vectorizer 없으면 유사도 계산 불가

    candidate_vectors_matrix = _global_tfidf_vectorizer_for_cosine.transform(
        candidate_names_for_vectorization
    )

    # 3. TF-IDF 기반 코사인 유사도 일괄 계산 (0.0 ~ 1.0)
    cosine_scores_raw = get_cosine_similarities(query_vector, candidate_vectors_matrix)
    
    # 점수를 0-100 스케일로 변환
    cosine_scores = cosine_scores_raw * 100

    best_match = {}
    highest_combined_score = -1

    for i, candidate in enumerate(candidates):
        # 4. SequenceMatcher 기반 유사도 계산 (0 ~ 100)
        # 이 부분은 각 후보에 대해 루프를 돌면서 개별적으로 계산해야 합니다.
        lev_score = korean_word_matching_ratio(query_string_processed, candidate['name'])

        # 5. 코사인 유사도 점수 가져오기
        current_cosine_score = cosine_scores[i] if i < len(cosine_scores) else 0.0

        # 6. 두 점수에 가중치 적용 및 합산
        # 각 0.5 가중치
        combined_score = (lev_score * 0.5) + (current_cosine_score * 0.5)

        # 현재까지의 최고 점수와 비교
        if combined_score > highest_combined_score:
            highest_combined_score = combined_score
            best_match = {
                'code': candidate['code'],
                'name': candidate['name'],
                'combined_score': highest_combined_score,
                'lev_score': lev_score,
                'cosine_score': current_cosine_score
            }
    
    # 최고 점수가 0이거나 초기 -1인 경우 (매칭이 없거나 유의미한 점수가 없는 경우)
    if highest_combined_score <= 0:
        return {}

    return best_match


# --- 메인 실행 블록 ---
if __name__ == "__main__":
    # 1. DB에서 약품명 데이터 가져오기 (skelecton 모듈 사용)
    print("Fetching drug data from DB...")
    current_db_drug_data = [
            {'code': 'DRG001', 'name': '타이레놀500mg'},
            {'code': 'DRG002', 'name': '유스메출피알서방정 20미리그램'},
            {'code': 'DRG003', 'name': '에페른정50mg'},
            {'code': 'DRG004', 'name': '이페른정50mg'},
            {'code': 'DRG005', 'name': '동화약품'},
            {'code': 'DRG006', 'name': '동화약봉'},
            {'code': 'DRG007', 'name': '사과'},
            {'code': 'DRG008', 'name': '세파클러250mg캡슐'},
            {'code': 'DRG009', 'name': '에스오메프라졸위장약캡슐40밀리그람'}
        ]

    # 2. TF-IDF Vectorizer 초기화 (캐시 사용 또는 새로 학습)
    # 코퍼스는 모든 약품명 리스트입니다.
    corpus_for_tfidf = [item['name'].lower().strip() for item in current_db_drug_data]
    
    # 캐시 파일명을 명시적으로 지정하여 initialize_tfidf_vectorizer_for_cosine 호출
    # 예를 들어, 'drug_name_tfidf_vectorizer.pkl'이라는 이름으로 저장
    initialize_tfidf_vectorizer_for_cosine(corpus_for_tfidf, cache_filename='drug_name_tfidf_vectorizer.pkl')

    # 3. 유사도 검색 테스트
    test_queries = [
        "유스메출피알서방객출20m미에스오폐프라출마리", # 오타가 많음
        "에페른정50mg",
        "이페른정50mg",
        "타이레놀",
        "동화약봉",
        "애플", # 일치하는 것이 없는 경우
        "세파클러캡슐"
    ]

    for query in test_queries:
        print(f"\n--- Query: '{query}' ---")
        best_match_result = find_best_match(query, current_db_drug_data)
        
        if best_match_result:
            print(f"Best Match Found:")
            print(f"  Code: {best_match_result['code']}")
            print(f"  Name: {best_match_result['name']}")
            print(f"  Combined Score: {best_match_result['combined_score']:.2f}")
            print(f"  Levenshtein Score: {best_match_result['lev_score']:.0f}")
            print(f"  Cosine Score (TF-IDF): {best_match_result['cosine_score']:.0f}")
        else:
            print(f"No significant match found for '{query}'.")