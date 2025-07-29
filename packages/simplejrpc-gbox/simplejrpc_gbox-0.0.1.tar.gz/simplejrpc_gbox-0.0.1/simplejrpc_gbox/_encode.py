import html


def xss_encode(text):
    """
    名称输入序列化
    :param text:
    :return:
    """
    xss_list = ["<", ">"]
    ret = []
    for i in text:
        if i in xss_list:
            i = ""
        ret.append(i)
    str_convert = "".join(ret)

    text2 = html.escape(str_convert, quote=True)

    reps = {"&amp;": "&"}
    for rep in reps:
        if text2.find(rep) != -1:
            text2 = text2.replace(rep, reps[rep])
    return text2


def xss_encode2(text):
    """ """
    try:
        from cgi import html

        return html.escape(text, quote=True)
    except Exception:
        return (
            text.replace("&", "&amp;")
            .replace('"', "&quot;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
