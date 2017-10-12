## Wolframbeta ##
---
## 모듈 설명 ##
* nonterminal.py
    - Expr(tail), Term(tail), Factor(tail), Func(Params) 클래스 정의
* config.py
    - 빌트인 함수, 상수(e, pi) 등 정의
* utils.py
    - 일반 함수(디버그, 에러 발생 등) 정의
* tokenizer.py
    - token manager 클래스 정의
* similar_term.py
    - 동류항, 단일항 클래스 정의

### 구현된 기능 ###
- 실수의 사칙연산
    두 실수의 사칙연산
    괄호를 포함한 여러 실수의 사칙연산
    괄호, 곱셈, 덧셈을 포함한 여러 실수의 연산자 우선순위를 따르는 사칙연산
- 실수의 거듭제곱
    거듭제곱의 우선순위는 괄호 > 거듭제곱 > 곱셈, 나눗셈
- 연산 트리 생성
- pi, e 등의 수학 상수 지원(부동소수점 실수 근사값)
- 동류항 연산을 위한 자료구조 구성
        - 동류항 자료구조 - SimilarTermsDict
        - 항 자료구조 - TermDict
- 다항식의 덧셈, 곱셈, 뺄셈
- 초등함수 (대수함수, 삼각함수, 지수함수, 로그함수)
- 합성함수

# TODO #
### 값 ###
- 지수함수

### 다항식의 계산 ###
- 다항식의 나눗셈
- 다항식의 거듭제곱


### 그 외 ###

- 정수값 출력할 때 소수점 이하 제거
- 편리한 예외처리 루틴

- 일반함수의 토큰화
- 일변수 함수의 미분
- 다변수 함수의 편미분
- 함수 정의
- 함수값의 계산
- 다변수 함수의 정의
- 미분가능성 판단

- GUI 인터페이스
- 함수 출력, 함수 그래프 출력

## 요구사항(참조) ## 
    ## 필수 구현 요소 ##
    1. 수학 함수 라이브러리
    - 값
        - 부동소수점 실수형 표현 범위 이내
        - π,e 등 주요 수학상수 지원 (부동소수점 실수형 근사값)
    -일변수 함수의 정의
        - 초등함수(대수함수, 삼각함수, 지수함수, 로그함수) 구현
        - 합성함수 구현
        - 함수 정의 문자열 표기(notation) 생성
        - 함수 정의 문자열 표기 정규화(canonicalization)
        - 함수값 계산 (정의역과 공역은 부동소수점 실수형 표현 범위 이내로 근사)
    - 일변수 함수의 미분
        - 도함수를 함수로 반환
    - 다변수 함수의 정의
        - 최소 2개 이상의 변수 지원
    - 다변수 함수의 편미분
        - 1개 변수로 미분한 편도함수를 함수로 반환
    - 미분가능성
        - 특정 점의 불연속점, 미분불가능점 여부 판단
    - 수식 구문 분석(parse)
        - 함수 정의 문자열 표기(notation) 해석하여 함수 생성
    2. 사용자 인터페이스
    - GUI 제공 (플랫폼 무관)
    - 함수 출력
        - 일변수 함수와 그 미분한 도함수의 정의 문자열 표기 출력
        - 다변수 함수와 각 변수로 편미분한 편도함수들의 정의 문자열 표기 출력
    - 그래프 플롯
        - 지정한 정의역에서 일변수 함수와 그 도함수를 2차원 그래프에 표시
     
    ## 추가 구현 요소 ##
    1. 수학 함수 라이브러리
    - 다변수 함수의 벡터 미분
        - 각 변수로 편미분한 편도함수들의 벡터인 기울기(gradient)를 반환
        - 지정한 벡터로 미분한 방향도함수를 반환
    - 미분가능성
        - 정의역에서 연속성, 미분가능성 판단
    - 복잡한 함수의 정의
        - 특수함수 구현
        - 급수(∑) 구현
    - 함수의 적분
        - 1개 변수로 적분하여 함수로 반환
        - 지정한 변수 범위에서 정적분 계산
    2. 사용자 인터페이스
    - 함수 입력
        - 함수 정의 문자열 표기 입력
    - 함수 출력
        - 함수 정의 수식 표기 출력
        - 벡터의 정의 문자열 표기 출력
    - 그래프 플롯
        - 지정한 정의역에서 변수가 2개인 다변수 함수와 각 변수로 편미분한 편도함수들의 벡터인 기울기를 3차원 그래프에 표시
        - 지정한 정의역에서 변수가 2개인 다변수 함수와 지정한 벡터로 미분한 방향도함수를 3차원 그래프에 표시
        