import locale


def rupiah_formatting(amount, with_prefix=True, decimal=0):
    locale.setlocale(locale.LC_NUMERIC, 'id_ID.UTF-8')
    result = locale.format_string("%.*f", (decimal, amount), True)
    if with_prefix:
        return "Rp. {}".format(result)
    return result
