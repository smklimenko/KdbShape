import unittest


class A:
    f = 0

    def __init__(self, v) -> None:
        self.f = v

    def tostr(self):
        return str(self.f)


class Test2(unittest.TestCase):
    def test_styleTest(self):
        a = [A(10), A(20), A(30)]

        all = ["MILK", "BREAD", "EGGS"]
        print(list(map(lambda x: x.lower(), all)))



        print()

        # print(a)


if __name__ == '__main__':
    unittest.main()
