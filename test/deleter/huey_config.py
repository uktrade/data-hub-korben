from huey import RedisHuey

huey_instance = RedisHuey(url='tcp://backend:6379')
