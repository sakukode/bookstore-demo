import locale
import http
import json
from django.conf import settings
import midtransclient


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


def generate_invoice_number(order):
    prefix = 'INV'

    if not order:
        return f'{prefix}0001'

    invoice_int = order.id
    new_invoice_number = f'{prefix}{invoice_int:05d}'

    return new_invoice_number


def generate_payment_token(order):
    if not order:
        return False

    item_details = []
    # detail item produk dari tabel order_products
    for item in order.orderproduct_set.all():
        item_details.append({
            'price': int(item.price),
            'quantity': item.quantity,
            'name': item.product.name
        })

    # detail item biaya pengiriman
    item_details.append({
        'price': int(order.total_shipping),
        'quantity': 1,
        'name': 'Ongkir ' + order.shipping_courier + " " + order.shipping_service
    })

    # detail data customer
    customer_details = {
        'first_name': order.customer_name,
        'last_name': '',
        'email': order.user.email,
        'phone': order.customer_phone
    }

    # Membuat instance Snap API
    snap = midtransclient.Snap(
        is_production=settings.MIDTRANS_IS_PRODUCTION,
        server_key=settings.MIDTRANS_SERVER_KEY,
        client_key=settings.MIDTRANS_CLIENT_KEY
    )
    # Menyiapkan API parameter
    param = {
        "transaction_details": {
            "order_id": "skbookstore-" + str(order.id),
            "gross_amount": int(order.total),
        },
        "item_details": item_details,
        "customer_details": customer_details
    }
    # Memanggil API midtrans untuk membuat transaksi
    transaction = snap.create_transaction(param)
    # Jika sukses, API midtrans akan mengembalikan token di response
    transaction_token = transaction['token']

    return transaction_token
