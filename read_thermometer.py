import asyncio
from datetime import datetime
import struct
import pymysql
from bleak import BleakScanner, BleakClient
import argparse
import time

# 小米温湿度计的特征值UUID
TEMP_HUMID_UUID = "ebe0ccc1-7a0a-4b0c-8a1a-6ff2997da3a6"
MAC_ADDRESS = "A4:C1:38:D5:9F:08"  # 你需要替换成你的设备MAC地址

async def connect_and_read(mac_address):
    try:
        async with BleakClient(mac_address) as client:
            print(f"Connected to {mac_address}")
            
            # 读取特征值
            data = await client.read_gatt_char(TEMP_HUMID_UUID)
            
            # 解析数据
            temperature = struct.unpack('H', data[0:2])[0] / 100
            humidity = struct.unpack('H', data[2:4])[0] / 100
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Temperature: {temperature}°C")
            print(f"Humidity: {humidity}%")
            
            return {
                'currentTime': current_time,
                'temperature': temperature,
                'humidity': humidity
            }
    except Exception as e:
        print(f"Error connecting to device: {e}")
        return None

def save_to_database(data):
    # 数据库连接配置
    db_config = {
        'host': 'localhost',
        'user': 'pofice',
        'password': 'your_password',
        'db': 'weather_data'
    }
    
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            sql = "INSERT INTO `temp_table` (`currentTime`, `temperature`, `humidity`) VALUES (%s, %s, %s)"
            cursor.execute(sql, (data['currentTime'], data['temperature'], data['humidity']))
        connection.commit()
        print("Data saved to database successfully!")
    except Exception as e:
        print(f"Error saving to database: {e}")
    finally:
        if connection:
            connection.close()

async def monitor_temperature(mac_address, interval=60):
    """持续监控温度，每隔interval秒读取一次数据"""
    print(f"Starting continuous monitoring. Reading every {interval} seconds...")
    
    while True:
        try:
            data = await connect_and_read(mac_address)
            if data:
                if data['humidity'] <= 100:  # 添加简单的数据验证
                    save_to_database(data)
                else:
                    print(f"Invalid humidity value: {data['humidity']}%, skipping...")
            
            # 等待指定的时间间隔
            await asyncio.sleep(interval)
            
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
            break
        except Exception as e:
            print(f"Error during monitoring: {e}")
            print("Retrying in 5 seconds...")
            await asyncio.sleep(5)

async def main():
    parser = argparse.ArgumentParser(description='Read Xiaomi Thermometer data and save to database')
    parser.add_argument('--mac', type=str, default=MAC_ADDRESS,
                      help='MAC address of the thermometer')
    parser.add_argument('--interval', type=int, default=6,
                      help='Interval between readings in seconds (default: 6)')
    args = parser.parse_args()

    print(f"Starting monitoring with device: {args.mac}")
    try:
        await monitor_temperature(args.mac, args.interval)
    except KeyboardInterrupt:
        print("\nProgram terminated by user")

if __name__ == '__main__':
    asyncio.run(main())
