import struct
import numpy as np

#                                              #          
#      ###    ###       #           #   ###    #    ###   
#     #   #      #      #           #      #  ###      #  
#     #   #   ####   ####        ####   ####   #    ####  
#     #   #  #   #  #   #       #   #  #   #   #   #   #  
####   ###    ####   ####        ####   ####   ##   ####

def load_bin_file(path, datatype, start_offset=None, end_offset=None):
    size_map = {
        "uint8": ("B", 1), "int8": ("b", 1),
        "uint16_le": ("<H", 2), "uint16_be": (">H", 2),
        "int16_le": ("<h", 2), "int16_be": (">h", 2),
        "uint32_le": ("<I", 4), "uint32_be": (">I", 4),
        "int32_le": ("<i", 4), "int32_be": (">i", 4),
        "float32_le": ("<f", 4), "float32_be": (">f", 4),
    }

    fmt, size = size_map[datatype]

    with open(path, "rb") as f:
        full_data = f.read()

    if start_offset is None:
        start_offset = 0
    if end_offset is None or end_offset > len(full_data):
        end_offset = len(full_data)

    data = full_data[start_offset:end_offset]

    total = len(data) // size
    unpacked = struct.iter_unpack(fmt, data[: total * size])
    arr = np.array([x[0] for x in unpacked])

    return arr, size
