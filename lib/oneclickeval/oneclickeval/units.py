import re
import copy

class IUnit:
    def __init__(self, qid, iid, score, vslen):
      self.qid = qid
      self.iid = iid
      self.score = score
      self.vslen = vslen
      self.entail = []

    def __str__(self):
      return "%s %s %s %s %s" % (self.qid, self.iid, self.score, 
                              self.vslen, ','.join(self.entail))


class IUnitSet:
    LINE_FORMAT = re.compile(r'([^ ]+)[ ]([^ ]+)[ ]([^ ]+)[ ]([^ ]+)[ ]?([^ ]*)')
    def __init__(self, iunits):
      self._iunits = {}
      for i in iunits:
        q = self._iunits.get(i.qid, {})
        q[i.iid] = i
        self._iunits[i.qid] = q

      self._cache = {}

    def __iter__(self):
      for qid in sorted(self._iunits.keys()):
        for i in self.get(qid):
          yield i

    def qids(self):
      return sorted(self._iunits.keys())

    def remove(self, qid, iid):
      iunit = self.get(qid, iid)
      entaileds = self.get_all_entailing(qid, iid)
      for e in entaileds:
        del self._iunits[e.qid][e.iid]
      # remove this after removing entaileds
      del self._iunits[qid][iid]

    def get(self, qid, iid = None):
      q = self._iunits.get(qid, None)
      if q:
        if iid:
          return q.get(iid, None)
        else:
          return sorted(q.values(), key=lambda x: x.iid)
      else:
        return []

    def get_all_entailed(self, qid, iid):
      iunit = self.get(qid, iid)
      entails = iunit.entail
      result = []
      for e in entails:
        result.append(self.get(qid, e))
        result += self.get_all_entailed(qid, e)

      return set(result)

    def get_all_entailing(self, qid, iid):
      iunit = self.get(qid, iid)
      iunits = self.get(qid)
      result = []
      for i in iunits:
        if iid in i.entail:
          result.append(i)
          result += self.get_all_entailing(qid, i.iid)
      return set(result)

    """
    1. Create cummulative iUnits
    2. Evaluate each cummulative iunit for S-measure
    3. Add an iUnit to the ideal X-string that maximize the S-measure
    """
    def pseudo_minimal_output(self, qid, l, maxlen):
      key = tuple([qid, l, maxlen] + [i.iid for i in self.get(qid)])
      if key in self._cache:
        return self._cache[key]

      iunits = copy.deepcopy(self.get(qid))
      result = []

      # 1. Create cummulative iUnits
      self._cumulate(iunits)

      # 2. Evaluate each cummulative iunit for S-measure
      offset = 0
      while True:
        # S-measure
        #######################################################################
        def s(i, l, offset): 
          return float(i.score) * float(l - (offset + i.vslen))
        #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        #######################################################################
        # make pairs of iUnit and estimated S-measure that do not exceed maxlen
        iunit_scores = [(i, s(i, l, offset)) for i in iunits 
          if offset + i.vslen < maxlen and i.score > 0]
        # termination condition
        if len(iunit_scores) == 0: break

        (max_iunit, max_score) = max(iunit_scores, key=lambda x: x[1])

        # 3. Add an iUnit to the ideal X-string that maximize the S-measure
        result.append(max_iunit)
        offset += max_iunit.vslen
        self._update_iunits(qid, iunits, max_iunit)

      # cache
      self._cache[key] = result

      return result

    def _update_iunits(self, qid, iunits, max_iunit):
      # delete an used iUnit
      iunits.remove(max_iunit)

      # remove entailed iUnits
      entailed_iids = [i.iid for i in self.get_all_entailed(qid, max_iunit.iid)]
      for i in self._iter_process(iunits, entailed_iids):
        iunits.remove(i)

      self._cumulate(iunits)

    def _cumulate(self, iunits):
      iids = [i.iid for i in iunits]
      for i in iunits:
        entaileds = self.get_all_entailed(i.qid, i.iid)
        iunit = self.get(i.qid, i.iid)
        i.score = iunit.score + sum([e.score for e in entaileds if e.iid in iids])
        i.vslen = iunit.vslen + sum([e.vslen for e in entaileds if e.iid in iids])

    def _iter_process(self, iunits, iids):
      for i in [i for i in iunits if i.iid in iids]:
        yield i

    @classmethod
    def read(cls, filename):
      result = []
      with open(filename, 'r') as f:
        for line in f:
          iunit = cls.parse_line(line)
          if iunit:
            result.append(iunit)

      return IUnitSet(result)

    @classmethod
    def parse_line(cls, line):
      m = cls.LINE_FORMAT.match(line)
      if m:
        (qid, iid, score, vslen, entail) = (g.strip() for g in m.groups())
        iunit = IUnit(qid = qid, iid = iid, 
                      score = int(score), vslen = int(vslen))
        if len(entail) > 0:
          iids = [i.strip() for i in entail.split(',')]
          iunit.entail += iids
        return iunit
      else:
        return None

class XString:
    SYSLEN = "syslen="
    LINE_FORMAT = re.compile(r'([^ ]+)[ ]([^ ]+)[ ]([^ ]+)')

    def __init__(self, lens, matches):
      self._lens = copy.copy(lens)
      self._matches = {}
      for m in matches:
        q = self._matches.get(m.qid, {})
        q[m.iid] = m
        self._matches[m.qid] = q

      # validation
      for qid in self._matches.keys():
        if not qid in self._lens.keys():
          raise Exception('Syslen for %s is missing' % qid)

    def get(self, qid, iid = None):
      q = self._matches.get(qid, {})
      if iid:
        return q.get(iid, None)
      else:
        matches = sorted(q.values(), key=lambda x: x.iid)
        return matches

    def qids(self):
      return sorted(self._lens.keys())

    def len(self, qid):
      return self._lens.get(qid, None)

    def __iter__(self):
      for qid in self.qids():
        for match in self.get(qid):
          yield match

    @classmethod
    def read(cls, filename):
      matches = []
      lens = {}
      with open(filename, 'r') as f:
        for line in f:
          match = cls.parse_line(line)
          if match:
            if isinstance(match, IUnitMatch):
              matches.append(match)
            else:
              lens[match[0]] = match[1]

      return XString(lens, matches)

    @classmethod
    def parse_line(cls, line):
      m = cls.LINE_FORMAT.match(line)
      if m:
        (qid, iid, offset) = (g.strip() for g in m.groups())
        if iid == cls.SYSLEN:
          return (qid, int(offset))
        else:
          return IUnitMatch(qid = qid, iid = iid, offset = int(offset))
      else:
        return None


class IUnitMatch:
    def __init__(self, qid, iid, offset):
      self.qid = qid
      self.iid = iid
      self.offset = offset
    
    def __str__(self):
      return "%s\t%s\t%s" % (self.qid, self.iid, self.offset)


if __name__ == '__main__':
    IUNIT_FILENAME = '/home/kato/rails_system/one_click_eval/1C2-J.iunits'
    INPUT_MAT = '/home/kato/rails_system/one_click_eval/batch/result/mat/MANUAL-J-D-OPEN-1.union'

    iunitset = IUnitSet.read(IUNIT_FILENAME)
    xstring = XString.read(INPUT_MAT)

    for x in xstring.get('1C2-J-0001'):
      print x

