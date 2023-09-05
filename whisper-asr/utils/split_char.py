#!/usr/bin/env python3
# 입력된 텍스트 파일을 char 단위로 나누어 공백으로 분리하여 출력한다.
# 영어, 한글 등 모든 글자를 char 단위로 분리한다.
#
# Usage: split_char.py in.txt > out.txt
 
# 입력 텍스트 파일의 첫번째 컬럼은 분리하지 않는 경우 (예, kaldi uttid)
# 아래 if 문의 False를 True로 수정한다.
#
# 주의사항:
# UnicodeDecodeError 오류가 나는 경우는 실행하는 shell 환경의 locale과
# 입력텍스트의 encoding이 일치하지 않는 경우이다.  예를 들어 입력 파일이
# euckr로 인코딩 되어있다면 shell의 환경변수도 ko_KR.euckr 로
# 설정되어있어야한다.

import sys

header_col = True
if sys.argv[1] == "-H":
    header_col = False
    del sys.argv[1]

for line in open(sys.argv[1]):
    words = line.split()
    # set as True to not to split the first column
    if header_col:
        print(words[0], end=" ")
        words = words[1:]
    print(' '.join(list(''.join(words))))
