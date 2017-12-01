## Wolframbeta ##
---
## 모듈 설명 ##
##### wolframbeta #####
* nonterminals.py
    - Expr(tail), Term(tail), Factor(tail), Func(Params) 클래스 정의
* config.py
    - 빌트인 함수, 상수(e, pi) 등 정의
* utils.py
    - 일반 함수(디버그, 에러 발생 등) 정의
* tokenizer.py
    - token manager 클래스 정의
* terminals.py
    - 동류항, 단일항, 함수, 밑상수항 클래스 정의
    
##### wolframui #####
* assign.py
    - ui에서 쓰는 assignment 파싱 관련 함수
* uiconfig.py
    - ui에서 쓰는 configs
    
##### 실행 파일 #####
* web_wolframbeta.py
    - 웹브라우저 기반 GUI
    - Dependency : bokeh
    - 실행 방법 : bokeh serve web_wolframbeta.py --port 8000 
    - 확인 : http://localhost:8000/web_wolframbeta
    
## 구현된 기능 ##
- 연산 트리 파싱 및 생성
- 실수의 사칙연산
    - 두 실수의 사칙연산
    - 괄호를 포함한 여러 실수의 사칙연산
    - 괄호, 곱셈, 덧셈을 포함한 여러 실수의 연산자 우선순위를 따르는 사칙연산
- 실수의 거듭제곱
    - 거듭제곱의 우선순위는 괄호 > 거듭제곱 > 곱셈, 나눗셈
- pi, e 등의 수학 상수 지원(부동소수점 실수 근사값)
- 동류항 연산을 위한 자료구조 구성
                
- 다항식의 사칙연산, 실수 거듭제곱

- 미분
    
- GUI 인터페이스
- 함수, 함수 그래프 출력
- 변수값의 Assignment
- 정의역, 치역 range 설정
