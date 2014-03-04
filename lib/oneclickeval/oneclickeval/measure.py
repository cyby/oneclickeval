from oneclickeval.units import IUnit, IUnitMatch, IUnitSet, XString
import unittest

class OneClickMeasure:
    @classmethod
    def recall(cls, iunits, matches):

        denominator = float(len(iunits))
        numerator = float(len(matches))

        return numerator / denominator if denominator != 0 else 0.0

    @classmethod
    def wrecall(cls, iunits, matches):
        idict = dict([(i.iid, i) for i in iunits])

        denominator = float(sum([i.score for i in iunits]))
        numerator = float(sum([idict[m.iid].score for m in matches]))

        return numerator / denominator if denominator != 0 else 0.0

    @classmethod
    def smeasure(cls, iunits, pmo, matches, l):
        denominator = cls._pmoscore(pmo, l)
        numerator = cls._smeasure_calc(iunits, matches, l)

        return numerator / denominator if denominator != 0 else 0.0

    @classmethod
    def sflat(cls, iunits, pmo, matches, l):
        return min([1.0, cls.smeasure(iunits, pmo, matches, l)])

    @classmethod
    def tmeasure(cls, iunits, matches, syslen):
        if not len(matches) > 0: return 0.0
        idict = dict([(i.iid, i) for i in iunits])

        denominator = float(syslen)
        numerator = float(sum([idict[m.iid].vslen for m in matches]))

        return numerator / denominator if denominator != 0 else 0.0

    @classmethod
    def tflat(cls, iunits, matches, syslen):
        return min([1.0, cls.tmeasure(iunits, matches, syslen)])

    @classmethod
    def ssharp(cls, iunits, pmo, matches, l, syslen, beta):
        sflat = cls.sflat(iunits, pmo, matches, l)
        tflat = cls.tflat(iunits, matches, syslen)

        numerator = (1.0 + beta ** 2) * sflat * tflat
        denominator = beta ** 2 * tflat + sflat

        return numerator / denominator if denominator != 0 else 0.0

    @classmethod
    def _pmoscore(cls, pmo, l):
        result = 0.0
        offset = 0
        for m in pmo:
            offset += m.vslen
            result += cls._s(m.score, offset, l)
        return result

    @classmethod
    def _s(cls, score, offset, l): 
        return float(score) * max([0.0, float(l - offset)])

    @classmethod
    def _smeasure_calc(cls, iunits, matches, l):
        idict = dict([(i.iid, i) for i in iunits])
        result = 0.0
        for m in matches:
            result += cls._s(idict[m.iid].score, m.offset, l)
        return result

class TestOneClickMeasure(unittest.TestCase):
    L = 500
    MAXLEN = 500
    def setUp(self):
        qid = '1C2-J-0001'
        self.qid = qid
        self.syslen = 500
        self.beta = 10
        iunits = []
        iunits.append(IUnit(qid, 'I001', 2, 5))
        iunits.append(IUnit(qid, 'I002', 1, 8))
        iunits.append(IUnit(qid, 'I003', 1, 9))
        iunits.append(IUnit(qid, 'I004', 2, 4))
        iunits.append(IUnit(qid, 'I005', 2, 3))
        iunits[1].entail.append('I001')
        iunits[2].entail.append('I002')
        self.iunitset = IUnitSet(iunits)
        self.matches = []
        self.matches.append(IUnitMatch(qid, 'I001', 10))
        self.matches.append(IUnitMatch(qid, 'I002', 10))
        self.matches.append(IUnitMatch(qid, 'I004', 50))
        self.matches.append(IUnitMatch(qid, 'I005', 100))

    def test_recall(self):
        iunits = self.iunitset.get(self.qid)
        actual = OneClickMeasure.recall(iunits, self.matches)
        ideal = 4. / 5
        self.assertEqual(actual, ideal)

    def test_wrecall(self):
        iunits = self.iunitset.get(self.qid)
        actual = OneClickMeasure.wrecall(iunits, self.matches)
        ideal = 7. / 8
        self.assertEqual(actual, ideal)
    
    def test_pmo(self):
        pmo = self.iunitset.pseudo_minimal_output(self.qid, self.L, self.MAXLEN)
        self.assertEqual(pmo[0].iid, 'I003')
        self.assertEqual(pmo[1].iid, 'I005')
        self.assertEqual(pmo[2].iid, 'I004')
        self.assertEqual(len(pmo), 3)

    def test_smeasure(self):
        iunits = self.iunitset.get(self.qid)
        pmo = self.iunitset.pseudo_minimal_output(self.qid, self.L, self.MAXLEN)
        actual = OneClickMeasure.smeasure(iunits, pmo, self.matches, self.L)
        ideal = 3170. / 3804
        self.assertEqual(actual, ideal)

    def test_tmeasure(self):
        iunits = self.iunitset.get(self.qid)
        actual = OneClickMeasure.tmeasure(iunits, self.matches, self.syslen)
        ideal = 20. / 500
        self.assertEqual(actual, ideal)

    def test_ssharp(self):
        iunits = self.iunitset.get(self.qid)
        pmo = self.iunitset.pseudo_minimal_output(self.qid, self.L, self.MAXLEN)
        actual = OneClickMeasure.ssharp(iunits, pmo, self.matches, self.L,
            self.syslen, self.beta)
        s = OneClickMeasure.smeasure(iunits, pmo, self.matches, self.L)
        t = OneClickMeasure.tmeasure(iunits, self.matches, self.syslen)
        ideal = (1 + 100) * s * t / (100 * t + s)
        self.assertEqual(actual, ideal)


if __name__ == '__main__':
    unittest.main()
