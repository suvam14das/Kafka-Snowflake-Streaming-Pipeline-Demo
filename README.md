# Kafka Weather Data Pipeline

This project demonstrates a complete Data Engineering pipeline that polls weather data from an external API, produces it to a Kafka topic, and consumes it into a Snowflake Data Warehouse for real-time analysis and hourly aggregation.

## Architecture
1.  **Producer**: A Python script ([`weather-api-producer.py`](https://github.com/suvam14das/Kafka-Snowflake-Streaming-Pipeline-Demo/blob/main/weather-api-producer.py)) that polls the OpenWeatherMap API every 10 seconds.
2.  **Streaming Platform**: A 3-node Kafka cluster running locally via Docker Compose.
3.  **Consumer**: A Python script ([`weather-stream-consumer.py`](https://github.com/suvam14das/Kafka-Snowflake-Streaming-Pipeline-Demo/blob/main/weather-stream-consumer.py)) that reads from Kafka and performs an idempotent insert into Snowflake.
4.  **Data Warehouse**: Snowflake handles the storage, semi-structured data parsing, and hourly aggregations using Streams and Tasks.

## Prerequisites

-   **Python 3.11.8**
-   **Docker & Docker Desktop**: 
    1. Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/) for your operating system.
    2. Start the Docker Desktop. This will start the Docker Engine by default. The UI should say 'Engine running'. 
-   **OpenWeatherMap API Key**: Sign up at [openweathermap.org](https://openweathermap.org/) to get an API key.
-   **Snowflake Account**: Ensure you have a Snowflake account with sufficient privileges to create databases, tables, streams, and tasks.

## Setup Instructions

### 1. Infrastructure (Kafka Cluster)
1. **Start the cluster**: Spin up the 3-node Kafka cluster and Zookeeper. This setup ensures high availability for your stream.
   ```bash
   docker-compose up -d
   ```

2. **Create the Topic**: Once the containers are running, create the `weather-data` topic with a replication factor of 3 to match the broker count:
   ```bash
   docker exec -it kafka1 kafka-topics --create --topic weather-data --bootstrap-server kafka1:29092 --partitions 3 --replication-factor 3
   ```

### 2. Snowflake Environment Setup
Run the following SQL commands in your Snowflake worksheet to initialize the database table for consumer to push data in. the rest of the snowflake script is to create a medalian architecture streaming pipeline. Follow the rest of the pipeline setup code in [Weather-stream-notebook.ipynb](https://github.com/suvam14das/Kafka-Snowflake-Streaming-Pipeline-Demo/blob/main/Weather-stream-notebook.ipynb)

```sql
-- 1. Create Database
CREATE OR REPLACE DATABASE WEATHER;
USE DATABASE WEATHER;

-- 2. Raw Ingestion Table (Stores raw JSON from Kafka)
CREATE OR REPLACE TABLE WEATHER_TABLE (
    DATA VARIANT,
    INGESTED_AT TIMESTAMP DEFAULT SYSDATE()
);
```

### 3. Application Setup
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Producer**: Ensure your `API_KEY` is set correctly in `weather-api-producer.py`.
3.  **Consumer**: Update the `snowflake.connector` credentials in `weather-stream-consumer.py` if necessary.

## Running the Pipeline

1.  **Start the Producer**:
    ```bash
    python weather-api-producer.py
    ```
2.  **Start the Consumer** :
    ```bash
    python weather-stream-consumer.py
    ```
    Start multiple consumers by running the below code in seperate terminals. But at most 3 consumers can be actively consume from the 3 partitions in this topic.

The consumer ensures "At Least Once" delivery by only committing the Kafka offset after a successful Snowflake transaction.
