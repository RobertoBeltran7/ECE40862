import esp32
import random
import os
import ubinascii
import machine
import hmac, hashlib
import ujson
import uhashlib
import struct
import uos
from ucryptolib import aes

class CryptAes:
    """Uses AES encryption to encrypt Payload/Data before sending using MQTT protocol
    The AES algo uses Cipher Block Chaining (CBC)
    AES encryption correctly requires three things to produce ciphertext:
    a message: Payload/Data which is to be encrypted,
    a key: Piece of information (a parameter) that determines the functional output of a
        cryptographic algorithm. For encryption algorithms, a key specifies transformation
        of plaintext into ciphertext, and vice versa for decryption algorithms.
    initialization vector (IV): Piece of data sent along with the key that modifies the end
        ciphertext result. As the name suggests, it initializes the state of the encryption
        algorithm before the data enters. This protects against attacks like pattern analysis.
        This needs to be DIFFERENT for every message.
        
    Uses sessionID (received from Spinner #2) and Encrypted Data to generate HMAC for 
    authentication of the sending device (Spinner #1)
    SessionID is generated by Spinner #2 by posting to the MQTT topic, SessionID every 1 sec.
    
    HMAC (hash-based message authentication code): Type of message authentication code (MAC)
    involving a cryptographic HASH function and a secret cryptographic key. It may be used to
    simultaneously verify both the data integrity and the authentication of a message.
    
    
    """
    #-----------------------------------------------COMMON-----------------------------------------------------------#   

    def __init__(self,sessionID):
        """
        This class initializes all keys and ids
        nodeid     : unique id to identify device or board
        iv         : pseudorandom initialization vector, this needs to be DIFFERENT for every message.
        staticiv   : static initialization vector to obfuscate the randomized
                     initialization vector sent with each message, NOT used for any data
        ivkey      : unique key to encrypt the initialization vector
        datakey    : unique key to encypt the Payload/Data
        passphrase : key to generate the HMAC code for authentication
        
        sessionID  : unique value to identify the current communication session, generated only by Spinner #2
        
        ***********************NOTE******************************
        AES is a block cipher with a block size of 128 bits; that's why it encrypts 16 bytes at a time.        
        The block size of CBC mode of encryption is 16, make sure that any data going into AES
        Encryption is of size 16 bytes.
        """
        self.nodeid = b"2555555555555555"
        self.iv = uos.urandom(16)
        self.staticiv = b"abcdef2345678901"
        self.ivkey = b"2345678901abcdef"
        self.datakey = b"youCantSeeMeever"
        self.passphrase = b"0000000000000001"
        self.sessionID = sessionID
        self.encrypted_iv = None
        self.encrypted_nodeid = None
        self.encrypted_data = None

    #------------------------------------SPINNER #1 Needs to Use These Functions--------------------------------------#   


    def encrypt(self, sensor_data):
        """Encrypt each of the current initialization vector (iv), the nodeid, and the sensor_data 
        using (staticiv, ivkey) for iv and (iv, datakey) for nodeid and sensor_data
        :param sensor_data  : Acceleration X, Acceleration Y, Acceleration Z, and Temperature
        """
        encode = aes(self.ivkey,2,self.staticiv)
        self.encrypted_iv = encode.encrypt(self.iv)
        encode = aes(self.datakey,2,self.iv)
        self.encrypted_nodeid = encode.encrypt(self.nodeid)
        ax = sensor_data["ax"]
        ay = sensor_data["ay"]
        az = sensor_data["az"]
        temp = sensor_data["temp"]
        sensorData = b'{0:08.4f}{1:08.4f}{2:08.4f}{3:08.4f}'.format(ax, ay, az, temp)
        encode = aes(self.datakey, 2, self.iv)
        self.encrypted_data = encode.encrypt(sensorData)        
    
    def sign_hmac(self, sessionID):
        """Generate HMAC by using passphrase, and combination of encrypted iv, encrypted nodeid, 
        encrypted data, received sessionID.
        :param sessionID: unique value to identify the current communication session
        :return         : generated HMAC
        """
        fullmessage = self.encrypted_iv + self.encrypted_nodeid + self.encrypted_data + sessionID
        hmac_sign = hmac.new(self.passphrase, msg=fullmessage, digestmod=hashlib.sha224).hexdigest()
        return hmac_sign
        
    def send_mqtt(self, hmac_signed):
        """Prepare the message for MQTT transfer using all of encrypted iv, encrypted nodeid, 
        encrypted data, HMAC. Create the message in JSON format.
        :param hmac_signed  : generated HMAC
        :return             : MQTT message to publish to Spinner #2 on Topic "Sensor_Data"
        """        
        publish_msg = {
            "encrypted_iv": ubinascii.hexlify(self.encrypted_iv),
            "encrypted_nodeid": ubinascii.hexlify(self.encrypted_nodeid),
            "encrypted_data": ubinascii.hexlify(self.encrypted_data),
            "hmac": hmac_signed
        }
        return ujson.dumps(publish_msg)
        
    #------------------------------------SPINNER #2 Needs to Use These Functions--------------------------------------#   
    
    
    def verify_hmac(self, payload):
        """Authenticates the received MQTT message. 
        Generate HMAC using passphrase, sessionID, RECEIVED encrypted iv, encrypted nodeid, encrypted data 
        and compare with received hmac inside payload to authenticate.
        :param payload  : received MQTT message from Spinner #1. This includes all encrypted data, nodeid, iv, and HMAC
        :return message : MQTT message to publish to Spinner #1 on Topic "Acknowledge", can be "Failed Authentication" 
                          if verification is unsuccessful
        """
        decrypted_payload = ujson.loads(payload)
        decrypted_iv = ubinascii.unhexlify(decrypted_payload['encrypted_iv'])
        decrypted_nodeid = ubinascii.unhexlify(decrypted_payload['encrypted_nodeid'])
        decrypted_data = ubinascii.unhexlify(decrypted_payload['encrypted_data'])
        decrypted_hmac = decrypted_payload['hmac']
        hmac_msg = decrypted_iv+decrypted_nodeid+decrypted_data+self.sessionID
        
        gen_hmac= hmac.new(self.passphrase,msg=hmac_msg,digestmod=hashlib.sha224).hexdigest()
        if (decrypted_hmac == gen_hmac):
            return b'HMAC Authenticated'
        else:
            return b'Failed Authentication'
            
    def decrypt(self, payload):
        """Decrypts the each encrypted item of the payload.
        Initialize decryption cipher for each item and and use cipher to decrypt payload items.
        :param payload  : received MQTT message from Spinner #1. This includes all encrypted data, nodeid, iv, and HMAC
        :return         : MQTT message to publish to Spinner #1 on Topic "Acknowledge", can be "Successful Decryption"
        """
        decrypted_payload = ujson.loads(payload)
        decrypted_iv = ubinascii.unhexlify(decrypted_payload['encrypted_iv'])
        decrypted_nodeid = ubinascii.unhexlify(decrypted_payload['encrypted_nodeid'])
        decrypted_data = ubinascii.unhexlify(decrypted_payload['encrypted_data'])
        decrypted_hmac = decrypted_payload['hmac']
        
        decryption_cipher = aes(self.ivkey,2,self.staticiv)
        decrypt_iv= decryption_cipher.decrypt(decrypted_iv)

        decryption_data = aes(self.datakey,2,decrypt_iv)
        decrypt_data = decryption_data.decrypt(decrypted_data)

        sensor_data={}
        sensor_data['a_x']=float(decrypt_data[0:8])
        sensor_data['a_y']=float(decrypt_data[8:16])
        sensor_data['a_z']=float(decrypt_data[16:24])
        sensor_data['temp']=float(decrypt_data[24:32])

        return (0,sensor_data)
