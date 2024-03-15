import psycopg2

from dataclasses import dataclass
import memcache

@dataclass
class CachedDatabase:
    ip: str = '127.0.0.1'
    port: str = '11211'
    
    _mc = memcache.Client(servers=[f'{ip}:{port}'], debug=0)

    def set_values(self, key_value, values) -> None:
        self._mc.set(key_value, values)
    
    def get_values(self, key_value) -> list:
        return self._mc.get(key_value)
    
    def delete_values(self, key_value) -> None:
        self._mc.delete(key_value)

@dataclass
class Database:
    dbname: str = 'datas'
    user: str = 'postgres'
    password: str = '1234'
    host: str = 'localhost'
    port: int = '5432'

    _connection = psycopg2.connect(
        dbname= dbname,
        user=user,
        password=password,
        host=host
        )
    
    _cur = _connection.cursor()

    def register_new_user(self, user_data) -> None:
        self._cur.execute('''
    INSERT INTO main.users(
	username, full_name, room, is_seller)
	VALUES ('{username}', '{full_name}', {room}, {is_seller});'''.format(username=user_data['username'], 
                                                                 full_name=user_data['full_name'], 
                                                                 room=user_data['room'], 
                                                                 is_seller=user_data['is_seller']))
        self._connection.commit()
    def check_registration(self, username) -> bool:
        self._cur.execute('''
        SELECT username, full_name, room, is_seller
        FROM main.users
        WHERE username='{username}';
    '''.format(username=username))
        result = self._cur.fetchone()
        if result:
            return True
        else:
            return False
    
    def get_user_shop(self, username: int = None) -> int:
        self._cur.execute('''
        SELECT admin_id, moderators_ids, name, description, is_active, shop_id, shop_photo
        FROM main.shops
        WHERE admin_id='{username}';
        '''.format(username=username))
        result = self._cur.fetchone()

        return result[-2]
        
    def check_main_admin(self, user_id: str | None = None) -> bool:
        return user_id in ['5468245021', '408789367']
    
    def get_user_info(self, username: str| None = None) -> tuple:
        self._cur.execute('''
        SELECT username, full_name, room, is_seller, orders_count
        FROM main.users
        WHERE username='{username}';
    '''.format(username=username))
        result = self._cur.fetchone()
        return result
    
    def get_current_shop_info(self, current_shop: int  = 1) -> tuple:
        self._cur.execute('''
        SELECT admin_id, name, description, is_active, shop_id, shop_photo
	    FROM main.shops
        WHERE shop_id={current_shop};
        '''.format(current_shop=current_shop))

        result = self._cur.fetchone()
        return result
    
    def get_count_of_shops(self) -> int:
        self._cur.execute('''
        SELECT admin_id, moderators_ids, name, description, is_active, shop_id
	    FROM main.shops;        
    ''')
        result = self._cur.fetchall()
        return len(result)
    
    def get_products_of_shop(self, shop_id: int = None) -> list:
        self._cur.execute('''
        SELECT shop_id, name, description, price, category, product_id
	    FROM main.goods_table
        WHERE shop_id={shop_id};
        '''.format(shop_id=shop_id))
        result = self._cur.fetchall()
        return result
    
    def get_current_product_info(self, product_id: int = None) -> tuple:
        self._cur.execute('''
        SELECT shop_id, name, description, price, category, product_id
	    FROM main.goods_table
        WHERE product_id={product_id};
        '''.format(product_id=product_id))

        result = self._cur.fetchone()
        return result
    
    def get_shop_statictics(self, shop_id: int = None) -> list:
        self._cur.execute('''
        SELECT shop_id, order_id, buyer_id, products_ids, room, totalsum, status
        FROM main.orders
        WHERE shop_id={shop_id};
        '''.format(shop_id=shop_id))
        result = self._cur.fetchall()
        return result

    def change_shop_name(self, shop_id: int = None, new_name: str = None) -> None:
        self._cur.execute('''
        UPDATE main.shops
        SET name='{new_name}'
        WHERE shop_id={shop_id};
        '''.format(new_name=new_name, shop_id=shop_id))
        self._connection.commit()

    def change_shop_description(self, shop_id: int = None, new_description: str = None) -> None:
        self._cur.execute('''
        UPDATE main.shops
        SET description='{new_description}'
        WHERE shop_id={shop_id};
        '''.format(new_description=new_description, shop_id=shop_id))
        self._connection.commit()

    def change_shop_photo(self, shop_id: int = None, shop_photo: str = None) -> None:
        self._cur.execute('''
        UPDATE main.shops
        SET shop_photo='{shop_photo}'
        WHERE shop_id={shop_id};
        '''.format(shop_photo=shop_photo, shop_id=shop_id))
        self._connection.commit()

    def change_shop_status(self, shop_id: int = None, status: str = None):
        self._cur.execute('''
        UPDATE main.shops
        SET is_active='{status}'
        WHERE shop_id={shop_id};
        '''.format(status=status, shop_id=shop_id))
        self._connection.commit()

    def change_product_info(self, product_id: int = None, name: str = None, description: str = None, price: int = None):
        self._cur.execute('''
        UPDATE main.goods_table
	    SET name='{name}', description='{description}', price={price}
	    WHERE product_id={product_id};
        '''.format(name=name, description=description, price=price, product_id=product_id))
        self._connection.commit()

    def delete_product(self, product_id: int = None):
        self._cur.execute('''
        DELETE FROM main.goods_table
	    WHERE product_id={product_id};
        '''.format(product_id=product_id))
        self._connection.commit()