import re


BASE_CODE, CHOSEONG, JUNGSEONG = 0xAC00, 19, 21
JONGSEONG_COUNT = 28

INITIAL_LIST = [
    'ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'
]
MEDIAL_LIST = [
    'ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ'
]
FINAL_LIST = [
    '', 'ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'
]

INITIAL_INDEX = {ch: idx for idx, ch in enumerate(INITIAL_LIST)}
MEDIAL_INDEX = {ch: idx for idx, ch in enumerate(MEDIAL_LIST)}
FINAL_INDEX = {ch: idx for idx, ch in enumerate(FINAL_LIST) if ch}

INITIAL_SET = set(INITIAL_LIST)
MEDIAL_SET = set(MEDIAL_LIST)
FINAL_SET = set([ch for ch in FINAL_LIST if ch])

# 쌍자음 분해 사전 (받침용, 초성용도 일부 포함)
HEAVY_TO_SIMPLE = {
    'ㄳ': ['ㄱ', 'ㅅ'],
    'ㄵ': ['ㄴ', 'ㅈ'],
    'ㄶ': ['ㄴ', 'ㅎ'],
    'ㄺ': ['ㄹ', 'ㄱ'],
    'ㄻ': ['ㄹ', 'ㅁ'],
    'ㄼ': ['ㄹ', 'ㅂ'],
    'ㄽ': ['ㄹ', 'ㅅ'],
    'ㄾ': ['ㄹ', 'ㅌ'],
    'ㄿ': ['ㄹ', 'ㅍ'],
    'ㅀ': ['ㄹ', 'ㅎ'],
    'ㅄ': ['ㅂ', 'ㅅ'],
    'ㄲ': ['ㄱ', 'ㄱ'],
    'ㄸ': ['ㄷ', 'ㄷ'],
    'ㅃ': ['ㅂ', 'ㅂ'],
    'ㅆ': ['ㅅ', 'ㅅ'],
    'ㅉ': ['ㅈ', 'ㅈ'],
}

# 역분해용 사전
SIMPLE_TO_HEAVY = {tuple(v): k for k, v in HEAVY_TO_SIMPLE.items()}

def split(text: str) -> str:
    """기본 분리 함수 - 완성형 한글을 자모로 분리"""
    result = []
    for ch in text:
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            syllable_index = code - BASE_CODE
            initial_idx = syllable_index // (JUNGSEONG * JONGSEONG_COUNT)
            medial_idx = (syllable_index % (JUNGSEONG * JONGSEONG_COUNT)) // JONGSEONG_COUNT
            final_idx = syllable_index % JONGSEONG_COUNT

            result.append(INITIAL_LIST[initial_idx])
            result.append(MEDIAL_LIST[medial_idx])
            if final_idx != 0:
                result.append(FINAL_LIST[final_idx])
        else:
            result.append(ch)
    return ''.join(result)

def add(jamo_str: str) -> str:
    """기본 합치기 함수 - 자모를 완성형 한글로 합침"""
    result = []
    i = 0
    length = len(jamo_str)
    while i < length:
        ch = jamo_str[i]
        if ch in INITIAL_SET and i + 1 < length and jamo_str[i+1] in MEDIAL_SET:
            initial = ch
            medial = jamo_str[i+1]
            initial_idx = INITIAL_INDEX.get(initial)
            medial_idx = MEDIAL_INDEX.get(medial)
            final_char = ''
            final_idx = 0
            if i + 2 < length:
                nxt = jamo_str[i+2]
                if nxt in FINAL_SET:
                    if not (nxt in INITIAL_SET and i + 3 < length and jamo_str[i+3] in MEDIAL_SET):
                        final_char = nxt
                        final_idx = FINAL_INDEX.get(final_char, 0)
                        i += 1
            syllable_code = BASE_CODE + (initial_idx * JUNGSEONG + medial_idx) * JONGSEONG_COUNT + final_idx
            result.append(chr(syllable_code))
            i += 2
        else:
            result.append(ch)
            i += 1
    return ''.join(result)

def heavy_split(text: str) -> str:
    """쌍자음을 분해해서 완성형 한글 -> 자모 분해 + 쌍자음 분리"""
    basic = split(text)
    result = []
    for ch in basic:
        if ch in HEAVY_TO_SIMPLE:
            result.extend(HEAVY_TO_SIMPLE[ch])
        else:
            result.append(ch)
    return ''.join(result)

def heavy_add(jamo_str: str) -> str:
    """쌍자음을 합쳐서 자모 + 쌍자음 -> 완성형 한글 합치기"""
    i = 0
    result_jamo = []
    length = len(jamo_str)

    while i < length:
        # 쌍자음 합치기 시도 (2글자)
        if i + 1 < length:
            pair = (jamo_str[i], jamo_str[i+1])
            if pair in SIMPLE_TO_HEAVY:
                result_jamo.append(SIMPLE_TO_HEAVY[pair])
                i += 2
                continue
        # 아니면 그냥 추가
        result_jamo.append(jamo_str[i])
        i += 1

    return add(''.join(result_jamo))

