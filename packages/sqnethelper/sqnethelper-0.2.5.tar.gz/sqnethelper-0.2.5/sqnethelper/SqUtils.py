
import struct
import json
import gzip
import io

class SqUtils:

    # with open(output_file, 'w', encoding='utf-8') as f:
    #     json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def read_varbin(reader):
        try:
            length_bytes = reader.read(2)
            if len(length_bytes) < 2:
                print(f"Warning: Expected 2 bytes for length, got {len(length_bytes)}")
                return None
            length = struct.unpack('>H', length_bytes)[0]
            data = reader.read(length)
            if len(data) < length:
                print(f"Warning: Expected {length} bytes of data, got {len(data)}")
                return None
            try:
                return data.decode('utf-8')
            except UnicodeDecodeError:
                return data.hex()
        except Exception as e:
            print(f"Error in read_varbin: {e}")
            return None
    
    @staticmethod
    def write_varbin(writer, data):
        if isinstance(data, str):
            encoded = data.encode('utf-8')
        elif isinstance(data, bytes):
            encoded = data
        else:
            raise ValueError("Data must be str or bytes")
        writer.write(struct.pack('>H', len(encoded)))
        writer.write(encoded)

    @staticmethod
    def bpf_to_json(bpf_file, json_file):
        with open(bpf_file, 'rb') as f:
            data = f.read()
        
        reader = io.BytesIO(data)
        
        try:
            # Read message type
            message_type = reader.read(1)
            if not message_type:
                raise ValueError("Could not read message type")
            message_type = message_type[0]
            if message_type != 3:  # MessageTypeProfileContent
                raise ValueError(f"Invalid message type: {message_type}")
            
            # Read version
            version_bytes = reader.read(1)
            if not version_bytes:
                raise ValueError("Could not read version")
            version = version_bytes[0]
            
            # Read gzipped content
            gzip_reader = gzip.GzipFile(fileobj=reader)
            content = {}
            
            content['name'] = SqUtils.read_varbin(gzip_reader)
            if content['name'] is None:
                raise ValueError("Could not read name")
            
            type_bytes = gzip_reader.read(4)
            if len(type_bytes) < 4:
                raise ValueError(f"Expected 4 bytes for type, got {len(type_bytes)}")
            content['type'] = struct.unpack('>i', type_bytes)[0]
            
            content['config'] = SqUtils.read_varbin(gzip_reader)
            if content['config'] is None:
                raise ValueError("Could not read config")
            
            if content['type'] != 0:  # Not ProfileTypeLocal
                content['remotePath'] = SqUtils.read_varbin(gzip_reader)
                if content['remotePath'] is None:
                    raise ValueError("Could not read remotePath")
            
            if content['type'] == 2 or (version == 0 and content['type'] != 0):  # ProfileTypeRemote
                auto_update_bytes = gzip_reader.read(1)
                if not auto_update_bytes:
                    raise ValueError("Could not read autoUpdate")
                content['autoUpdate'] = struct.unpack('>?', auto_update_bytes)[0]
                
                if version >= 1:
                    interval_bytes = gzip_reader.read(4)
                    if len(interval_bytes) < 4:
                        raise ValueError(f"Expected 4 bytes for autoUpdateInterval, got {len(interval_bytes)}")
                    content['autoUpdateInterval'] = struct.unpack('>i', interval_bytes)[0]
                
                last_updated_bytes = gzip_reader.read(8)
                if len(last_updated_bytes) < 8:
                    raise ValueError(f"Expected 8 bytes for lastUpdated, got {len(last_updated_bytes)}")
                content['lastUpdated'] = struct.unpack('>q', last_updated_bytes)[0]
            
            with open(json_file, 'w') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            
            print("Successfully converted BPF to JSON")
        
        except Exception as e:
            print(f"Error in bpf_to_json: {e}")
            print(f"Current position in file: {reader.tell()}")
            raise

    @staticmethod
    def json_to_bpf(json_file, bpf_file):
        with open(json_file, 'r') as f:
            content = json.load(f)
        
        buffer = io.BytesIO()
        buffer.write(struct.pack('B', 3))  # MessageTypeProfileContent
        buffer.write(struct.pack('B', 1))  # Version
        
        gzip_writer = gzip.GzipFile(fileobj=buffer, mode='wb')
        
        SqUtils.write_varbin(gzip_writer, content['name'])
        gzip_writer.write(struct.pack('>i', content['type']))
        SqUtils.write_varbin(gzip_writer, content['config'])
        
        if content['type'] != 0:  # Not ProfileTypeLocal
            SqUtils.write_varbin(gzip_writer, content['remotePath'])
        
        if content['type'] == 2:  # ProfileTypeRemote
            gzip_writer.write(struct.pack('>?', content['autoUpdate']))
            gzip_writer.write(struct.pack('>i', content['autoUpdateInterval']))
            gzip_writer.write(struct.pack('>q', content['lastUpdated']))
        
        gzip_writer.close()
        
        with open(bpf_file, 'wb') as f:
            f.write(buffer.getvalue())
                

             
    

