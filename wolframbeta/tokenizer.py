class TokenManager:
    def __init__(self, str_expression):
        self.str_expression = str_expression
        self.__tokens__ = self.tokenize(self.str_expression)

    def tokenize(self, str_expression):
        """
        str_expression : 괄호, 연산자, 숫자 등을 포함한 입력 식
        return : 숫자, 연산자가 분리된 리스트 (infix)
        """
        NUMBERS = "0123456789."
        tokens = []
        number_buff = ""
        str_expression = str_expression.replace(" ", "")

        for i, ch in enumerate(str_expression):
            if ch not in NUMBERS:
                if number_buff != "" :
                    tokens.append(float(number_buff))
                    number_buff = ""
                tokens.append(ch)
            else:
                number_buff += ch

        if number_buff != "":
            tokens.append(float(number_buff))
            number_buff = ""
        return tokens

    def get_next_token(self):
        ret = self.__tokens__[0]
        self.__tokens__ = self.__tokens__[1:]
        return ret

    def show_next_token(self):
        return self.__tokens__[0]

    def has_next_token(self):
        if len(self.__tokens__) > 0:
            return True
        else:
            return False
