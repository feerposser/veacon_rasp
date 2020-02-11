

class Testou:

    loco = "loooco"

    def __init__(self, a):
        if a == "a":
            self.a = self.print_a
            self.b = "bbbb"

    def print_a(self, nome):
        return "aaaaaaaaaaaaaaaaaaa " + nome


t = Testou('a')
print(t.a("fernando"))
print(t.__dict__)

for j in t.__dict__:
    print(type(t.__dict__[j]))

print(Testou.__dict__)
