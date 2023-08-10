from typing import *
from pydantic import BaseModel, Field
from aiokafka.helpers import create_ssl_context
from fastkafka import FastKafka


class StoreProduct(BaseModel):
    product_name: str = Field(..., description="Name of the product.")
    currency: str = Field(..., description="The currency.")
    price: float = Field(..., description="Price of the product.")


kafka_brokers = {
    "localhost": {
        "url": "localhost",
        "description": "local development kafka broker",
        "port": 9092,
    },
    "staging": {
        "url": "staging.airt.ai",
        "description": "staging kafka broker",
        "port": 9092,
        "protocol": "kafka-secure",
        "security": {"type": "scramSha256"},
    },
    "production": {
        "url": "prod.airt.ai",
        "description": "production kafka broker",
        "port": 9092,
        "protocol": "kafka-secure",
        "security": {"type": "scramSha256"},
    }
}

store_product_app_description = "A FastKafka application using localhost broker for testing, staging.airt.ai for staging and prod.airt.ai for production, using default port numbers. It should consume from 'store_product' topic an JSON encoded object with the following three attributes: product_name, currency and price. The format of the currency will be three letter string, e.g. 'EUR'. For each consumed message, check if the currency attribute is set to 'HRK'. If it is then change the currency to 'EUR' and divide the price by 7.5, if the currency is not set to 'HRK' don't change the original message. Finally, publish the consumed message to 'change_currency' topic. Use SASL_SSL with SCRAM-SHA-256 for authentication."

store_product_app = FastKafka(
    kafka_brokers=kafka_brokers, 
    description=store_product_app_description, 
    version="0.0.1", 
    title='Product currency converter',
    security_protocol = "SASL_SSL",
    sasl_mechanism= "SCRAM-SHA-256",
    sasl_plain_username= "<username>",
    sasl_plain_password=  "<password>", # nosec B106
    ssl_context= create_ssl_context(),
)


store_product_description = "For each consumed message, check if the currency attribute is set to 'HRK'. If it is then change the currency to 'EUR' and divide the price by 7.5, if the currency is not set to 'HRK' don't change the original message. Finally, publish the consumed message to 'change_currency' topic."

@store_product_app.consumes(topic="store_product", description=store_product_description)
async def on_store_product(msg: StoreProduct):
    if msg.currency == "HRK":
       msg = StoreProduct(product_name = msg.product_name, currency="EUR", price = msg.price / 7.5)
    await to_change_currency(msg)


@store_product_app.produces(topic="change_currency")
async def to_change_currency(msg: StoreProduct) -> StoreProduct:
    return msg
