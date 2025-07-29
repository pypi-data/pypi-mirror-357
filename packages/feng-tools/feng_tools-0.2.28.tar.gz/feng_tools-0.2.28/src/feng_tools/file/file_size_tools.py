
one_kb = 1024
one_mb = 1024 * 1024
one_gb = 1024 * 1024 * 1024


def format_size(file_size: int) -> str | None:
    """格式化文件大小"""
    if file_size is None:
        return file_size
    if file_size < 1024:
        return f'{file_size}B'
    elif file_size // one_kb < 1024:
        return f'{round(file_size / one_kb, 2)}KB'
    elif file_size // one_mb < 1024:
        return f'{round(file_size / one_mb, 2)}MB'
    else:
        return f'{round(file_size / one_gb, 2)}GB'


def parse_size(file_size: str) -> int | None:
    """
    转换文件大小
    :param file_size: 文件大小，如：2MB
    :return: 文件大小int值
    """
    if file_size is None:
        return file_size
    file_size = file_size.strip()
    if file_size.endswith('KB') or file_size.endswith('kb'):
        return int(float(file_size.removesuffix('KB').removesuffix('kb')) * one_kb)
    elif file_size.endswith('K') or file_size.endswith('k'):
        return int(float(file_size.removesuffix('K').removesuffix('k')) * one_kb)
    elif file_size.endswith('MB'):
        return int(float(file_size.removesuffix('MB')) * one_mb)
    elif file_size.endswith('M'):
        return int(float(file_size.removesuffix('M')) * one_mb)
    elif file_size.endswith('GB'):
        return int(float(file_size.removesuffix('GB')) * one_gb)
    elif file_size.endswith('G'):
        return int(float(file_size.removesuffix('G')) * one_gb)
    elif file_size.endswith('B'):
        return int(file_size.removesuffix('B'))
    return int(file_size)

if __name__ == '__main__':
    print(format_size(1024))