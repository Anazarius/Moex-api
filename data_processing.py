from datetime import date
import requests
import xml.etree.ElementTree as ET
from database import mycursor, mydb
import pandas as pd

def process_data():
    data_inserted_flag = True
    if data_inserted_flag:
        statuses_data = [
        (1, 'Неквалифицированный', 'Статус для новичков', 0),
        (2, 'Квалифицированный', 'Статус для опытных пользователей', 50),
        (3, 'Продвинутый', 'Статус для продвинутых', 100),
        (4, 'Эксперт', 'Статус для экспертов', 150),
        (5, 'Мультигигант', 'Статус для профессионалов', 200),
        ]

        insert_status_query = "INSERT INTO Statuses (id, name, description, reward) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE name = VALUES(name), description = VALUES(description), reward =VALUES(reward)"
        mycursor.executemany(insert_status_query, statuses_data)

        users_data = [
            (1, 'qwe', 'qwe', 'qwe', 1000, 1),
            (2, 'Петр', 'Петров', 'password456', 500, 2),
            (3, 'Мария', 'Сидорова', 'securepwd789', 1500, 3),
            (4, 'Анна', 'Кузнецова', 'mysecurepassword', 2000, 2),
            (5, 'Алексей', 'Смирнов', 'strongpwd321', 800, 1),
        ]

        insert_user_query = "INSERT INTO Users (id, name, last_name, password, balance, status_id) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE name = VALUES(name), password = VALUES(password), balance = VALUES(balance), status_id = VALUES(status_id)"
        mycursor.executemany(insert_user_query, users_data)

def process_data_dynamic():
        api_url = "http://iss.moex.com/iss/history/engines/stock/markets/shares/sessions/2023-12-20/boards/tqbr/securities?iss.meta=off&history.columns=SHORTNAME,SECID,TRADEDATE,VOLUME,NUMTRADES,LOW,HIGH,OPEN,CLOSE&start=143"

        try:
            response = requests.get(api_url)

            if response.status_code == 200:
                root = ET.fromstring(response.content)
                rows = root.find(".//data/rows")
                
                if rows is not None:
                    shares_data = []
                    data = []
                    for row in rows.findall("row"):
                        name = row.get("SHORTNAME")
                        tag = row.get("SECID")
                        tradedate = row.get("TRADEDATE")
                        
                        volume = int(row.get("VOLUME", 0)) if row.get("VOLUME", None) else 0
                        numtrades = int(row.get("NUMTRADES", 0)) if row.get("NUMTRADES", None) else 0
                        low = float(row.get("LOW", 0)) if row.get("LOW", None) else 0
                        high = float(row.get("HIGH", 0)) if row.get("HIGH", None) else 0
                        open = float(row.get("OPEN", 0)) if row.get("OPEN", None) else 0
                        close = float(row.get("CLOSE", 0)) if row.get("CLOSE", None) else 0
                        
                        shares_data.append((name, tag, 'common_shares'))
                        data.append((name, tag, tradedate, volume, numtrades, low, high, open, close))


                    insert_query_shares = "INSERT INTO Shares (name, tag, type) VALUES (%s, %s, %s)"
                    mycursor.executemany(insert_query_shares, shares_data)
                    insert_query_data = "REPLACE INTO Data (name, tag, tradedate, volume, numtrades, low, high, open, close) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    mycursor.executemany(insert_query_data, data)
                    
                    print(f"Добавлено {len(shares_data)} акций в таблицу Shares")
                    mydb.commit()
                else:
                    print("Не найдены данные в XML или ответ пустой")

        except requests.RequestException as e:
            print(f"Запрос завершился ошибкой: {e}")


        user_share_data = [
            (1, 1, 1, 5, date.today()),
            (2, 2, 2, 10, date.today()),
            (3, 3, 3, 15, date.today()),
            (4, 4, 4, 20, date.today()),
            (5, 5, 5, 25, date.today()),
        ]

        insert_user_share_query = "INSERT INTO User_share (id, user_id, share_id, count, data_purchase) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE id = VALUES(id), user_id = VALUES(user_id), share_id = VALUES(share_id), count = VALUES(count), data_purchase = VALUES(data_purchase)"
        mycursor.executemany(insert_user_share_query, user_share_data)

        favorites_data = [
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5),
        ]

        insert_favorites_query = "INSERT INTO Favorites (user_id, share_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE user_id = VALUES(user_id), share_id = VALUES(share_id)"
        mycursor.executemany(insert_favorites_query, favorites_data)

        mycursor.execute("SELECT id, tag, volume, numtrades, low, high, open, close FROM Data")
        data = mycursor.fetchall()

        max_values = {
            'average_price': 0,
            'price_range': 0,
            'count_numtrades': 0,
            'price_index': 0,
            'ratio_low_open': 0
        }

        for row in data:
            numtrades = row[3]
            low = row[4]
            high = row[5]
            open = row[6]
            close= row[7]

            average_price = ((((close+open)/2)-open)/open)*100  if open != 0 else 0
            price_range = ((high-low)/open)*100  if open != 0 else 0
            count_numtrades = numtrades  if open != 0 else 0
            price_index = ((close/open)-1)*100  if open != 0 else 0
            ratio_low_open = ((low/open)-1)*100 if open != 0 else 0

            max_values['average_price'] = max(max_values['average_price'], average_price)
            max_values['price_range'] = max(max_values['price_range'], price_range)
            max_values['count_numtrades'] = max(max_values['count_numtrades'], numtrades)
            max_values['price_index'] = max(max_values['price_index'], price_index)
            max_values['ratio_low_open'] = max(max_values['ratio_low_open'], ratio_low_open)


        additive = []

        for row in data:
            numtrades = row[3]
            low = row[4]
            high = row[5]
            open = row[6]
            close= row[7]

            average_price = ((((close + open) / 2) - open) / open) * 100  if open != 0 else 0
            price_range = ((high - low) / open) * 100  if open != 0 else 0
            price_index = ((close / open) - 1) * 100  if open != 0 else 0
            ratio_low_open = ((low/open) - 1) * 100  if open != 0 else 0

            normalized_average_price = (average_price / max_values['average_price']) * 0.5
            normalized_price_range = (price_range / max_values['price_range']) * 0.25
            normalized_count_numtrades = (numtrades / max_values['count_numtrades']) * 0.25
            normalized_price_index = (price_index / max_values['price_index']) * 1
            if max_values['ratio_low_open'] != 0:
                normalized_ratio_low_open = (ratio_low_open / max_values['ratio_low_open']) * 0.5
            else:
                normalized_ratio_low_open = 0
            
            additive_sum = (
                normalized_average_price +
                normalized_price_range +
                normalized_count_numtrades +
                normalized_price_index +
                normalized_ratio_low_open
            )
            additive.append(additive_sum)

        result_data = []
        for (id_value, tag_value, *_), additive_sum in zip(data, additive):
            result_data.append((id_value, tag_value, additive_sum))

        sorted_results = sorted(result_data, key=lambda x: x[2], reverse=True)
        mydb.commit()
        data_inserted_flag = False
        df = pd.DataFrame(sorted_results, columns=["ID", "Tag", "Additive"], index=range(1, len(sorted_results) + 1))
        df = df.drop(columns=["ID"])
        return df
    
if __name__ == "__main__":
    process_data()
    process_data_dynamic()