def getChoseong(text: str) -> str:
    """문자열의 한글 글자마다 초성만 추출해서 반환"""
    result = []
    for ch in text:
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            syllable_index = code - BASE_CODE
            initial_idx = syllable_index // (JUNGSEONG * JONGSEONG_COUNT)
            result.append(INITIAL_LIST[initial_idx])
        else:
            # 한글 아닌 글자는 그대로 추가하거나 건너뛸 수도 있음 (여기서는 그대로 둠)
            result.append(ch)
    return ''.join(result)

def josa(word: str, josa_pair: str) -> str:
    """
    word: 조사 붙일 단어 (한글 완성형)
    josa_pair: '을/를', '이/가', '은/는', '과/와', '와/과', '로/으로', '으로/로' 등 '/'로 구분된 조사 쌍.
    
    예:
      josa('사과', '을/를') -> '사과를'
      josa('바나나', '이/가') -> '바나나가'
      josa('사과', '와/과') -> '사과와'
      josa('사과', '과/와') -> '사과와'  (역순 입력도 동작)
      josa('길', '로/으로') -> '길로'
      josa('길', '으로/로') -> '길로'
    """
    if not word:
        return ''
    
    # 마지막 글자 받침 여부 판단
    last_char = word[-1]
    code = ord(last_char)
    if not (0xAC00 <= code <= 0xD7A3):
        has_batchim = False
        jong_idx = 0
    else:
        syllable_index = code - BASE_CODE
        jong_idx = syllable_index % JONGSEONG_COUNT
        has_batchim = jong_idx != 0
    
    # 조사 쌍 파싱
    parts = josa_pair.split('/')
    if len(parts) != 2:
        # 형식이 이상할 경우, 단순히 word 반환
        return word
    
    first, second = parts[0].strip(), parts[1].strip()
    
    # 대표적인 조사 쌍들의 집합 정의 (역순 입력도 허용)
    pair_set = {first, second}
    # key: 집합, value: ('batchim_form', 'no_batchim_form')
    known = {
        frozenset({'을','를'}): ('을','를'),
        frozenset({'이','가'}): ('이','가'),
        frozenset({'은','는'}): ('은','는'),
        frozenset({'와','과'}): ('과','와'),
        frozenset({'로','으로'}): ('으로','로'),  # batchim_form:'으로', no_batchim_form:'로'; 다만 최종 선택은 아래에서 추가 논리로 처리
    }
    
    batchim_form = None
    no_batchim_form = None
    key = frozenset(pair_set)
    if key in known:
        # 입력 순서에 상관없이 올바른 배침/무배침 형태 찾기
        std_batchim, std_no = known[key]
        # parts 중 어느 것이 배침/무배침 양식인지 결정
        if first == std_batchim and second == std_no:
            batchim_form, no_batchim_form = first, second
        elif first == std_no and second == std_batchim:
            batchim_form, no_batchim_form = second, first
        else:
            # 두 조사 중 문자열 비교로 정확히 일치하지 않으면, 그래도 기본 지정
            batchim_form, no_batchim_form = std_batchim, std_no
    else:
        # 알 수 없는 쌍: 기본적으로 '을/를' 스타일(첫째=batchim, 둘째=no-batchim)로 간주
        batchim_form, no_batchim_form = first, second
    
    # '로/으로' 계열의 특수 처리:
    # 배침이 있더라도 종성이 'ㄹ'인 경우에는 '로'를 쓰고, 그 외 배침이 있으면 '으로', 배침 없으면 '로'
    # 여기서는 batchim_form/no_batchim_form이 ('으로','로') 형태로 설정되어 있음.
    # 따라서 has_batchim일 때도, jong_idx에 따라 '로' 선택이 필요하면 override.
    if {batchim_form, no_batchim_form} == {'로','으로'}:
        # 실제 선택
        if not has_batchim:
            chosen = no_batchim_form  # '로'
        else:
            # 종성이 'ㄹ'인지 확인
            last_jong = FINAL_LIST[jong_idx] if jong_idx != 0 else ''
            if last_jong == 'ㄹ':
                chosen = no_batchim_form  # '로'
            else:
                chosen = batchim_form  # '으로'
        return word + chosen
    
    # 일반 조사: 배침이 있으면 batchim_form, 없으면 no_batchim_form
    chosen = batchim_form if has_batchim else no_batchim_form
    return word + chosen


import re

