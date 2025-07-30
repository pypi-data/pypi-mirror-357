import itertools
import pypinyin
from pypinyin import Style


class PinYinUtils(object):
    @classmethod
    def get(cls, str):
        rs = pypinyin.pinyin(str, style=Style.NORMAL)
        return "".join([r[0].capitalize() for r in rs])

    @classmethod
    def gets(cls, str):
        rs = pypinyin.pinyin(str, heteronym=True, style=Style.NORMAL)
        for item in itertools.product(*rs):
            yield "".join([x.capitalize() for x in item])
