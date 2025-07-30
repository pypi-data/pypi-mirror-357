import hashlib
import urllib
from urllib.parse import ParseResult
import pwgen

class URLSign(object):
    def __init__(self, password, hash_method=hashlib.sha512, sign_parameter_name="sign", salt_parameter_name="salt", salt_size=32):
        self.password = password
        self.hash_method = hash_method
        self.sign_parameter_name = sign_parameter_name
        self.salt_parameter_name = salt_parameter_name
        self.salt_size = salt_size
    
    def sign(self, url):
        salt = pwgen.pwgen(self.salt_size)
        info = urllib.parse.urlparse(url)
        parameters = urllib.parse.parse_qsl(info.query)
        text = ""
        for parameter in parameters:
            text += parameter[0]
            text += parameter[1]
        text += salt
        text += self.password
        sign = self.hash_method(text.encode("utf-8")).hexdigest()
        parameters.append((self.salt_parameter_name, salt))
        parameters.append((self.sign_parameter_name, sign))
        new_query = urllib.parse.urlencode(parameters)
        new_info = ParseResult(
            info.scheme,
            info.netloc,
            info.path,
            info.params,
            new_query,
            info.fragment,
        )
        return new_info.geturl()

    def verify(self, url):
        sign = None
        salt = None
        info = urllib.parse.urlparse(url)
        parameters = urllib.parse.parse_qsl(info.query)
        text = ""
        for parameter in parameters:
            if parameter[0] == self.sign_parameter_name:
                sign = parameter[1]
            elif parameter[0] == self.salt_parameter_name:
                salt = parameter[1]
            else:
                text += parameter[0]
                text += parameter[1]
        if (not sign) or (not salt):
            return False
        text += salt
        text += self.password
        new_sign = self.hash_method(text.encode("utf-8")).hexdigest()
        return new_sign == sign
