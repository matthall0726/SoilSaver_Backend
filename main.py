import RPi.GPIO as GPIO
import time

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)

# Set up GPIO pin
gpio_pin = 17  # Change this to match the GPIO pin you've connected
GPIO.setup(gpio_pin, GPIO.OUT)

# Turn on the relay (energize) to activate the motor
GPIO.output(gpio_pin, GPIO.HIGH)
time.sleep(2)  # Run the motor for 2 seconds (adjust as needed)

# Turn off the relay (de-energize) to stop the motor
GPIO.output(gpio_pin, GPIO.LOW)

# Clean up GPIO settings
GPIO.cleanup()
