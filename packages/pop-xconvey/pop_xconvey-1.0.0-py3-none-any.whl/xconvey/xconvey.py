import time
import platform
import paho.mqtt.client as mqtt

machine = platform.machine().lower()
if machine == "aarch64":
    product_file_path = "/etc/product"
else:
    product_file_path = "product"

class SensorBase:
    def __init__(self):
        """
        Initialize the data class to store and retrieve sensor data.
        """
        self.__value = None

    def setVal(self, data):
        """
        Save sensor data in this class.
        """
        self.__value = data

    def read(self):
        """
        Read stored data. A timeout error occurs if data does not change for 3 seconds after calling the read function.
        """
        now_time = time.time()
        while self.__value == None:
            if time.time() - now_time > 3:
                raise TimeoutError("Please check connection")
        return self.__value
    
class BlockBase:
    BLOCK = ""
    def __init__(self, device=None):
        """
        Initialization process before each block control. Connect to MQTT server and register callback function.

        :param device: Initialization process before each block control. Connect to MQTT server and register callback function.
        """
        if device == None:
            try:
                with open(product_file_path) as file:
                    self.BROKER_DOMAIN = None
                    self.DEV_NUM = None
                    self.DEV_NAME = None
                    self.INSITUTION_NAME = None
                    for line in file:
                        line = line.strip()
                        if line.startswith('BROKER_DOMAIN='):
                            self.BROKER_DOMAIN = line.split('=')[1].strip()
                        if line.startswith('DEV_NUM='):
                            self.DEV_NUM = line.split('=')[1].strip()
                        if line.startswith('DEVICE_NAME='):
                            self.DEV_NAME = line.split('=')[1].strip()
                        if line.startswith('INSITUTION_NAME='):
                            self.INSITUTION_NAME = line.split('=')[1].strip()
                    if self.BROKER_DOMAIN is None:
                        raise "[Error] There is no product file. Please make sure the device has product info"
                self.TOPIC_HEADER = self.DEV_NAME+"/"+self.INSITUTION_NAME+self.DEV_NUM+"/"+self.BLOCK
            except FileNotFoundError:
                raise FileNotFoundError("Can't detect hbe device. Please set device argument.")
        self.value = None
        self._client = mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.connect(self.BROKER_DOMAIN)
        self._client.loop_start()

    def __del__(self):
        """
        MQTT client connection terminated when class is deleted.
        """
        self._client.disconnect()

    def _on_connect(self, client, userdata, flags, rc):
        """
        Automatically subscribe to topics about specified blocks when connecting to the server.
        """
        if rc == 0:
            self._client.subscribe(self.topic+"/#")
    
    def _on_message(self, client, userdata, message):
        """
        Base function for convert message
        """
        raise NotImplementedError

    @property
    def topic(self):
        """
        Output block topics specified in this class
        """
        return self.TOPIC_HEADER
    
class Safety(BlockBase):
    BLOCK="safety"

    class SWStart(SensorBase):
        pass

    class SWStop(SensorBase):
        pass

    def __init__(self):
        """
        After performing the BlockBase initialization process, create a sensor instance for using SwitchStart and SwitchStop.
        """
        super().__init__()
        self.__sw_start = self.SWStart()
        self.__sw_stop = self.SWStop()

    def _on_message(self, client, userdata, message):
        """
        After receiving messages from the Safety block topic, store them in the corresponding sensor instance.
        """
        payload = message.payload.decode("utf-8")
        if message.topic.find("sw_start") != -1:
            if payload == "active":
                self.__sw_start.setVal(True)
            elif payload == "deactive":
                self.__sw_start.setVal(False)
        elif message.topic.find("sw_stop") != -1:
            if payload == "stop":
                self.__sw_stop.setVal(True)
                self.__sw_start.setVal(False)
            elif payload == "running":
                self.__sw_stop.setVal(False)

    def indicator(self, color):
        """
        Status light color control

        :param color: Enter the desired value from the four values ​​presented below: 'red', 'yellow', 'green', 'off'
        """
        if color not in ["red", "yellow", "green", "off"]:
            raise ValueError("Wrong value.")
        self._client.publish(self.topic+"/indicator", color, 0) 

    @property
    def sw_start(self):
        """
        Check if the Start button is pressed
        """
        return self.__sw_start.read()
    
    @property
    def sw_stop(self):
        """
        Check if the Stop button is pressed
        """
        return self.__sw_stop.read()

class Transfer(BlockBase):
    BLOCK="transfer"

    class Encoder(SensorBase):
        pass

    def __init__(self):
        """
        After performing the BlockBase initialization process, create a sensor instance for using Encoder. 
        """
        super().__init__()
        self.__encoder = self.Encoder()

    def _on_message(self, client, userdata, message):
        """
        After receiving messages from the Transfer block topic, store them in the corresponding sensor instance.
        """
        payload = message.payload.decode("utf-8")
        if message.topic.find('encoder') != -1:
            self.__encoder.setVal(int(payload))

    def run(self, step=1):
        """ 
        Active the conveyor
        """
        self._client.publish(self.topic+"/motor/step", str(step), 0)
    
    def stop(self):
        """ 
        Stop the conveyor
        """
        self._client.publish(self.topic+"/motor/step", "0", 0)
        time.sleep(0.5)

    @property
    def encoder(self):
        """
        Read encoder value.
        """
        return self.__encoder.read()

