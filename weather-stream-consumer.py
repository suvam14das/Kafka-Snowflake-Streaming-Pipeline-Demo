from kafka import KafkaConsumer
import snowflake.connector
import json

consumer = KafkaConsumer(
    'weather-data',
    bootstrap_servers=['localhost:9092','localhost:9093','localhost:9094'],
    group_id='weather-consumer-group',
    auto_offset_reset='earliest',
    enable_auto_commit=False,  # critical
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

conn = snowflake.connector.connect(
    user='<USERNAME>',
    password='<PASSWORD>',
    account='<ACCOUNT_IDENTIFIER>'
)

cursor = conn.cursor()

cursor.execute(""" USE DATABASE WEATHER """)

for message in consumer:
    data = message.value
    print("Message conusmed : ",data)
    
    # simple insert (better: stage + merge)
    cursor.execute("""
        INSERT INTO WEATHER_TABLE (DATA)
        SELECT PARSE_JSON(%s)
    """, (json.dumps(data),))
    
    conn.commit()
    
    # commit Kafka offset ONLY after Snowflake success
    consumer.commit()