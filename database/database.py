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