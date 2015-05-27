def myAssertDictEqual(a, b):
    dictAInB(a, b)
    dictAInB(b, a)

def dictAInB(a, b):
    for akey, avalue in a.items():
        if avalue != b[akey]:
            raise Exception("%s[%s] != [%s]" % (akey, avalue, b.get(akey)))
