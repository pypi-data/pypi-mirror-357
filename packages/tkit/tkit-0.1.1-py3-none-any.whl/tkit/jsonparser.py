
import jsonpath_ng


class JsonParser(object):

    def __init__(self, data):
        self.data = data

    def extract(self, path, default=None):
        expr = jsonpath_ng.parse(path)
        matches = expr.find(self.data)
        if matches:
            if len(matches) > 1:
                return [x.value for x in matches]
            else:
                return matches[0].value
        else:
            return default

    def fix(self, data):
        if data is None:
            return None
        if isinstance(data, str):
            if data.startswith("$"):
                return self.extract(data)
            else:
                return data
        elif isinstance(data, list):
            result = []
            for item in data:
                result.append(self.fix(item))
            return result
        elif isinstance(data, tuple):
            result = []
            for item in data:
                result.append(self.fix(item))
            return tuple(result)
        elif isinstance(data, set):
            result = []
            for item in data:
                result.append(self.fix(item))
            return set(result)
        elif isinstance(data, dict):
            result = {}
            for k, v in data.items():
                result[k] = self.fix(v)
            return result
        else:
            return data