def compjosa(text: str) -> str:
    """
    문자열 내에서 한글 단어 뒤의 조사 패턴 “을(를)”, “를(을)”, “이/가”, “가/이” 등
    또는 “사과이/가” 같은 “X/Y” 형식을 찾아, 알맞은 조사를 선택해 치환합니다.
    
    예:
      compjosa("사과을(를) 먹었는데 포켓몬이/가 왔다!")
      -> "사과를 먹었는데 포켓몬이 왔다!"
    """
    # 미리 정의한 조사 쌍 목록
    josa_pairs = [
        ('을','를'),
        ('이','가'),
        ('은','는'),
        ('와','과'),
        ('로','으로'),
    ]

    result = text
    for a, b in josa_pairs:
        # 1) 괄호 패턴: “단어” + a(b) 또는 b(a)
        #    예: "사과을(를)", "사과를(을)"
        #    정규식: (?P<word>[가-힣]+)a\(b\)
        pat1 = re.compile(rf'(?P<word>[가-힣]+){re.escape(a)}\({re.escape(b)}\)')
        result = pat1.sub(lambda m: josa(m.group('word'), f"{a}/{b}"), result)
        pat1_rev = re.compile(rf'(?P<word>[가-힣]+){re.escape(b)}\({re.escape(a)}\)')
        result = pat1_rev.sub(lambda m: josa(m.group('word'), f"{b}/{a}"), result)

        # 2) 슬래시 패턴: “단어” + a/b 또는 b/a
        #    예: "포켓몬이/가", "바나나가/이"
        pat2 = re.compile(rf'(?P<word>[가-힣]+){re.escape(a)}/{re.escape(b)}')
        result = pat2.sub(lambda m: josa(m.group('word'), f"{a}/{b}"), result)
        pat2_rev = re.compile(rf'(?P<word>[가-힣]+){re.escape(b)}/{re.escape(a)}')
        result = pat2_rev.sub(lambda m: josa(m.group('word'), f"{b}/{a}"), result)

    return result

def toCompat(text: str) -> str:
    """완성형 한글을 조합형(초성, 중성, 종성 유니코드 조합 문자)으로 변환"""
    result = []
    for ch in text:
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            syllable_index = code - BASE_CODE
            initial_idx = syllable_index // (JUNGSEONG * JONGSEONG_COUNT)
            medial_idx = (syllable_index % (JUNGSEONG * JONGSEONG_COUNT)) // JONGSEONG_COUNT
            final_idx = syllable_index % JONGSEONG_COUNT

            # 유니코드 조합형 초성, 중성, 종성
            choseong = chr(0x1100 + initial_idx)
            jungseong = chr(0x1161 + medial_idx)
            result.append(choseong)
            result.append(jungseong)
            if final_idx != 0:
                jongseong = chr(0x11A7 + final_idx)
                result.append(jongseong)
        else:
            result.append(ch)
    return ''.join(result)

def fromCompat(text: str) -> str:
    """조합형 한글을 완성형으로 변환"""
    result = []
    i = 0
    length = len(text)
    while i < length:
        ch = ord(text[i])
        if 0x1100 <= ch <= 0x1112:  # 초성
            initial_idx = ch - 0x1100
            if i + 1 < length and 0x1161 <= ord(text[i + 1]) <= 0x1175:
                medial_idx = ord(text[i + 1]) - 0x1161
                final_idx = 0
                if i + 2 < length and 0x11A8 <= ord(text[i + 2]) <= 0x11C2:
                    final_idx = ord(text[i + 2]) - 0x11A7
                    i += 1
                syllable = chr(BASE_CODE + (initial_idx * JUNGSEONG + medial_idx) * JONGSEONG_COUNT + final_idx)
                result.append(syllable)
                i += 2
            else:
                result.append(chr(ch))
                i += 1
        else:
            result.append(chr(ch))
            i += 1
    return ''.join(result)

def native_number(n: int) -> str:
    """숫자 → 순우리말로 변환 (1~99999 정도 권장)"""
    units = ['', '하나', '둘', '셋', '넷', '다섯', '여섯', '일곱', '여덟', '아홉']
    tens = ['', '열', '스물', '서른', '마흔', '쉰', '예순', '일흔', '여든', '아흔']
    hundreds = ['', '백', '이백', '삼백', '사백', '오백', '육백', '칠백', '팔백', '구백']
    thousands = ['', '천', '이천', '삼천', '사천', '오천', '육천', '칠천', '팔천', '구천']
    m = ['', '만', '이만', '삼만', '사만', '오만', '육만', '칠만', '팔만', '구만']

    if n == 0:
        return '영'
    if n < 10:
        return units[n]
    elif n < 100:
        ten, unit = divmod(n, 10)
        return tens[ten] + (units[unit] if unit != 0 else '')
    elif n < 1000:
        hun, rem = divmod(n, 100)
        return hundreds[hun] + (native_number(rem) if rem else '')
    elif n < 10000:
        tho, rem = divmod(n, 1000)
        return thousands[tho] + (native_number(rem) if rem else '')
    elif n < 100000:
        tho, rem = divmod(n, 10000)
        return m[tho] + (native_number(rem) if rem else '')
    else:
        return str(n)  # 너무 큰 수는 숫자로 그대로 반환




def native_day(n: int) -> str:
    """1~31일 사이 날짜를 순우리말로 변환"""
    special_days = {
        1: '하루',
        2: '이틀',
        3: '사흘',
        4: '나흘',
        5: '닷새',
        6: '엿새',
        7: '이레',
        8: '여드레',
        9: '아흐레',
        10: '열흘',
        15: '보름',
        20: '스무날',
        # 21: '세이레',
        30: '그믐',
    }
    if n in special_days:
        return special_days[n]
    else:
        return str(n) + '일'



__all__ = ['split', 'add', 'heavy_split', 'heavy_add', 'getChoseong', 'josa', 'compjosa', 'toCompat', 'fromCompat', 'native_number', 'native_day']