class BlockServoBase(BlockBase):
    class Servo(SensorBase):
        pass

    class Photo(SensorBase):
        pass
    
    def __init__(self):
        """
        After performing the BlockBase initialization process, create a sensor instance for using Servo, Photo. 
        """
        super().__init__()
        self._servo = self.Servo()
        self._photo = self.Photo()

    @property
    def servo(self):
        """
        Read servo status value.
        """
        return self._servo.read()

    @property
    def photo(self):
        """
        Read photo sensor value.
        """
        return self._photo.read()    

class Feeding(BlockServoBase):
    BLOCK = "feeding" 
    
    def _on_message(self, client, userdata, message):
        """
        After receiving messages from the Feeding block topic, store them in the corresponding sensor instance.
        """
        payload = message.payload.decode("utf-8")
        if message.topic.find("photo") != -1:
            if payload == "exist":
                self._photo.setVal(True)
            elif payload == "non-exist":
                self._photo.setVal(False) 
        elif message.topic.find("servo") != -1 and message.topic.find("state") != -1:
            if payload == "load" or payload == "supply":
                self._servo.setVal(payload)

    def load(self):
        """
        Performing an object loading operation on the feeding servo motor
        """
        self._client.publish(self.topic+"/servo/set", "load", 0)
    
    def supply(self):
        """
        Performs an object supply operation to the feeding servo motor
        """
        self._client.publish(self.topic+"/servo/set", "supply", 0)

    def toggle(self):
        """
        Performs an action opposite to the current state of the servo on the feeding servo motor
        """
        if self._servo.read() == "load":
            self.supply()
        elif self._servo.read() == "supply":
            self.load()
    
class Processing(BlockServoBase):
    BLOCK = "processing"

    def _on_message(self, client, userdata, message):
        """
        After receiving messages from the Safety block topic, store them in the corresponding sensor instance.
        """
        payload = message.payload.decode("utf-8")
        if message.topic.find("photo") != -1:
            if payload == "exist":
                self._photo.setVal(True)
            elif payload == "non-exist":
                self._photo.setVal(False) 
        elif message.topic.find("servo") != -1 and message.topic.find("state") != -1:
            if payload == "up" or payload == "down":
                self._servo.setVal(payload)

    def up(self):
        """
        Performing a rising motion on the processing servo motor
        """
        self._client.publish(self.topic+"/servo/set", "up", 0)

    def down(self):
        """
        Performing a falling motion on the processing servo motor
        """
        self._client.publish(self.topic+"/servo/set", "down", 0)
    
    def toggle(self):
        """
        Performs an action opposite to the current state of the servo on the processing servo motor.
        """
        if self._servo.read() == "up":
            self.down()
        elif self._servo.read() == "down":
            self.up()

class Sorting(BlockServoBase):
    BLOCK = "sorting"

    class Inductive(SensorBase):
        pass

    class HitCount(SensorBase):
        pass

    class NormalCount(SensorBase):
        pass

    def __init__(self):
        """
        After performing the BlockBase initialization process, create a sensor instance for using Inductive, hit basket count, normal basket count. 
        """ 
        super().__init__()
        self.__inductive = self.Inductive()
        self.__hit_count = self.HitCount()
        self.__normal_count = self.NormalCount()
        self.__hit_count.setVal(0)
        self.__normal_count.setVal(0)

    def _on_message(self, client, userdata, message):
        """
        After receiving messages from the Sorting block topic, store them in the corresponding sensor instance.
        """
        payload = message.payload.decode("utf-8")
        if message.topic.find("photo") != -1:
            if payload == "exist":
                self._photo.setVal(True)
            elif payload == "non-exist":
                self._photo.setVal(False) 
        elif message.topic.find("servo") != -1 and message.topic.find("state") != -1:
            if payload == "hit" or payload == "normal":
                self._servo.setVal(payload)
        elif message.topic.find("inductive") != -1:
            if payload == "metal":
                self.__inductive.setVal(True)
            elif payload == "non-metal":
                self.__inductive.setVal(False)
        elif message.topic.find("hit_count") != -1:
            self.__hit_count.setVal(self.__hit_count.read()+1)
        elif message.topic.find("normal_count") != -1:
            self.__normal_count.setVal(self.__normal_count.read()+1)

    @property
    def inductive(self):
        """
        Read inductive sensor value.
        """
        return self.__inductive.read()
    
    @property
    def hit_count(self):
        """
        Read the number of objects in the basket after the direction of the object has changed.
        """
        return self.__hit_count.read()
    
    @property
    def normal_count(self):
        """
        Read the number of objects that entered the basket without changing direction.
        """
        return self.__normal_count.read()

    def hit(self):
        """
        Performing an action to change the direction of an object on the sorting servo motor
        """
        self._client.publish(self.topic+"/servo/set", "hit", 0)

    def normal(self):
        """
        Performs an action to return the servo motor which on the sorting block to its normal state.
        """
        self._client.publish(self.topic+"/servo/set", "normal", 0)
    
    def toggle(self):
        """
        Performs the opposite action from the current state on the sorting servo motor.
        """
        if self._servo.read() == "hit":
            self.normal()
        elif self._servo.read() == "normal":
            self.hit()