## Wolframbeta ##
---
### 구현된 기능 ###
- 사칙연산
    두 실수의 사칙연산
    괄호를 포함한 여러 실수의 사칙연산
    괄호, 곱셈, 덧셈을 포함한 여러 실수의 연산자 우선순위를 따르는 사칙연산
- 거듭제곱
    거듭제곱의 우선순위는 괄호 > 거듭제곱 > 곱셈, 나눗셈
- 연산 트리 생성
- 일반함수의 토큰화
- pi, e 등의 수학 상수 지원(부동소수점 실수 근사값)
- 초등함수 (대수함수, 삼각함수, 지수함수, 로그함수)
- 합성함수

# TODO #

## 다항식의 계산 ##

- 다항식의 덧셈, 뺄셈
- 다항식의 곱셈, 나눗셈
- 다항식의 거듭제곱

- 내부 연산의 객체화 : x^(2*x^3+1) + x^(2*x^3+1)을 계산할 수 있을 것인지?
    - 2*x^3+1 == 2*x^3+1 ? 같은 비교 연산도 가능해야함
    - expr 객체의 비교는 어떻게 구현?, term의 비교는?
    - 일단 가장 간단한 factor의 비교부터 생각해보자.
        - factor := (something)(^<factor>) 의 꼴이다.
        - 최대한 계산한 다음 something, factor가 각각 같으면 같은 factor
        - 근데 그 최대한 계산 이라는건 어떻게 정의하지?
        - 일단 factor의 연산(multiply)부터 정의해보자
            - factor 의 something 부분은 5가지로 나눠지고, 곱셈 나눗셈 해서 총 50가지 연산으로 나뉜다.
            - 일단 기본적인게 number * number, number / number 이게 베이스가 되고
            - number * variable, number / variable, variable * number, variable / number
            - number * function, number / function, function * number, function / number
            - 일단 이 위의 것들이 기본이 되어야 할 듯.
            - ( expr ) * number, ( expr ) / number 정도는 구현할 수 있을 것 같은데 문제는
            - ( expr ) * ( expr ), ( expr ) / ( expr ) 이 되면 골치가 아픔. due 까지 구현할 수 있을지도 미지수.
        
## 그 외 ## 

- 일변수 함수의 미분
- 다변수 함수의 편미분
- 함수 정의
- 함수값의 계산
- 다변수 함수의 정의
- 다변수 함수의 편미분
- 미분가능성 판단

- GUI 인터페이스
- 함수 출력, 함수 그래프 출력