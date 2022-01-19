
HEADERSIZE = 64




def get_header(message_bytes : bytes, headersize: int = HEADERSIZE) -> bytes:
    """
    creating a header as bytes 
    """
    header = f"{len(message_bytes):<{headersize}}".encode()
    return header

def decode_header(header : bytes) -> int: 
    """
    decoding a header to int
    """
    header : str = header.decode()
    header = header.strip(" ")
    bytesize = int(header)
    return bytesize