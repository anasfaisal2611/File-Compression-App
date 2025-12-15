import DSA
from collections import Counter
import heapq
import os
import json
import time
from bitarray import bitarray
import pandas as pd
import zlib


from DSA import huffmanCodes

def chunked_file_reader(filename, block_size):
    with open(filename, 'r', encoding='utf-8') as fp:

        while True:
            chunk = fp.read(block_size)
            if not chunk:
                break
            yield chunk

# def read_from_file_v2(filename, block_size=1024*8):
#     with open(filename, 'r') as fp:
#         for chunk in chunked_file_reader(fp, block_size):


            # processing the content chunk from the file
def frequency_counter(filename,blocksize):
    freq=Counter()
    for block in chunked_file_reader(filename,blocksize):
        freq.update(block)
    return freq
def save_codes_to_file(codes, filename="codes.json"):
    """Save Huffman code dictionary to JSON for decoding later."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(codes, f)

def load_codes_from_file(filename="codes.json"):
    """Load Huffman code dictionary back from JSON file."""
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)



# def compress_file(filename):
#     """Compress a file using Huffman coding and return compression stats."""
#     start_time = time.time()
#
#     # Step 1: Frequency count
#     ans = frequency_counter(filename, 1024)
#     s, frequency = "", []
#     for char, freq in ans.items():
#         s += char
#         frequency.append(freq)
#
#     # Step 2: Generate Huffman codes
#     result = huffmanCodes(s, frequency)
#     save_codes_to_file(result)
#
#     # Step 3: Encode content
#     with open(filename, "r", encoding="utf-8") as f:
#         content = f.read()
#     encoded_text = "".join(result[ch] for ch in content if ch in result)
#
#     # Step 4 & 5: Use bitarray for efficient bit storage
#     bit_arr = bitarray(encoded_text)
#     padding = (8 - len(bit_arr) % 8) % 8
#     bit_arr.extend('0' * padding)
#
# # Step 6: Save compressed file (store padding info)
#     with open("compressed.bin", "wb") as out:
#         out.write(bytes([padding]))  # first byte stores padding count
#         bit_arr.tofile(out)
#
#     # Step 7: Compression ratio
#     original_size = os.path.getsize(filename)
#     compressed_size = os.path.getsize("compressed.bin")
#     ratio = (1 - (compressed_size / original_size)) * 100
#
#
#     # Step 8: Return stats for GUI
#     end_time = time.time()
#     duration = round(end_time - start_time, 3)
#
#     save_log(filename, {
#     "original_size": original_size,
#     "compressed_size": compressed_size,
#     "compression_ratio": ratio,
#     "time_taken": duration
# })
#
#
#     return {
#         "original_size": original_size,
#         "compressed_size": compressed_size,
#         "compression_ratio": round(ratio, 2),
#         "time_taken": duration,
#     }


def compress_file(filename, block_size=1024*1024):
    """Compress a file using Huffman coding safely for large files."""
    start_time = time.time()

    # Frequency count
    ans = frequency_counter(filename, block_size)
    if not ans:
        print(" File is empty. Cannot compress.")
        return

    s, frequency = "", []
    for char, freq in ans.items():
        s += char
        frequency.append(freq)

    #Generate Huffman codes
    result = huffmanCodes(s, frequency)
    save_codes_to_file(result)

    # Encode content incrementally
    bit_arr = bitarray()
    for block in chunked_file_reader(filename, block_size):
        encoded_block = "".join(result[ch] for ch in block if ch in result)
        bit_arr.extend(encoded_block)


    padding = (8 - len(bit_arr) % 8) % 8
    bit_arr.extend('0' * padding)
    compressed_name = f"{os.path.splitext(filename)[0]}_compressed.bin"
    with open(compressed_name, "wb") as out:
        out.write(bytes([padding]))
        bit_arr.tofile(out)



    with open("compressed.bin", "wb") as out:
        out.write(bytes([padding]))  # first byte stores padding count
        bit_arr.tofile(out)

    # Step 6: Stats
    original_size = os.path.getsize(filename)
    compressed_size = os.path.getsize("compressed.bin")
    ratio = (1 - (compressed_size / original_size)) * 100
    duration = round(time.time() - start_time, 3)

    save_log(filename, {
        "original_size": original_size,
        "compressed_size": compressed_size,
        "compression_ratio": ratio,
        "time_taken": duration
    })

    return {
        "original_size": original_size,
        "compressed_size": compressed_size,
        "compression_ratio": round(ratio, 2),
        "time_taken": duration,
        "compressed_file": compressed_name
    }



def save_log(filename, stats):
    """Append compression data to log file."""
    with open("log.csv", "a", encoding="utf-8") as f:
        f.write(f"{filename},{stats['original_size']},{stats['compressed_size']},"
                f"{stats['compression_ratio']},{stats['time_taken']}\n")

def show_log():
    """Display log.csv as a pandas DataFrame."""
    try:
        df = pd.read_csv("log.csv", names=["File", "Original", "Compressed", "Ratio", "Time"])
        print("\nCompression History:\n", df)
    except FileNotFoundError:
        print("No log file found yet.")

def compare_with_zlib(filename):
    """Compare custom Huffman compression with Python's built-in zlib."""
    with open(filename, 'rb') as f:
        data = f.read()
    zlib_compressed = zlib.compress(data)
    zlib_ratio = (1 - len(zlib_compressed) / len(data)) * 100

    print(f"\n Zlib Compression Ratio: {zlib_ratio:.2f}%")
    print(f" Huffman Compression Ratio will be shown after running compress_file()")
    return round(zlib_ratio, 2)


