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
    # 只在battery值合理时打印
    if battery and 0 <= battery <= 100:
        print(f"Temperature: {temperature}°C")
        print(f"Humidity: {humidity}%") 
        print(f"Battery: {battery}%")
        
    return {
        'currentTime': current_time,
        'temperature': temperature,
        'humidity': humidity,
        'battery': battery
    }

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
        client = None
        try:
            async with BleakClient(mac_address) as client:
                print(f"Connected to {mac_address}")
                
                while True:
                    try:
                        # 读取温湿度数据
                        data = await client.read_gatt_char(TEMP_HUMID_CHAR)
                        temperature = struct.unpack('<H', data[0:2])[0] / 100
                        humidity = data[2]
                        
                        # 读取电池电量
                        try:
                            battery_data = await client.read_gatt_char(BATTERY_CHAR)
                            battery = battery_data[0]
                            if 0 <= battery <= 100:
                                print(f"Battery level: {battery}%")
                        except Exception as e:
                            print(f"Error reading battery: {e}")
                            battery = None
                        
                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # 数据验证
                        if not (0 <= humidity <= 100 and -40 <= temperature <= 60):
                            print(f"Invalid readings - Temperature: {temperature}°C, Humidity: {humidity}%")
                            continue
                        
                        # 显示读取到的数据
                        print(f"Temperature: {temperature:.2f}°C")
                        print(f"Humidity: {humidity}%")
                        print("-" * 40)
                        
                        # 保存数据
                        data = {
                            'currentTime': current_time,
                            'temperature': temperature,
                            'humidity': humidity
                        }
                        save_to_database(data)
                        
                        # 等待下一次读取
                        print(f"Waiting {interval} seconds before next reading...")
                        await asyncio.sleep(interval)
                        
                    except (BleakError, asyncio.TimeoutError) as e:
                        print(f"Error during reading: {e}")
                        break
                        
        except Exception as e:
            print(f"Connection error: {e}")
            print("Attempting to reconnect in 5 seconds...")
            await asyncio.sleep(5)
            
        finally:
            if client and client.is_connected:
                await client.disconnect()

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
