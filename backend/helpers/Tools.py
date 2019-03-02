class Tools:
    @staticmethod
    def getValue(value, default):
        if value:
            return value
        else:
            return default