def sort_dict(sort_d: dict, use_key=True, reverse=False):
    """
    字典排序
    :param sort_d:
    :param use_key:
    :param reverse:
    :return:
    """
    sorted_tuples = (
        sorted(sort_d.items(), key=lambda d: d[0], reverse=reverse)
        if use_key
        else sorted(sort_d.items(), key=lambda d: d[1], reverse=reverse)
    )
    return dict(sorted_tuples)
