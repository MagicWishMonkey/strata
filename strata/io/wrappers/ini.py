from strata.utilities.structs import *
from strata.io.wrappers.abstract import FileWrap


class INI(FileWrap):
    def __init__(self, uri):
        FileWrap.__init__(self, uri)
        self.default = SafeWrapper.create({})
        self.current = self.default
        self.sections = {"default": self.default}

        def __read__(txt):
            buffer = []
            lines = txt.splitlines(True)
            map(buffer.append, lines)
            return buffer


        self.decoder = __read__


    def read(self):
        lines = self.read_lines()
        map(self.append, lines)
        return self


    def append(self, line):
        from strata import util

        txt = line.strip()
        if len(txt) == 0:
            return self

        pfx = txt[0]
        if pfx == "#" or pfx == ";":
            return self

        ix = txt.find(";")
        if ix > -1:
            txt = txt[:ix]

        if pfx == "[":
            if txt.endswith("]") is True:
                section = txt[1:len(txt)-1]
                section = section.lower()
                self.current = SafeWrapper.create({})
                self.sections[section] = self.current
                return self

        line = txt
        parts = line.split("=")
        key = parts[0].strip()
        val = "=".join(parts[1:]).strip()
        if val.isdigit() is True:
            val = int(val)
        elif val[0] == "{" or val[0] == "[":
            try:
                val = util.unjson(val)
            except:
                pass
        else:
            small = val.lower()
            if small == "true" or small == "yes":
                val = True
            elif small == "false" or small == "no":
                val = False
        self.current[key] = val
        self.buffer.append(line)
        return self

    def section(self, section):
        section_name = section.lower()
        try:
            return self.sections[section_name]
        except:
            raise Exception("The section could not be found: %s" % section)

    def __getitem__(self, field):
        try:
            return self.default[field]
        except:
            try:
                return self.default[field.strip().lower()]
            except:
                return None

    def __setitem__(self, key, value):
        self.default[key] = value


    def __getattr__(self, field):
        try:
            return self.default[field]
        except:
            try:
                return self.default[field.strip().lower()]
            except:
                return None


    def stringify(self):
        from strata import util

        sections = self.sections
        def append_section(buffer, section):
            keys = section.keys()
            for key in keys:
                val = section[key]
                if isinstance(val, basestring) is False:
                    if isinstance(val, bool) is True:
                        val = str(val).lower()
                    elif isinstance(val, (dict, list)) is True:
                        val = util.json(val)
                    else:
                        val = str(val)
                buffer.append("%s=%s" % (key, val))

        buffer = []
        if len(self.default.keys()) > 0:
            append_section(buffer, self.default)
        if len(sections.keys()) == 1:
            return "\n".join(buffer)

        for key in sections.keys():
            if key == "default":
                continue
            section = sections[key]

            if len(buffer) > 0:
                buffer.append("\n")
            buffer.append("[%s]" % key)
            append_section(buffer, section)

        return "\n".join(buffer)

    def __str__(self):
        sections = self.sections.values()
        section_count = len(sections)
        field_count = sum([len(s.keys()) for s in sections])
        return "INI: %s sections, %s fields" % (str(section_count), str(field_count))

    def __repr__(self):
        return self.__str__()

    # @classmethod
    # def parse(cls, txt):
    #     ini = cls()
    #     lines = txt.splitlines(True)
    #     map(ini.append, lines)
    #     return ini