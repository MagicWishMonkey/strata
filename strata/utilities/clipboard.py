import os
import platform
try:
    import ctypes
except:
    pass


class Clipboard(object):
    __functions__ = {}

    def __init__(self):
        functions = Clipboard.__functions__
        if len(functions) == 0:
            if os.name == "nt" or platform.system() == "Windows":
                def winGetClipboard():
                    ctypes.windll.user32.OpenClipboard(0)
                    pcontents = ctypes.windll.user32.GetClipboardData(1) # 1 is CF_TEXT
                    data = ctypes.c_char_p(pcontents).value
                    ctypes.windll.user32.CloseClipboard()
                    return data

                def winSetClipboard(text):
                    GMEM_DDESHARE = 0x2000
                    ctypes.windll.user32.OpenClipboard(0)
                    ctypes.windll.user32.EmptyClipboard()
                    try:
                        # works on Python 2 (bytes() only takes one argument)
                        hCd = ctypes.windll.kernel32.GlobalAlloc(GMEM_DDESHARE, len(bytes(text))+1)
                    except TypeError:
                        # works on Python 3 (bytes() requires an encoding)
                        hCd = ctypes.windll.kernel32.GlobalAlloc(GMEM_DDESHARE, len(bytes(text, 'ascii'))+1)
                    pchData = ctypes.windll.kernel32.GlobalLock(hCd)
                    try:
                        # works on Python 2 (bytes() only takes one argument)
                        ctypes.cdll.msvcrt.strcpy(ctypes.c_char_p(pchData), bytes(text))
                    except TypeError:
                        # works on Python 3 (bytes() requires an encoding)
                        ctypes.cdll.msvcrt.strcpy(ctypes.c_char_p(pchData), bytes(text, 'ascii'))
                    ctypes.windll.kernel32.GlobalUnlock(hCd)
                    ctypes.windll.user32.SetClipboardData(1,hCd)
                    ctypes.windll.user32.CloseClipboard()
                functions["get"] = winGetClipboard
                functions["set"] = winSetClipboard
            elif os.name == "mac" or platform.system() == "Darwin":
                def macSetClipboard(text):
                    outf = os.popen('pbcopy', 'w')
                    outf.write(text)
                    outf.close()

                def macGetClipboard():
                    outf = os.popen('pbpaste', 'r')
                    content = outf.read()
                    outf.close()
                    return content

                functions["get"] = macGetClipboard
                functions["set"] = macSetClipboard
            else: #posix or linux
                xclipExists = os.system('which xclip') == 0
                if xclipExists:
                    functions["get"] = xclipGetClipboard
                    functions["set"] = xclipSetClipboard
                else:
                    xselExists = os.system('which xsel') == 0
                    if xselExists:
                        functions["get"] = xselGetClipboard
                        functions["set"] = xselSetClipboard
                    try:
                        import gtk
                        functions["get"] = gtkGetClipboard
                        functions["set"] = gtkSetClipboard
                    except:
                        try:
                            import PyQt4.QtCore
                            import PyQt4.QtGui
                            app = QApplication([])
                            cb = PyQt4.QtGui.QApplication.clipboard()
                            functions["get"] = qtGetClipboard
                            functions["set"] = qtSetClipboard
                        except:
                            pass

        self.get = functions["get"]
        self.set = functions["set"]

    @staticmethod
    def read():
        txt = Clipboard().get()
        return txt

    @staticmethod
    def write(txt):
        Clipboard().set(txt)