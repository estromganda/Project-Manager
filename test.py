def sayHello(who="world"):
    print(f"Hello {who}!")


def fct(a: int):
    print("Fct1", type(a))


def fct(b: str):
    print("Fct 2", type(b))


fct(9)
