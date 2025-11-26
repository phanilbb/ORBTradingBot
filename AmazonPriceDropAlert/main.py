from AmazonPriceDropAlert import lambda_function
from AmazonPriceDropAlert import communication

if __name__ == '__main__':
    event = [
        {
            "url": "https://www.amazon.in/Samsung-inches-Crystal-Vivid-UA75DUE77AKXXL/dp/B0CX5FY89F",
            "price": 70000,
            "product": "Samsung TV 75 inches"
        },
        {
            "url": "https://www.amazon.in/Xiaomi-inches-Ultra-Google-L65M8-A2IN/dp/B0CH31ZLNQ",
            "price": 40000,
            "product": "Xiaomi TV 65 inches"
        },
        {
            "url": "https://www.amazon.in/Haier-Inverter-Refrigerator-HES-690IM-P-Convertible/dp/B0BZ135HFX",
            "price": 50000,
            "product": "Haier Fridge"
        },
        {
            "url": "https://www.amazon.in/ILIFE-T20s-Self-Emptying-Navigation-Simultaneous/dp/B0BTTDLW7L",
            "price": 20000,
            "product": "ILIFE Robo Vaccum Cleaner"
        },
        {
            "url": "https://www.amazon.in/Panasonic-Condenser-Convertible-CS-CU-NU18ZKY5W/dp/B0CSCWVKGK",
            "price": 35000,
            "product": "Panasonic AC"
        },
        {
            "url": "https://www.amazon.in/Bosch-Settings-Dishwasher-SMS66GI01I-Silver/dp/B07JW58P2C",
            "price": 33000,
            "product": "Bosch Dishwasher"
        }
    ]
    comm = communication.Communication()
    comm.send_telegram_msg("hello")
    #lambda_function.lambda_handler(event, None)
