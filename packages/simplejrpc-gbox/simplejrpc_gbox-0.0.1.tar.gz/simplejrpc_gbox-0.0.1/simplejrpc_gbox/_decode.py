def xss_decode(text):
    """
    名称输入反序列化
    :param text:
    :return:
    """
    try:
        cs = {"&quot": '"', "&#x27": "'"}
        for c in cs:
            text = text.replace(c, cs[c])

        str_convert = text
        import html

        return html.unescape(str_convert)
    except Exception:
        return text
