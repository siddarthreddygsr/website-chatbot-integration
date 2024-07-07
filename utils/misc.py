import hashlib

def generate_hash(data):
    hash_object = hashlib.new('md5')
    hash_object.update(data.encode('utf-8'))
    return hash_object.hexdigest()
