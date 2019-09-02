from collections import OrderedDict
import configparser


class ConfigOperator:
    def __init__(self, file_path):
        config = configparser.ConfigParser()
        self.file_path = file_path
        self.file = open(file_path)
        config.read_file(self.file)
        self.config = config
        self._all_data = None

    def get_all(self):
        if self._all_data is None:
            od = OrderedDict()
            for section in self.config.values():
                section_name = section.name
                tmp = {}
                if section_name != "DEFAULT":
                    od[section_name] = tmp
                    for key in section.keys():
                        v = section.get(key)
                        tmp[key] = v
            self._all_data = od
            return od
        return self._all_data

    def get(self, section, key=None):
        data = self.get_all().get(section)
        if key:
            data = data.get(key)
        return data

    def update(self, section, key, value):
        self.config.set(section=section, option=key, value=value)

    def overwrite(self):
        self.file.close()
        new_file = open(self.file_path, "w", encoding="utf8")
        self.config.write(new_file)
        new_file.close()


if __name__ == '__main__':
    operator = ConfigOperator("frpc.ini")
    print(operator.get_all())
    operator.update(section="homeip", key="http_pwd", value="update")
    operator.overwrite()
