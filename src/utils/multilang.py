# Multi-language Support Stub
class MultiLangSupport:
    def __init__(self):
        self.languages = ['en']
        self.current_language = 'en'

    def add_language(self, lang_code):
        if lang_code not in self.languages:
            self.languages.append(lang_code)
            return True
        return False

    def set_language(self, lang_code):
        if lang_code in self.languages:
            self.current_language = lang_code
            return True
        return False
