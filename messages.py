


SEPERATOR = b"<|sep|>"
STARTER = b"<|start|>"
ENDER = b"<|end|>"



def read_message(message_bytes) -> tuple[bytes,bytes]:
    """ 
    Reading a message with the format: \n
    [0] STARTER  + [1] SEPERATOR + [2] data1 + [3] SEPERATOR + [4] data2 + [5] SEPERATOR + [6] ENDER 

    """
    message_split =  message_bytes.split(SEPERATOR)
    
    starter = message_split[0]
    if not starter == STARTER:
        raise Exception(f"StarterException: erhaltener starter: {starter} stimmt nicht mit dem vorgegebenen STARTER: {STARTER} überein.")
    seperators = [message_split[1], message_split[3], message_split[5]]

    for seperator in seperators:
        if not seperator == SEPERATOR:
            raise Exception(f"SeperatorException: erhaltener seperator: {seperator} stimmt nicht mit dem vorgegebenen SEPERATOR: {SEPERATOR} überein.")

    ender = message_split[-1]
    if not ender == ENDER:
        raise Exception(f"EnderException: erhaltener ender: {ender} stimmt nicht mit dem vorgegebenen ENDER: {ENDER} überein.")

    data1 = message_split[2]
    data2 = message_split[4]

    return data1, data2
        
    
def format_message(data1: bytes = "", data2:bytes = "" ) -> bytes:
    """
    Formatting a message with the format: \n
    [0] STARTER  + [1] SEPERATOR + [2] data1 + [3] SEPERATOR + [4] data2 + [5] SEPERATOR + [6] ENDER 
    
    """
    message : bytes = STARTER + SEPERATOR+ data1 + SEPERATOR + data2 +SEPERATOR+ ENDER
    
    return message
