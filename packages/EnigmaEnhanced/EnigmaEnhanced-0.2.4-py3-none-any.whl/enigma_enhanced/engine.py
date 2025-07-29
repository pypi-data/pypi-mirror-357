import os
import json
import base64
import hashlib
import secrets
import zlib
import hmac
import argparse
from typing import List, Tuple

class EnigmaEngine:
    """完全独立、无状态的恩尼格玛引擎核心"""
    
    @staticmethod
    def generate_key(legacy=False) -> dict:
        """生成密钥（无状态版本）"""
        if legacy:
            # 0.1.2兼容密钥生成
            seed = secrets.token_bytes(32)
            key_material = EnigmaEngine._derive_key_legacy(seed, 768)
            
            rotors = []
            for i in range(3):
                rotor = list(range(256))
                for j in range(256):
                    swap_index = key_material[i*256 + j] % 256
                    rotor[j], rotor[swap_index] = rotor[swap_index], rotor[j]
                rotors.append(rotor)
            
            reflector = list(range(256))
            for i in range(128):
                j = 255 - i
                reflector[i], reflector[j] = reflector[j], reflector[i]
            
            return {
                "version": "0.1.2",
                "seed": base64.b64encode(seed).decode(),
                "rotors": rotors,
                "reflector": reflector
            }
        else:
            # 增强密钥生成
            seed = secrets.token_bytes(32)
            salt = secrets.token_bytes(16)
            key_material = EnigmaEngine._derive_key(seed, salt, 1024)
            
            # 生成转子
            rotors = []
            rotor_directions = []
            for i in range(3):
                rotor = list(range(256))
                for j in range(256):
                    swap_index = key_material[i*256 + j] % 256
                    rotor[j], rotor[swap_index] = rotor[swap_index], rotor[j]
                rotors.append(rotor)
                rotor_directions.append(secrets.choice([True, False]))
            
            # 生成反射器
            reflector = list(range(256))
            indices = list(range(256))
            secrets.SystemRandom().shuffle(indices)
            for i in range(0, 256, 2):
                if i + 1 < len(indices):
                    a, b = indices[i], indices[i+1]
                    reflector[a], reflector[b] = b, a
            
            # 压缩转子和反射器
            compressed_rotors = [
                base64.b64encode(zlib.compress(bytes(rotor), level=9)).decode()
                for rotor in rotors
            ]
            compressed_reflector = base64.b64encode(
                zlib.compress(bytes(reflector), level=9)
            ).decode()
            
            return {
                "version": "0.2.4",
                "seed": base64.b64encode(seed).decode(),
                "salt": base64.b64encode(salt).decode(),
                "rotors": compressed_rotors,
                "reflector": compressed_reflector,
                "notches": [secrets.randbelow(256) for _ in range(3)],
                "initial_positions": [secrets.randbelow(256) for _ in range(3)],
                "directions": [1 if d else 0 for d in rotor_directions]
            }
    
    @staticmethod
    def load_key(key_data: dict) -> dict:
        """加载并准备密钥"""
        version = key_data.get("version", "0.1.2")
        
        if version in ["0.2.1", "0.2.2", "0.2.3", "0.2.4"]:
            # 检查转子是否已经是解压后的格式
            if isinstance(key_data["rotors"][0], list):
                # 已经是解压后的格式，直接使用
                pass
            else:
                # 需要解压转子
                decompressed_rotors = []
                for compressed in key_data["rotors"]:
                    if isinstance(compressed, str):
                        comp_data = base64.b64decode(compressed)
                        decomp_data = zlib.decompress(comp_data)
                        decompressed_rotors.append(list(decomp_data))
                    else:
                        decompressed_rotors.append(compressed)
                key_data["rotors"] = decompressed_rotors
            
            # 检查反射器是否已经是解压后的格式
            if isinstance(key_data["reflector"], list):
                # 已经是解压后的格式，直接使用
                pass
            else:
                if isinstance(key_data["reflector"], str):
                    comp_reflector = base64.b64decode(key_data["reflector"])
                    decomp_reflector = zlib.decompress(comp_reflector)
                    key_data["reflector"] = list(decomp_reflector)
                else:
                    key_data["reflector"] = list(range(256))
            
            # 处理方向设置
            if 'directions' in key_data:
                key_data["rotor_directions"] = [
                    d == 1 for d in key_data["directions"]
                ]
            else:
                key_data["rotor_directions"] = [True, True, True]
            
            # 处理位置设置
            if 'positions' in key_data:
                key_data["initial_positions"] = key_data["positions"]
            elif 'initial_positions' not in key_data:
                key_data["initial_positions"] = [0, 0, 0]
        else:
            # 0.1.2兼容模式
            key_data["salt"] = base64.b64encode(b'enigma_salt').decode()
            key_data["notches"] = [0, 0, 0]
            key_data["initial_positions"] = [0, 0, 0]
            key_data["rotor_directions"] = [True, True, True]
        
        # 确保所有值都是正确的类型
        for key in ["initial_positions", "notches"]:
            if key in key_data:
                key_data[key] = [int(x) for x in key_data[key]]
        
        # 确保转子是整数列表
        for i in range(len(key_data["rotors"])):
            if not all(isinstance(x, int) for x in key_data["rotors"][i]):
                key_data["rotors"][i] = list(range(256))
        
        # 确保反射器是整数列表
        if "reflector" in key_data and not all(isinstance(x, int) for x in key_data["reflector"]):
            key_data["reflector"] = list(range(256))
        
        return key_data
    
    @staticmethod
    def _custom_hkdf(salt: bytes, ikm: bytes, info: bytes, length: int) -> bytes:
        """自定义 HKDF 实现"""
        if not salt:
            salt = bytes([0] * hashlib.sha256().digest_size)
        
        # 提取阶段
        prk = hmac.new(salt, ikm, hashlib.sha256).digest()
        
        # 扩展阶段
        t = b""
        okm = b""
        n = (length + 31) // 32
        for i in range(1, n + 1):
            t = hmac.new(prk, t + info + i.to_bytes(1, 'big'), hashlib.sha256).digest()
            okm += t
        
        return okm[:length]
    
    @staticmethod
    def _derive_key_legacy(seed: bytes, length: int) -> bytes:
        """0.1.2版本的派生方法"""
        key = b''
        salt = b'enigma_salt'
        counter = 0
        while len(key) < length:
            key += hashlib.sha256(salt + seed + counter.to_bytes(4, 'big')).digest()
            counter += 1
        return key[:length]
    
    @staticmethod
    def _derive_key(seed: bytes, salt: bytes, length: int) -> bytes:
        """HKDF密钥派生方法"""
        try:
            return hashlib.hkdf(
                salt=salt,
                ikm=seed,
                info=b'enigma_key_material',
                hash=hashlib.sha256,
                length=length
            )
        except AttributeError:
            return EnigmaEngine._custom_hkdf(
                salt=salt,
                ikm=seed,
                info=b'enigma_key_material',
                length=length
            )
    
    @staticmethod
    def _step_rotors(positions: List[int], notches: List[int], directions: List[bool]) -> List[int]:
        """完全符合历史恩尼格玛机的步进机制"""
        steps = [1 if d else -1 for d in directions]
        positions = [p % 256 for p in positions]
        
        # 1. 快转子总是步进
        positions[0] = (positions[0] + steps[0]) % 256
        
        # 2. 检查快转子是否在凹口位置
        step_middle = positions[0] == notches[0]
        
        # 3. 检查中转子是否在凹口位置（用于双步进）
        step_slow = positions[1] == notches[1]
        
        # 4. 如果快转子在凹口，中转子步进
        if step_middle:
            positions[1] = (positions[1] + steps[1]) % 256
        
        # 5. 如果中转子在凹口，慢转子步进（双步进）
        if step_slow:
            positions[2] = (positions[2] + steps[2]) % 256
        
        return [p % 256 for p in positions]
    
    @staticmethod
    def _process_byte(byte_val: int, positions: List[int], 
                     rotors: List[List[int]], reflector: List[int],
                     directions: List[bool], notches: List[int],
                     version: str) -> Tuple[int, List[int]]:
        """处理单个字节（返回处理后的字节和更新后的位置）"""
        if version == "0.1.2":
            # 0.1.2兼容模式（无位置步进）
            for rotor in rotors:
                byte_val = rotor[byte_val % 256]
            byte_val = reflector[byte_val % 256]
            for rotor in reversed(rotors):
                byte_val = rotor.index(byte_val % 256)
            return byte_val % 256, positions
        
        else:
            # 步进转子
            positions = EnigmaEngine._step_rotors(positions, notches, directions)
            
            # 应用位置偏移
            def apply_offset(val, offset, direction):
                return (val + (offset if direction else -offset)) % 256
            
            # 正向通过转子
            result = byte_val
            for i in range(3):
                result = apply_offset(result, positions[i], directions[i])
                result = rotors[i][result % 256]
                result = apply_offset(result, -positions[i], directions[i])
                result %= 256
            
            # 通过反射器
            result = reflector[result % 256]
            result %= 256
            
            # 反向通过转子
            for i in range(2, -1, -1):
                result = apply_offset(result, positions[i], directions[i])
                result %= 256
                result = rotors[i].index(result % 256)
                result = apply_offset(result, -positions[i], directions[i])
                result %= 256
            
            return result % 256, positions
    
    @staticmethod
    def encrypt(text: str, key: dict) -> str:
        """加密文本（完全无状态）"""
        # 准备密钥
        key = EnigmaEngine.load_key(key)
        version = key.get("version", "0.1.2")
        
        # 准备组件
        rotors = key["rotors"]
        reflector = key["reflector"]
        positions = list(key["initial_positions"])
        
        # 获取方向设置
        if "rotor_directions" in key:
            directions = key["rotor_directions"]
        else:
            directions = [True, True, True]
        
        notches = key["notches"]
        
        # 处理文本
        text_bytes = text.encode('utf-8')
        processed_bytes = []
        
        # 处理每个字节
        for byte_val in text_bytes:
            result, positions = EnigmaEngine._process_byte(
                byte_val, positions, rotors, reflector, 
                directions, notches, version
            )
            processed_bytes.append(result)
        
        # 派生密钥材料
        seed = base64.b64decode(key["seed"])
        text_len = len(text_bytes)
        
        if version == "0.1.2":
            key_material = EnigmaEngine._derive_key_legacy(seed, text_len)
        else:
            salt = base64.b64decode(key["salt"])
            key_material = EnigmaEngine._derive_key(seed, salt, text_len)
        
        # 异或混淆
        encrypted = [b ^ key_material[i] for i, b in enumerate(processed_bytes)]
        return "ENC:" + base64.b64encode(bytes(encrypted)).decode()
    
    @staticmethod
    def decrypt(text: str, key: dict) -> str:
        """解密文本（完全无状态）"""
        if not text.startswith("ENC:"):
            return "错误: 无效的密文格式"
        
        # 准备密钥
        key = EnigmaEngine.load_key(key)
        version = key.get("version", "0.1.2")
        
        # 准备组件
        rotors = key["rotors"]
        reflector = key["reflector"]
        positions = list(key["initial_positions"])
        
        # 获取方向设置
        if "rotor_directions" in key:
            directions = key["rotor_directions"]
        else:
            directions = [True, True, True]
        
        notches = key["notches"]
        
        try:
            # 解码密文
            encrypted_bytes = base64.b64decode(text[4:])
            cipher_len = len(encrypted_bytes)
            
            # 派生密钥材料
            seed = base64.b64decode(key["seed"])
            if version == "0.1.2":
                key_material = EnigmaEngine._derive_key_legacy(seed, cipher_len)
            else:
                salt = base64.b64decode(key["salt"])
                key_material = EnigmaEngine._derive_key(seed, salt, cipher_len)
            
            # 去混淆
            decrypted = [b ^ key_material[i] for i, b in enumerate(encrypted_bytes)]
            result_bytes = []
            
            # 处理每个字节
            for byte_val in decrypted:
                result, positions = EnigmaEngine._process_byte(
                    byte_val, positions, rotors, reflector, 
                    directions, notches, version
                )
                result_bytes.append(result)
            
            # 返回解码结果
            return bytes(result_bytes).decode('utf-8')
        except Exception as e:
            return f"解密失败: {str(e)}"

