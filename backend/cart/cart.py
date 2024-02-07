from decimal import Decimal

from shop.models import ProductProxy


class Cart:
    """Cart, that stores products for order. Based on sessions.

        Methods:

        __len__ = calcutes quantity of products in cart;
        __iter__ = get products and presents they by their id's in a session;
        add = adds product in a cart;
        delete = deletes product from cart;
        update = updates product's quantity to the one specified by the user;
        get_total_price = gets total price of all products in cart
        """

    def __init__(self, request) -> None:

        self.session = request.session

        cart = self.session.get('session_key')

        if not cart:
            cart = self.session['session_key'] = {}

        self.cart = cart

    def __len__(self):
        return sum(item['qty'] for item in self.cart.values())

    def __iter__(self):
        product_ids = [key for key in self.cart.keys()]
        products = ProductProxy.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product
            cart[str(product.id)]['product_pk'] = product.pk

        for key, item in cart.items():
            item['price'] = Decimal(item['price'])
            item['total'] = item['price'] * item['qty']
            yield item

    def add(self, product, quantity):

        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {'qty': quantity, 'price': str(product.get_discounted_price())}

        self.cart[product_id]['qty'] = quantity

        self.session.modified = True

    def delete(self, product):
        product_id = str(product)
        if product_id in self.cart:
            del self.cart[product_id]
            self.session.modified = True

    def update(self, product, quantity):
        product_id = str(product)
        if product_id in self.cart:
            self.cart[product_id]['qty'] = quantity
            self.session.modified = True

    def get_total_price(self):
        cart = self.cart.copy()
        total_price = sum(Decimal(item['price']) * item['qty'] for item in self.cart.values())
        return total_price
