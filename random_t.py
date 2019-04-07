import random

a = []
for x in range(97, 123):
    a.append(chr(x))

b = []
for x in range(65, 91):
    b.append(chr(x))

c = []
for x in range(48, 58):
    c.append(chr(x))


def letter_number(flag, n):
    ret = []
    if flag:
        #catital & number
        for i in range(n):
            ret.append(random.choice(b+c))
    else:
        #lower & number
        for i in range(n):
            ret.append(random.choice(a+c))

    return ''.join(ret)

if __name__ == '__main__':
    ret = letter_number(True, 80)
    print(ret)
    ret = letter_number(False, 30)
    print(ret)
