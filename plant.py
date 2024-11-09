import time
import RPi.GPIO as GPIO
import spidev

GPIO.setmode(GPIO.BCM)
water_pump_pin = 17
GPIO.setup(water_pump_pin, GPIO.OUT)
spi_bus = spidev.SpiDev()
spi_bus.open(0, 0)
spi_bus.max_speed_hz = 1000000

wet_value = 290
dry_value = 700

def read_adc(channel):
    try:
        adc_data = spi_bus.xfer2([1, (8 + channel) << 4, 0])
        adc_value = ((adc_data[1] & 3) << 8) + adc_data[2]
        return adc_value
    except Exception as error:
        print(f"Error reading ADC data: {error}")
        return None

def map_to_percentage(adc_value, min_adc, max_adc):
    if adc_value is None:
        return None
    moisture_percentage = (max_adc - adc_value) / (max_adc - min_adc) * 100
    return max(0, min(100, moisture_percentage))

def control_water_pump(moisture_percentage, moisture_threshold=40):
    if moisture_percentage is None:
        return
    if moisture_percentage < moisture_threshold:
        if GPIO.input(water_pump_pin) == GPIO.LOW:
            print("Moisture is low. Turning water pump ON.")
            GPIO.output(water_pump_pin, GPIO.HIGH)
    else:
        if GPIO.input(water_pump_pin) == GPIO.HIGH:
            print("Moisture is sufficient. Turning water pump OFF.")
            GPIO.output(water_pump_pin, GPIO.LOW)

try:
    while True:
        raw_adc_value = read_adc(0)

        if raw_adc_value is not None:
            print(f"Raw ADC value: {raw_adc_value}")
            moisture_percentage = map_to_percentage(raw_adc_value, wet_value, dry_value)
            print(f"Moisture level: {round(moisture_percentage, 2)}% ({raw_adc_value})\n")
            control_water_pump(moisture_percentage)

        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting program.")
    GPIO.cleanup()
