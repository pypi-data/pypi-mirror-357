# korean_text_matcher_package/korean_text_matcher/similarity_matcher.py

import re
from difflib import SequenceMatcher
import math

def korean_word_matching_ratio(s1, s2):
    """
    두 문자열의 부분 유사도를 계산합니다. 한글은 초성, 중성, 종성으로 분리하여 비교하며,
    첫 번째 유의미한 글자의 일치 여부에 따라 가중치를 적용합니다.

    Args:
        s1 (str): 첫 번째 입력 문자열.
        s2 (str): 두 번째 입력 문자열.

    Returns:
        int: 0에서 100 사이의 유사도 점수.
    """

    # --- 내부 헬퍼 함수 정의 시작 ---
    CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅝ', 'ㅙ', 'ㅞ', 'ㅛ', 'ㅜ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
    JONGSUNG_LIST = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

    def _decompose_korean_char(char):
        if not ('가' <= char <= '힣'):
            return char

        char_code = ord(char) - ord('가')

        if not (0 <= char_code < 11172):
            return char

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

    def _get_first_meaningful_char(s):
        for char in s:
            if '가' <= char <= '힣' or 'a' <= char <= 'z' or 'A' <= char <= 'Z' or '0' <= char <= '9':
                return char
        return None
    # --- 내부 헬퍼 함수 정의 끝 ---

    s1_lower = str(s1).lower() if s1 is not None else ""
    s2_lower = str(s2).lower() if s2 is not None else ""

    s1_processed = _decompose_korean_string(s1_lower)
    s2_processed = _decompose_korean_string(s2_lower)

    if not s1_processed or not s2_processed:
        return 0

    if len(s1_processed) <= len(s2_processed):
        shorter = s1_processed
        longer = s2_processed
    else:
        shorter = s2_processed
        longer = s1_processed

    m = SequenceMatcher(None, shorter, longer)
    blocks = m.get_matching_blocks()

    scores = []
    for block in blocks:
        long_start = block[1] - block[0]
        if long_start < 0:
            long_start = 0
        long_end = long_start + len(shorter)
        long_substr = longer[long_start:long_end]

        m2 = SequenceMatcher(None, shorter, long_substr)
        r = m2.ratio()
        scores.append(r)

    if not scores:
        base_score = 0
    else:
        base_score = 100 * max(scores)

    weight_adjustment = 0
    first_char_s1 = _get_first_meaningful_char(s1_lower)
    first_char_s2 = _get_first_meaningful_char(s2_lower)

    if first_char_s1 is not None and first_char_s2 is not None:
        if first_char_s1 == first_char_s2:
            weight_adjustment = 5
        else:
            weight_adjustment = -5

    weighted_score = base_score + weight_adjustment
    final_score = max(0, min(100, weighted_score))

    return math.trunc(final_score)