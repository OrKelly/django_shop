# Description
This is a shop web app. This app have: a products catalog,
cart, payment, rating and sale system, promocodes and many other features.

### Account app
This is a user's account app. User can change his perfomance in this app (for example: 
change email, login and shipping address). He can see his order history, detail information about every order and total cost and count of all his orders

### Api app
This is a default API app. Other app can receive information about products, reviews and categories 
by this API. Also, user can be created using this API

### Recommend app

This app set's and store user reviews on products. User can add only one specified review for a product he bought.

### Shop app

The main page contains all available products of the store. There are also two collections with discounted goods and goods with the highest rating.
If product has sale or discount - special signs will appear in the header. User can add product in a product detail page.
Also, he can see reviews on this product in a bottom of page. If he has already bought this product and has not left a review before, he can leave a review.
If there is discount on this product - user will see cost before discount and discounted price.

### Cart app

When shopping, user can add some products in a cart to order them. Cart is based on sessions,
user can fill the cart even he isn't authorized. Cart calculates quantity and price of all products.
User can update product's quantity and delete his from a cart. Post request for update and delete are
sending by Ajax

### Payment app

When cart is completed, user can create order. In this web-app used two payment systems:
Stripe and Yookassa. Also, user can use promo-code while making pay. When the order is paid - user receive
email with order confirmation. Also order status changes to 'paid' and cart cleans up

### Account app
This is a user's account app. This app provides user authentication and registration. When user register - he receives mail with register confirmation. User can change his perfomance in this app (for example: 
change email, login and shipping address). He can see his order history, detail information about every order and total cost and count of all his orders


### Recommend app

This app set's and store user reviews on products. User can add only one specified review for a product he bought.


### Staff app

This is app for shop employee. They can work with products (CRUD operations), orders and promos. Employee can see active and completed/cancelled orders.
If order is active, employee can change order status or cancel order. When cancelling order, he can also send disposable promo-code, and user receives email
with details of cancel and promo(if had been chosen).

Employee can start and deactivate promos. He chooses discount percent and expires time. Also, he can choose, send this promo with email for all users all. If yes, then two fields appear with the mail template, 
which the employee can change or leave as is.

### Api app
This is a default API app. Other app can receive information about products, reviews and categories 
by this API. Also, user can be created using this API


# Techologes used

* Python
* Django
* Ajax  
* CSS  
* HTML  
* Postgres  
* Celery  
* Redis Broker  
* Django Htmx  
* Nginx  
* Gunicorn  
* API  
* Swagger and Redoc Docs  
* Stripe
* Yookassa
* Django Rest Framework
* Docker
* Docker Compose