def decompress_file(compressed_file, codes_file="codes.json"):
    """Decompress a Huffman-compressed file safely and restore original name."""
    if not os.path.exists(compressed_file):
        print("❌ No compressed file found.")
        return

    start_time = time.time()

    try:
        result = load_codes_from_file(codes_file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("❌ Codes file missing or corrupted.")
        return

    reverse_codes = {v: k for k, v in result.items()}

    with open(compressed_file, "rb") as f:
        padding = f.read(1)[0]
        byte_data = f.read()

    bit_arr = bitarray()
    bit_arr.frombytes(byte_data)
    if padding > 0:
        bit_arr = bit_arr[:-padding]
    bit_string = bit_arr.to01()

    decoded_text = []
    current_bits = ""
    for bit in bit_string:
        current_bits += bit
        if current_bits in reverse_codes:
            decoded_text.append(reverse_codes[current_bits])
            current_bits = ""

    # Generate output name from compressed filename
    base_name = compressed_file.replace("_compressed.bin", "_decompressed.txt")
    output_file = base_name
    counter = 1
    while os.path.exists(output_file):
        output_file = base_name.replace(".txt", f"_{counter}.txt")
        counter += 1

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("".join(decoded_text))

    duration = round(time.time() - start_time, 3)
    print(f"✅ Decompression complete → {output_file}")
    return {"time_taken": duration, "output_file": output_file}

# def decompress_file(compressed_file="compressed.bin", codes_file="codes.json"):
#     """Decompress a Huffman-compressed binary file."""
#     start_time = time.time()
#
#     # Step 1: Load codes
#     result = load_codes_from_file(codes_file)
#     reverse_codes = {v: k for k, v in result.items()}
#
#     # Step 2: Read compressed file
#     with open(compressed_file, "rb") as f:
#         padding = ord(f.read(1))  # read first byte for padding
#         byte_data = f.read()
#
#     # Step 3: Convert bytes back to bits
#     # Step 3: Convert bytes back to bits using bitarray
#     bit_arr = bitarray()
#     bit_arr.frombytes(byte_data)
#     if padding > 0:
#         bit_arr = bit_arr[:-padding]
#     bit_string = bit_arr.to01()
#
#     # Step 4: Decode bits
#     decoded_text = ""
#     current_bits = ""
#     for bit in bit_string:
#         current_bits += bit
#         if current_bits in reverse_codes:
#             decoded_text += reverse_codes[current_bits]
#             current_bits = ""
#
#     # Step 5: Write output
#     with open("decompressed.txt", "w", encoding="utf-8") as f:
#         f.write(decoded_text)
#
#     end_time = time.time()
#     duration = round(end_time - start_time, 3)
#
#     return {"time_taken": duration}


import os


def select_file_from_folder(folder="."):
    """Display all files of allowed types in the folder and let the user select one."""
    allowed_extensions = (".txt", ".csv", ".json", ".log",".docx",".png",".jpeg",".pdf")  # Add any extensions you want
    files = [f for f in os.listdir(folder) if f.endswith(allowed_extensions)]

    if not files:
        print(" No files found with allowed extensions in the folder.")
        exit()

    print("\nAvailable files:")
    for idx, f in enumerate(files, start=1):
        print(f"{idx}. {f}")

    while True:
        choice = input(f"\nSelect a file (1-{len(files)}): ")
        if choice.isdigit() and 1 <= int(choice) <= len(files):
            return files[int(choice) - 1]
        else:
            print(" Invalid choice. Try again.")


if __name__ == "__main__":

    if __name__ == "__main__":
        while True:
            print("\n===================================")
            print(" Huffman Compression Utility")
            print("===================================")
            print("1. Compress a file")
            print("2. Decompress a file")
            print("3. View history")
            print("4. Exit")

            choice = input("Enter your choice (1-4): ").strip()

            # Option 1: Compress
            if choice == "1":
                allowed = (".txt", ".csv", ".json", ".log", ".docx", ".pdf")
                files = [f for f in os.listdir(".") if f.endswith(allowed) and not f.endswith("_compressed.bin")]
                if not files:
                    print(" No uncompressed files found.")
                    continue

                print("\nAvailable files to compress:")
                for i, f in enumerate(files, start=1):
                    print(f"{i}. {f}")

                pick = input(f"Select a file (1-{len(files)}): ").strip()
                if not pick.isdigit() or not (1 <= int(pick) <= len(files)):
                    print(" Invalid selection.")
                    continue

                filename = files[int(pick) - 1]
                print(f"\nCompressing '{filename}'...")
                try:
                    stats = compress_file(filename)
                    print(f"\n Compression Complete!")
                    print(f"File saved as: {stats['compressed_file']}")
                    print(f"Compression Ratio: {stats['compression_ratio']}%")
                except Exception as e:
                    print(f" Compression failed: {e}")

            # Option 2: Decompress
            elif choice == "2":
                compressed_files = [f for f in os.listdir(".") if f.endswith("_compressed.bin")]
                if not compressed_files:
                    print(" No compressed files found.")
                    continue

                print("\nAvailable compressed files:")
                for i, f in enumerate(compressed_files, start=1):
                    print(f"{i}. {f}")

                pick = input(f"Select a file to decompress (1-{len(compressed_files)}): ").strip()
                if not pick.isdigit() or not (1 <= int(pick) <= len(compressed_files)):
                    print(" Invalid selection.")
                    continue

                comp_file = compressed_files[int(pick) - 1]
                print(f"\nDecompressing '{comp_file}'...")
                try:
                    result = decompress_file(comp_file)
                    if result:
                        print(f"Done! Output: {result['output_file']} (Time: {result['time_taken']}s)")
                except Exception as e:
                    print(f" Decompression failed: {e}")

            # Option 3: View History
            elif choice == "3":
                print("\nCompression History:\n")
                try:
                    df = pd.read_csv("log.csv",
                                     names=["File", "Original (B)", "Compressed (B)", "Ratio (%)", "Time (s)"])
                    print(df.to_string(index=False))
                except FileNotFoundError:
                    print("⚠ No history found yet. Try compressing a file first.")
                except Exception as e:
                    print(f" Error reading log: {e}")

            # Option 4: Exit
            elif choice == "4":
                print(" Exiting program. Goodbye!")
                break

            else:
                print(" Invalid choice. Please select 1–4.")

# if __name__ == "__main__":
#     file = "sample.txt"  # your input file
#
#     print("Comparing with zlib first...")
#     zratio = compare_with_zlib(file)
#
#     print("\nCompressing file with Huffman coding...")
#     stats = compress_file(file)
#     print(f Compression Complete in {stats['time_taken']}s")
#     print(f"Original Size: {stats['original_size']} bytes")
#     print(f"Compressed Size: {stats['compressed_size']} bytes")
#     print(f"Compression Ratio: {stats['compression_ratio']}%")
#
#     print("\nDecompressing file...")
#     result = decompress_file()
#     print(f" Decompression Complete in {result['time_taken']}s")
#
#     print("\n Log of past compressions:")
#     show_log()

    # filename = "sample"  # put your text file name here
    # s=''
    # frequency=[]
    # # read_from_file_v2(filename, block_size=1024*1)  # read 4KB at a time
    # ans=frequency_counter(filename,1024*1)
    # print(ans)
    # for char,freq in ans.items():
    #     s+=char
    #     frequency.append(freq)
    # print(s)
    # print(char)
    # result=huffmanCodes(s,frequency)

    # print(result)
    # with open(filename,"r",encoding="utf-8") as f:
    #     content=f.read()
    # encoded_text="".join(result[ch] for ch in content if ch in result)
    # b=bytearray()
    # for i in range(0,len(encoded_text),8):
    #     byte=encoded_text[i:i+8]
    #     b.append(int(byte.ljust(8,'0'),2))
    # with open("compressed.bin","wb") as out:
    #     out.write(b)
    # with open("compressed.bin","rb") as f:
    #     byte_data=f.read()

    # bit_string=""
    # for byte in byte_data:

    #     bits=bin(byte)[2:].rjust(8,"0")
    #     bit_string+=bits
    # reverse_codes={v:k for k,v in result.items()}#reversing the code dictionary
    # decoded_text=""
    # current_bits=""
    # for bit in bit_string:
        
    #     current_bits+=bit
        
    #     if current_bits in reverse_codes:

    #         decoded_text+=reverse_codes[current_bits]
            
    #         current_bits=''
    # print(decoded_text)
    # with open("decompressed.txt","w",encoding="utf-8") as f:
    #     f.write(decoded_text)

