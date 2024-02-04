from decimal import Decimal

from shop.models import ProductProxy


class Cart():
    """Корзина, хранящая в себе товары для дальнейшего заказа. Все данные хранит в сессии.

        Методы:

        __len__ = получает количество всех предметов в ней;
        __iter__ = получает все продукты из базы данных по их id, хранящихся в сессии;
        add = добавляет продукт в корзину;
        delete = удаляет продукт из корзины;
        update = обновляет количество товара в корзине на то, которое указано пользователем
        get_total_price = получает итоговую стоимость всей корзины
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

    # def add_promo(self, coupon, discount):
    #     coupon = str(coupon.code)
    #     if coupon not in self.cart:
    #         self.cart['coupon'] = {'code': coupon, 'discount': discount, 'qty': 0, 'price': 0}
    #         self.cart['coupon']['qty'] = 0
    #     self.session.modified = True

    def get_total_price(self):
        cart = self.cart.copy()
        total_price = sum(Decimal(item['price']) * item['qty'] for item in self.cart.values())
        return total_price
