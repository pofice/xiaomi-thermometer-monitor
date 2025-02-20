import asyncio
from datetime import datetime
import struct
import pymysql
from bleak import BleakScanner, BleakClient
import argparse
import time

# Mi Thermometer services and characteristics
MI_SERVICE = "ebe0ccb0-7a0a-4b0c-8a1a-6ff2997da3a6"
TEMP_HUMID_CHAR = "ebe0ccc1-7a0a-4b0c-8a1a-6ff2997da3a6" 
BATTERY_CHAR = "ebe0ccc4-7a0a-4b0c-8a1a-6ff2997da3a6"

async def notification_handler(sender, data):
    """Handle incoming notifications"""
    temperature = struct.unpack('<H', data[0:2])[0] / 100
    humidity = data[2]
    battery = data[3] if len(data) >= 4 else None
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Temperature: {temperature}°C")
    print(f"Humidity: {humidity}%")
    if battery:
        print(f"Battery: {battery}%")
        
    return {
        'currentTime': current_time,
        'temperature': temperature,
        'humidity': humidity,
        'battery': battery
    }

async def connect_and_read(address):
    try:
        async with BleakClient(address) as client:
            print(f"Connected to {address}")
            
            # Enable notifications
            await client.start_notify(TEMP_HUMID_CHAR, notification_handler)
            
            # Wait for data
            await asyncio.sleep(5)
            
            # Read temperature and humidity directly
            data = await client.read_gatt_char(TEMP_HUMID_CHAR)
            battery = await client.read_gatt_char(BATTERY_CHAR)
            
            temperature = struct.unpack('<H', data[0:2])[0] / 100
            humidity = data[2]
            battery_level = battery[0]
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 显示电池信息但不保存到数据库
            print(f"Battery level: {battery_level}%")
            
            return {
                'currentTime': current_time, 
                'temperature': temperature,
                'humidity': humidity
            }
            
    except Exception as e:
        print(f"Connection error: {e}")
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
            # 移除battery字段
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
    parser.add_argument('--mac', type=str, required=True,
                      help='MAC address of the thermometer (required)')
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
