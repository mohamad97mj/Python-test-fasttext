class GeneralUtils:

    @staticmethod
    def sort_lis_in_persian(mylist):
        alphabet = "آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهیيى ‌"

        def cmp_to_key(mycmp):
            """Convert a cmp= function into a key= function"""

            class K(object):
                def __init__(self, obj, *args):
                    self.obj = obj

                def __lt__(self, other):
                    return mycmp(self.obj, other.obj) < 0

                def __gt__(self, other):
                    return mycmp(self.obj, other.obj) > 0

                def __eq__(self, other):
                    return mycmp(self.obj, other.obj) == 0

                def __le__(self, other):
                    return mycmp(self.obj, other.obj) <= 0

                def __ge__(self, other):
                    return mycmp(self.obj, other.obj) >= 0

                def __ne__(self, other):
                    return mycmp(self.obj, other.obj) != 0

            return K

        def acmp(a, b):
            la = len(a)
            lb = len(b)
            lm = min(la, lb)
            p = 0
            while p < lm:
                pa = alphabet.index(a[p])
                pb = alphabet.index(b[p])
                if pa > pb:
                    return 1
                if pb > pa:
                    return -1
                p = p + 1

            if la > lb:
                return 1
            if lb > la:
                return -1
            return 0

        return sorted(mylist, key=cmp_to_key(acmp))
