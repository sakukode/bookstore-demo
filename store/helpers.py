import locale
import http
import json
from django.conf import settings


def rupiah_formatting(amount, with_prefix=True, decimal=0):
    locale.setlocale(locale.LC_NUMERIC, 'id_ID.UTF-8')
    result = locale.format_string("%.*f", (decimal, amount), True)
    if with_prefix:
        return "Rp. {}".format(result)
    return result


def convert_rupiah_to_float(amount_with_currency):
    locale.setlocale(locale.LC_NUMERIC, 'id_ID.UTF-8')
    amount = locale.atof(amount_with_currency.strip("Rp. "))

    return float(amount)


def get_shipping_cost(courier, origin, destination, weight):
    if weight < 1:
        weight = 1

    conn = http.client.HTTPSConnection(settings.RAJAONGKIR_API_URL)

    payload = "origin={origin}&destination={destination}&weight={weight}&courier={courier}".format(
        origin=origin,
        destination=destination,
        weight=weight, courier=courier
    )

    headers = {
        'key': settings.RAJAONGKIR_API_KEY,
        'content-type': "application/x-www-form-urlencoded"
    }

    conn.request("POST", "/{plan}/cost".format(plan=settings.RAJAONGKIR_ACCOUNT_PLAN), payload, headers)
    res = conn.getresponse()
    data = res.read()
    result = json.loads(data.decode("utf-8"))
    costs = []

    if result['rajaongkir']['status']['code'] == 200:
        responseCosts = result['rajaongkir']['results'][0]['costs']

        for responseCost in responseCosts:
            costs.append({
                'service': responseCost['service'],
                'description': responseCost['description'],
                'cost': {
                    'value': responseCost['cost'][0]['value'],
                    'label': rupiah_formatting(responseCost['cost'][0]['value'])
                }
            })

    return costs