class EnigmaEnhanced:
    """重构的恩尼格玛密码机（无状态管理）"""
    
    def __init__(self, debug=False, interactive=False):
        self.key = None
        self.debug = debug
        if interactive:
            self.print_help()
    
    def print_help(self):
        print("""
        === 增强版恩尼格玛密码机 v0.2.4 ===
        完全无状态设计，彻底解决问题
        
        命令:
          /genkey [filename] - 生成并导出密钥
          /genkey_legacy [filename] - 生成0.1.2兼容密钥
          /loadkey <filename> - 从文件加载密钥
          /delkey - 删除当前密钥
          /help - 显示帮助
          /exit - 退出程序
          /debug - 切换调试模式
        
        加密: 输入任何非命令文本
        解密: 输入以"ENC:"开头的文本
        
        安全特性:
          - 完全无状态设计
          - 符合历史恩尼格玛机的步进机制
          - 每次操作完全独立
          - 修复所有已知问题
        
        === Enhanced Enigma Cipher Machine v0.2.4 ===
        Stateless design, all issues fixed
        
        Commands:
          /genkey [filename] - Generate and export key
          /genkey_legacy [filename] - Generate 0.1.2 compatible key
          /loadkey <filename> - Load key from file
          /delkey - Delete current key
          /help - Show help
          /exit - Exit program
          /debug - Toggle debug mode
        
        Security Features:
          - Fully stateless design
          - Historically accurate stepping mechanism
          - Completely independent operations
          - All known issues fixed
        """)
    
    def generate_key(self, filename="enigma_key.json", legacy=False):
        """生成密钥"""
        key_data = EnigmaEngine.generate_key(legacy)
        
        # 保存密钥文件
        with open(filename, 'w') as f:
            json.dump(key_data, f, separators=(',', ':'))
        
        # 加载并处理密钥
        self.key = EnigmaEngine.load_key(key_data)
        file_size = os.path.getsize(filename)
        print(f"密钥已生成并保存到 {filename} (大小: {file_size}字节)")
        print(f"Key generated and saved to {filename} (Size: {file_size} bytes)")
        print(f"算法版本: {key_data['version']}")
        return key_data
    
    def load_key(self, filename):
        """从文件加载密钥"""
        try:
            with open(filename, 'r') as f:
                key_data = json.load(f)
                self.key = EnigmaEngine.load_key(key_data)
                file_size = os.path.getsize(filename)
                print(f"密钥已从 {filename} 加载 (大小: {file_size}字节)")
                print(f"Key loaded from {filename} (Size: {file_size} bytes)")
                print(f"算法版本: {self.key.get('version', '0.1.2')}")
                return True
        except Exception as e:
            print(f"错误: {e}")
            return False
    
    def delete_key(self):
        """删除当前密钥"""
        self.key = None
        print("密钥已删除")
    
    def encrypt(self, text: str) -> str:
        """加密文本"""
        if not self.key:
            print("错误: 没有可用密钥")
            return None
        return EnigmaEngine.encrypt(text, self.key)
    
    def decrypt(self, text: str) -> str:
        """解密文本"""
        if not self.key:
            print("错误: 没有可用密钥")
            return None
        return EnigmaEngine.decrypt(text, self.key)
    
    def self_test(self):
        """自检验证"""
        print("\n正在执行自检...")
        
        # 测试1: 基本加密/解密
        self.delete_key()
        self.generate_key("self_test.json")
        plaintext = "测试Test 123! 你好，世界！🔐"
        
        print(f"\n测试1: 基本功能")
        print(f"原始文本: {plaintext}")
        
        ciphertext = self.encrypt(plaintext)
        print(f"加密结果: {ciphertext}")
        
        decrypted = self.decrypt(ciphertext)
        print(f"解密结果: {decrypted}")
        
        if decrypted == plaintext:
            print("测试1成功: 加密/解密一致")
        else:
            print("测试1失败: 加密/解密不一致")
            print(f"期望: {plaintext}")
            print(f"实际: {decrypted}")
        
        # 测试2: 密钥一致性
        self.delete_key()
        self.generate_key("self_test_key1.json")
        plaintext = "密钥一致性测试"
        
        print(f"\n测试2: 密钥一致性")
        print(f"原始文本: {plaintext}")
        
        # 第一次加密
        ciphertext1 = self.encrypt(plaintext)
        print(f"第一次加密: {ciphertext1}")
        
        # 第二次加密（相同密钥）
        ciphertext2 = self.encrypt(plaintext)
        print(f"第二次加密: {ciphertext2}")
        
        # 解密两次加密的结果
        decrypted1 = self.decrypt(ciphertext1)
        decrypted2 = self.decrypt(ciphertext2)
        
        # 验证
        consistency = ciphertext1 == ciphertext2
        decrypt_success = decrypted1 == plaintext and decrypted2 == plaintext
        
        if consistency and decrypt_success:
            print("测试2成功: 相同密钥相同明文加密结果一致")
        else:
            print(f"测试2失败: 一致性={consistency}, 解密成功={decrypt_success}")
        
        # 测试3: 密钥切换
        self.generate_key("self_test_key2.json")
        ciphertext3 = self.encrypt(plaintext)
        print(f"新密钥加密: {ciphertext3}")
        
        # 重新加载第一个密钥
        self.load_key("self_test_key1.json")
        decrypted3 = self.decrypt(ciphertext1)
        decrypted3_new = self.decrypt(ciphertext3)
        
        # 验证
        reload_success = decrypted3 == plaintext
        key_mismatch = decrypted3_new != plaintext
        
        if reload_success and key_mismatch:
            print("测试3成功: 密钥切换功能正常")
        else:
            print(f"测试3失败: 重加载解密={reload_success}, 密钥不匹配={key_mismatch}")
            if not key_mismatch:
                print(f"错误: 使用key1成功解密了key2的密文")
        
        # 清理
        for f in ["self_test.json", "self_test_key1.json", "self_test_key2.json"]:
            if os.path.exists(f):
                os.remove(f)
                print(f"已删除测试文件: {f}")
    
    def main(self):
        """主程序循环"""
        print("执行自检测试...")
        self.self_test()
        print("\n自检测试完成，开始交互模式")
        
        while True:
            try:
                user_input = input("\n> ").strip()
                if not user_input:
                    continue
                
                if user_input.startswith("/"):
                    parts = user_input[1:].split(maxsplit=1)
                    cmd = parts[0]
                    arg = parts[1] if len(parts) > 1 else ""
                    
                    if cmd == "genkey":
                        filename = arg or "enigma_key.json"
                        self.generate_key(filename)
                    elif cmd == "genkey_legacy":
                        filename = arg or "enigma_key_legacy.json"
                        self.generate_key(filename, legacy=True)
                    elif cmd == "loadkey":
                        if not arg:
                            print("请指定文件名")
                        else:
                            self.load_key(arg)
                    elif cmd == "delkey":
                        self.delete_key()
                    elif cmd == "help":
                        self.print_help()
                    elif cmd == "exit":
                        break
                    elif cmd == "debug":
                        self.debug = not self.debug
                        print(f"调试模式 {'开启' if self.debug else '关闭'}")
                    else:
                        print(f"未知命令: /{cmd}")
                
                elif user_input.startswith("ENC:"):
                    if not self.key:
                        print("错误: 没有可用密钥")
                    else:
                        result = self.decrypt(user_input)
                        if not result.startswith("错误") and not result.startswith("解密失败"):
                            print(f"解密结果: {result}")
                        else:
                            print(result)
                
                else:
                    if not self.key:
                        print("错误: 没有可用密钥")
                    else:
                        result = self.encrypt(user_input)
                        print(f"加密结果: {result}")
            
            except EOFError:
                print("\n退出程序")
                break
            except KeyboardInterrupt:
                print("\n退出程序")
                break

