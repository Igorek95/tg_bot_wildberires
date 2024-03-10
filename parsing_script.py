import requests
import aiohttp


async def get_product_info(article):
    base_url = "https://card.wb.ru/cards/v1/detail"
    params = {
        "appType": 1,
        "curr": "rub",
        "dest": -1257786,
        "spp": 30,
        "nm": article,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=params) as response:
            product_json =await response.json()
            product_info = product_json.get('data')
            products = []
            for product in product_info.get('products'):
                name = product.get('name')
                article = product.get('id')
                price = product.get('salePriceU')
                rating = product.get('reviewRating')
                remaining_goods = 0
                for size in product.get('sizes'):
                    for stock_item in size['stocks']:
                        quantity = stock_item['qty']
                        remaining_goods += quantity
                products.append({
                    'name': name,
                    'id': article,
                    'price': price,
                    'rating': rating,
                    'remaining_goods': remaining_goods
                })
            try:
                product_data = {
                    'название': name,
                    'артикул': article,
                    'цена': f"{price // 100} руб",
                    'рейтинг товара': f"{rating}⭐",
                    'количество товара': f"{remaining_goods  } шт.",
                }
                return product_data
            except IndexError:
                return "Ошибка артикула"
