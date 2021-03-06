import os
from os.path import expanduser
from . import tools
from .fsentry import IOError
from .fsentry import FSEntry
from .file import File



class Directory(FSEntry):
    __slots__ = ["uri", "type", "name"]

    def __init__(self, uri):
        if uri.startswith("~"):
            path = expanduser("~")
            if len(uri) > 1:
                uri = uri[1:]
            else:
                uri = os.sep
            if uri[0] != os.sep:
                uri = "{sep}{uri}".format(sep=os.sep, uri=uri)

            uri = "{pfx}{sfx}".format(pfx=path, sfx=uri)


        if os.path.isabs(uri) is False:
            try:
                #is this a relative path? try and resolve the real path
                retry = os.path.realpath(uri)
                if os.path.isabs(retry):
                    uri = retry
            except Exception, ex:
                raise IOError("Invalid uri-> %s" % uri, ex)

            if os.path.isabs(uri) is False:
                raise IOError("Invalid uri-> %s" % uri)

        self.uri = uri
        if uri.endswith(os.sep) is False:
            self.uri = "%s%s" % (uri, os.sep)

        if tools.is_dir(self.uri) is False:
            raise IOError("Invalid uri-> %s" % uri)

        #self.type = "Directory"

        parts = os.path.normpath(self.uri).split(os.path.sep)
        self.name = parts[len(parts) - 1]

    def files(self, *patterns, **kwd):
        if self.exists is False:
            return []

        pattern = None if len(patterns) == 0 else patterns[0]

        contents = tools.contents(
            self.uri,
            include_folders=False,
            pattern=pattern,
            recursive=kwd.get("recursive", False)
        )

        list = []
        for file in contents:
            list.append(File(file))

        return list

    def folders(self):
        if self.exists is False:
            return []

        contents = tools.contents(
            self.uri,
            include_files=False
        )

        list = []
        for folder in contents:
            list.append(Directory(folder))

        return list

    def contents(self, *patterns, **kwd):
        if self.exists is False:
            return []

        pattern = None if len(patterns) == 0 else patterns[0]
        recursive = kwd.get("recursive", False)

        contents = tools.contents(
            self.uri,
            pattern=pattern,
            recursive=recursive
        )

        files, folders = [], []
        for path in contents:
            if tools.is_file(path) is True:
                files.append(File(path))
            else:
                folders.append(Directory(path))

        if len(files) > 0:
            folders.extend(files)
        return folders

    def folder(self, path):
        return self.sub(path)

    def sub(self, path):
        return self.relative(path, cls=Directory)

    def file(self, path):
        return self.relative(path, cls=File)

    @property
    def siblings(self):
        parent = self.parent
        return parent.contents() if parent is not None else self.contents()

    @property
    def children(self):
        return self.folders()

    def find_dir(self, name, reverse=False):
        for folder in self.walk_dirs(reverse=reverse, recursive=True):
            sub = folder.folder(name)
            if sub.exists:
                return sub
        return None

    def walk_files(self, reverse=False, recursive=False):
        return self.__walker__(file_mode=True, reverse=reverse, recursive=recursive)

    def walk_dirs(self, reverse=False, recursive=False):
        return self.__walker__(file_mode=False, reverse=reverse, recursive=recursive)

    def __walker__(self, file_mode=False, reverse=False, recursive=False):
        current = self
        while True:
            if file_mode is True:
                files = current.files()
                for file in files:
                    yield file
            else:
                folders = current.folders()
                for folder in folders:
                    yield folder

            if reverse is True:
                while current.parent is not None:
                    current = current.parent
                    if file_mode is True:
                        files = current.files()
                        for file in files:
                            yield file
                    else:
                        folders = current.folders()
                        for folder in folders:
                            yield folder
                break

            if recursive is False:
                break

            def __iterate__(file_mode, sub):
                if file_mode is True:
                    files = sub.files()
                    for file in files:
                        yield file
                else:
                    folders = sub.folders()
                    for folder in folders:
                        yield folder

                folders = sub.folders()
                for folder in folders:
                    __iterate__(file_mode, folder)


            subs = current.folders()
            for sub in subs:
                __iterate__(file_mode, sub)
            return

                # history[sub.uri] = 1
                # if file_mode is True:
                #     files = sub.files()
                #     for file in files:
                #         yield file
                # else:
                #     folders = sub.folders()
                #     for folder in folders:
                #         yield folder
                #
                # inner = sub.folders()
                # while len(inner) > 0:
                #     inner_sub = inner[0]
                #     inner = inner[1:] if len(inner) > 0 else []
                #
                #     if file_mode is True:
                #         files = inner_sub.files()
                #         for file in files:
                #             yield file
                #     else:
                #         folders = inner_sub.folders()
                #         for folder in folders:
                #             yield folder
                #
                #     inner_sub_dirs = inner_sub.folders()
                #     if len(inner_sub_dirs) > 0:
                #         for i in inner_sub_dirs:
                #             if history.get(i.uri, None) is None:
                #                 history[i.uri] = 1
                #                 inner.append(i)
                #
                #         #inner.extend(inner_sub_dirs)

    def reverse_search(self, name):
        return self.search(name, reverse_search=True)

    def search(self, name, reverse_search=False):
        key = name.strip().lower()
        current = self

        others = current.contents()
        for o in others:
            if o.name.lower() == key:
                return o

        if reverse_search is True:
            current = current.parent
            if current is None:
                return None

            subs = current.folders()
            # if len(subs) == 0:
            #     return None

            for sub in subs:
                if sub.file(name).exists is True:
                    return sub.file(name)





            return current.search(name, reverse_search=True)

        subs = current.folders()
        for sub in subs:
            result = sub.search(name, reverse_search=False)
            if result is not None:
                return result

        return None

    def clear(self):
        files = self.files()
        [f.delete() for f in files]
        folders = self.folders()
        [f.clear().delete() for f in folders]
        return self

    @staticmethod
    def current():
        uri = os.getcwd()
        return Directory(uri)