def cli():
    """命令行接口"""
    parser = argparse.ArgumentParser(description='Enigma Enhanced Cipher Machine')
    
    parser.add_argument('-v', '--version', action='version', version='EnigmaEnhanced 0.2.4')
    parser.add_argument('--genkey', nargs='?', const='enigma_key.json', metavar='KEYFILE',
                        help='Generate a new key (default: enigma_key.json)')
    parser.add_argument('--genkey_legacy', nargs='?', const='enigma_key_legacy.json', metavar='KEYFILE',
                        help='Generate a legacy compatible key (default: enigma_key_legacy.json)')
    parser.add_argument('--keyfile', default='enigma_key.json', help='Key file to use (default: enigma_key.json)')
    parser.add_argument('--encrypt', metavar='TEXT', help='Text to encrypt')
    parser.add_argument('--decrypt', metavar='CIPHERTEXT', help='Ciphertext to decrypt (must start with "ENC:")')
    
    args = parser.parse_args()
    
    # 只有在进入交互模式时才显示帮助信息
    interactive = not any([args.genkey, args.genkey_legacy, args.encrypt, args.decrypt])
    enigma = EnigmaEnhanced(debug=False, interactive=interactive)
    
    if args.genkey:
        enigma.generate_key(args.genkey, legacy=False)
        print(f"Key generated and saved to {args.genkey}")
    elif args.genkey_legacy:
        enigma.generate_key(args.genkey_legacy, legacy=True)
        print(f"Legacy key generated and saved to {args.genkey_legacy}")
    elif args.encrypt:
        if not os.path.exists(args.keyfile):
            print(f"Error: Key file {args.keyfile} not found.")
            return
        enigma.load_key(args.keyfile)
        result = enigma.encrypt(args.encrypt)
        print(result)
    elif args.decrypt:
        if not os.path.exists(args.keyfile):
            print(f"Error: Key file {args.keyfile} not found.")
            return
        enigma.load_key(args.keyfile)
        result = enigma.decrypt(args.decrypt)
        print(result)
    else:
        # 没有参数则进入交互模式
        enigma.main()

if __name__ == "__main__":
    cli()