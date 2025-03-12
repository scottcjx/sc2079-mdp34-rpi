class Protocol:
    @staticmethod
    def serialize(message):
        return message.encode('utf-8')

    @staticmethod
    def deserialize(data):
        return data.decode('utf-8')