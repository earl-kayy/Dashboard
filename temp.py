import pandas as pd

data = {
    'category': [
        'KlecSpeech', 'KconfSpeech', 'KsponSpeech', 'CommandSpeech', 'FreeConvSpeech/normal',
        'KforeignSpeech',
        'SpeakerSpeech', 'MultiSpeakerSynthesis', 'KconvSpeech',
        'CarConvCommand',
        'WelfareCallCenter', 'NumPatternSpeech', 'KresSpeech', 'KtelSpeech',
        'LiterarySpeech', 'LowQualityTelephone',
        'DialectSpeech', 'KoreanEnglishChinese',
        'NoisySpeech', 'ForeignerSpeech',
        'ChildSpeech', 'KoreanEnglishHybrid', 'TelehealthSpeech',
        'VCTK', 'common-voice-en', 'LibriSpeech', 'KaggleMediSpeech',
        'GigaSpeech', 'peoples_speech', 'NSC', 'NSC_additional',
        'Tedlium', 'Voxpopuli'
    ],
    'explanation': [
        '한국어 강의 음성', '회의 음성', '한국어 음성', '명령어 음성', '자유대화 음성', 
        '한국어 외래어 발화',
        '화자 인식용 음성 데이터', '다화자 음성합성 데이터', '한국인 대화음성',
        '차량 내 대화 및 명령어',
        '복지 분야 콜센터 상담데이터', '숫자가 포함된 패턴 발화 데이터', '고객 응대 음성', '상담 음성',
        '문학작품 낭송.낭독 음성 데이터', '저음질 전화망 음성인식 데이터',
        '한국어 방언 발화', '한-영 및 한-중 음성발화 데이터',
        '소음 환경 음성인식 데이터', '외국인 한국어 발화 음성 데이터',
        '한국어 아동 음성 데이터', '한영 혼합 인식 데이터', '비대면 진료를 위한 의료진 및 환자',
        '다양한 영어 억양의 화자 음성 데이터', '다화자 다문장 낭독 음성 데이터', '오디오북 발췌 음성 데이터',
        '의료 환경 수집 음성 데이터', '영어 음성 대규모 데이터셋', '다양한 화자/상황 수집된 음성 데이터', 
        '영어 뉴스 방송', '영어 뉴스 방송', 'TED 강연 오디오', '유럽 의회 회의록'
    ]
}

df = pd.DataFrame(data)

df.to_csv('./data/cat_explanation.csv', index = False)