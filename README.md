## Wolframbeta ##
---
## 모듈 설명 ##
* nonterminals.py
    - Expr(tail), Term(tail), Factor(tail), Func(Params) 클래스 정의
* config.py
    - 빌트인 함수, 상수(e, pi) 등 정의
* utils.py
    - 일반 함수(디버그, 에러 발생 등) 정의
* tokenizer.py
    - token manager 클래스 정의
* terminals.py
    - 동류항, 단일항 클래스 정의
* webapp.py
    - 웹브라우저 기반 GUI
    - Dependency : bokeh
    - 실행 방법 : bokeh serve webapp.py --port 8000 
    
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
    - 동류항 자료구조 :: ExprDict
    - 항 자료구조 :: TermDict
    - 지수함수의 밑 상수 :: ConstDict(TermDict)
        - TermDict 구현 시 해시 함수에서 항의 계수를 고려하지 않도록 의도적으로 설계함.
        - 그 결과 상수 밑을 갖는 지수 함수의 경우, 서로 다른 상수를 밑으로 할 때 같은 해시값이 나오는 경우 발생
        - 상수 밑을 갖는 지수함수의 경우에만 특별히 해시함수를 따로 쓰기 위해 사용함. 
            
- 다항식의 사칙연산, 실수 거듭제곱
- 변수값의 대입
- 초등함수 (대수함수, 삼각함수, 지수함수, 로그함수)
- 합성함수

- 미분
    - 다변수 다항식의 편미분
    
# 구현중인 기능 #
- 변수값의 Assignment
- GUI 인터페이스
- 함수, 함수 그래프 출력

# TODO #

### 다항식의 계산 ###

- 삼각함수의 미분
- 지수함수의 미분
- 미분가능성 판단

### 어려웠던 점 ###

- 동류항 정리
    - x^2, pow(x, 2)는 같은 의미인데, L1 parsing에서는 서로 다른 루틴을 타게 된다.
    - 전자는 <variable><factor_tail>, 후자는 <func><params>
    - 동류항 정리를 할 때 x^2와 pow(x, 2)를 동일하게 취급해야 한다.
    - pow(x, 2)를 먼저 정리해서 x^2로 취급해서 연산할것인지, x^2를 pow로 취급해서 연산할 것인지 결정 필요
        - Func 객체로 취급할 때(pow 함수로 취급)의 이점 : params를 별도로 관리하므로 값의 계산에 유리함
        - 단점 : 함수 출력이나 Key를 관리할 때에 pow의 경우에만 ^ 기호로 분리하여 우아하지 않은 코드를 만들어야 함.
        - 단점2 : x^2까지 parsing한 다음 pow로 변환하는 과정에서 다시 parsing이 일어나므로 LL1 Parsing이 아닌 코드가 된다. (이게 제일 중요)
    - 결국 별도로 pow, ^ operator 를 연산해서 동류항 딕셔너리로 보내는 과정이 필요하다.
    
- 분수함수의 존재
    - 최초 구현 당시 분수함수를 염두에 두지 않고 다항식만을 염두에 두고 클래스를 디자인한 문제
        - 기존에는 동류항 dictionary의 key를 str로만, value를 정수로만 사용
        - Log 함수 등의 미분을 구현하기 위해서는 분수함수 및 지수함수의 구현이 필수적임.
        - 고민 끝에 식, 항 클래스를 처음부터 다시 디자인함.
        - 새 클래스는 동류항의 밑, 지수 모두에 여러 가지 객체가 들어갈 수 있도록 key를 디자인함
     
        
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
        