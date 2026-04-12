import streamlit as st
import pandas as pd
import random
import hashlib 
import time
import os 
from services.lcg import LCG
from services.cesaro import cesaro_test
from services.reports import get_LCG_report
from services.md5_custom import get_md5_hash, count_different_bits
from services.rc5 import rc5_cbc_pad_encrypt, rc5_cbc_pad_decrypt
from services.rsa import generate_rsa_keys, rsa_encrypt_file, rsa_decrypt_file

# --- ІМПОРТ ДЛЯ ЛАБ 5 ---
from services.dsa import generate_dsa_keys, dsa_sign, dsa_verify

M = (2**13) - 1
A = 5**5
C = 3
X0 = 16

def show_lcg():
    tab_gen, tab_compare = st.tabs(["Generator LCG", "Compare with System Random"])

    with tab_gen:
        st.header("Lab №1: LCG")
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("Parameters")
            st.info(f"""
            * m = {M}
            * a = {A}
            * c = {C}
            * seed = {X0}
            """)

            count = st.number_input("Count of numbers:", min_value=1, max_value=100000, value=100)

            if st.button("Generate", use_container_width=True):
                generator = LCG(m=M, a=A, c=C, seed=X0)
                sequence = generator.generate(count)
                period = generator.calculatePeriod(M)
                
                test_seq = generator.generate(max(count, 1000))
                pi_est, error = cesaro_test(test_seq)
                
                st.session_state['results'] = {
                    'seq': sequence,
                    'period': period,
                    'pi': pi_est,
                    'error': error
                }
        with col2:
            st.subheader("Results")
            
            if 'results' in st.session_state:
                res = st.session_state['results']
                m1, m2, m3 = st.columns(3)
                m1.metric(label="Period:", value=res['period'])
                m2.metric("Calculated PI", f"{res['pi']:.5}")
                m3.metric("Absolute Error", f"{res['error']:.5f}", delta_color="inverse")
                
                st.subheader("Generated Pseudo-Nums Table")
                df = pd.DataFrame(res['seq'], columns=["Число"])
                st.dataframe(df, height=300)
        
                report = get_LCG_report(
                    nums=res['seq'], 
                    m=M, a=A, c=C, seed=X0, 
                    period=res['period'], 
                    pi_est=res['pi']
                )
                st.download_button("Create Report", report, "report.txt")
            else:
                st.info("Click 'Generate' button to see the results")

    with tab_compare:
        comp_count = st.slider("Count of numbers:", 1000, 50000, 5000)
        
        if st.button("Compare", use_container_width=True):
            my_gen = LCG(m=M, a=A, c=C, seed=X0)
            lcg_seq = my_gen.generate(comp_count)
            lcg_pi, lcg_err = cesaro_test(lcg_seq)
            
            sys_seq = [random.randint(0, M-1) for _ in range(comp_count)]
            sys_pi, sys_err = cesaro_test(sys_seq)
            
            c1, c2 = st.columns(2)
            
            with c1:
                st.info("LCG")
                st.metric("Pi Estimate", f"{lcg_pi:.5f}")
                st.metric("Error", f"{lcg_err:.5f}")
                
            with c2:
                st.success("System Random")
                st.metric("Pi Estimate", f"{sys_pi:.5f}")
                diff = lcg_err - sys_err
                st.metric("Error", f"{sys_err:.5f}")
                

def show_md5():
    st.header("Lab №2: MD5")
    
    tab_gen, tab_check = st.tabs(["Generate MD5", "File Integrity Check"])
    
    with tab_gen:
        st.subheader("Generate MD5 hash")
        input_type = st.radio("To hash:", ["Text", "File"], horizontal=True)
        
        data_to_hash = b""
        if input_type == "Text":
            text_input = st.text_area("Input some symbols:", "Hello World")
            data_to_hash = text_input.encode('utf-8')
        else:
            uploaded_file = st.file_uploader("Choose file", key="gen_file")
            if uploaded_file is not None:
                data_to_hash = uploaded_file.read()
                st.success(f"File was upploaded ({len(data_to_hash)} byte)")
        
        if "my_hash" not in st.session_state:
            st.session_state.my_hash = None
        if "sys_hash" not in st.session_state:
            st.session_state.sys_hash = None

        if st.button("Generate hash", type="primary"):
            if data_to_hash:
                st.session_state.my_hash = get_md5_hash(data_to_hash)
                st.session_state.sys_hash = hashlib.md5(data_to_hash).hexdigest()

        if st.session_state.my_hash is not None:
            st.markdown("### Results:")
            st.code(st.session_state.my_hash, language="text")
            
            if st.session_state.my_hash == st.session_state.sys_hash:
                st.success("Hash created with my function is the same as created with system function hashlib!")
                
                report_text = f"MD5 Hash: {st.session_state.my_hash}\n"
                
                st.download_button(
                    label="Save in file",
                    data=report_text,
                    file_name="md5_result.txt",
                )
            else:
                st.error(f"Error! System hash: {st.session_state.sys_hash}")

    with tab_check:
        st.subheader("File Integrity Check")
        
        check_col1, check_col2 = st.columns(2)
        with check_col1:
            check_file = st.file_uploader("Upload file to verify", key="verify_file")
        with check_col2:
            expected_hash_input = st.text_input("Expected MD5 Hash")
            
        if st.button("Verify File Integrity"):
            if check_file and expected_hash_input:
                file_content = check_file.read()
                calculated_check_hash = get_md5_hash(file_content)
                
                if calculated_check_hash.lower() == expected_hash_input.strip().lower():
                    st.success(f"Success! The file integrity is verified.\nHash: {calculated_check_hash}")
                else:
                    st.error("Integrity check failed! The file has been modified.")
                    st.warning(f"Expected: {expected_hash_input}")
                    st.warning(f"Actual:   {calculated_check_hash}")
            else:
                st.warning("Please upload a file and provide the expected hash.")


def show_rc5():
    st.header("Lab №3: RC5")
    
    W = 16
    R = 20
    
    st.info(f"**Parameters (Variant 4)**: w = {W} bits, r = {R} rounds.")
    
    tab_enc, tab_dec = st.tabs(["Encrypt File", "Decrypt File"])
    
    with tab_enc:
        st.subheader("Encrypt using RC5-CBC-Pad")
        passphrase = st.text_input("Enter passphrase:", type="password", key="enc_pass")
        enc_file = st.file_uploader("Choose file to encrypt", key="enc_file")
        
        if st.button("Encrypt", type="primary", use_container_width=True):
            if passphrase and enc_file:
                file_data = enc_file.read()
                
                pass_hash_hex = get_md5_hash(passphrase.encode('utf-8'))
                key_bytes = bytes.fromhex(pass_hash_hex) 
                
                start_time = time.time()
                encrypted_data = rc5_cbc_pad_encrypt(file_data, key_bytes, W, R)
                end_time = time.time()
                
                st.success(f"File encrypted successfully in {end_time - start_time:.4f} seconds!")
                st.download_button(
                    label="Download Encrypted File",
                    data=encrypted_data,
                    file_name=f"encrypted_{enc_file.name}",
                    mime="application/octet-stream"
                )
            else:
                st.warning("Please provide both a passphrase and a file.")
                
    with tab_dec:
        st.subheader("Decrypt using RC5-CBC-Pad")
        dec_passphrase = st.text_input("Enter passphrase:", type="password", key="dec_pass")
        dec_file = st.file_uploader("Choose encrypted file", key="dec_file")
        
        if st.button("Decrypt", type="primary", use_container_width=True):
            if dec_passphrase and dec_file:
                enc_data = dec_file.read()
                
                pass_hash_hex = get_md5_hash(dec_passphrase.encode('utf-8'))
                key_bytes = bytes.fromhex(pass_hash_hex)
                
                try:
                    start_time = time.time()
                    decrypted_data = rc5_cbc_pad_decrypt(enc_data, key_bytes, W, R)
                    end_time = time.time()
                    
                    st.success(f"File decrypted successfully in {end_time - start_time:.4f} seconds!")
                    st.download_button(
                        label="Download Decrypted File",
                        data=decrypted_data,
                        file_name=f"decrypted_{dec_file.name.replace('encrypted_', '')}",
                        mime="application/octet-stream"
                    )
                except Exception as e:
                    st.error(f"Decryption failed! Check your passphrase or file integrity. Error: {e}")
            else:
                st.warning("Please provide both a passphrase and a file.")


def show_rsa():
    st.header("Lab №4: RSA")
    
    tab_keys, tab_enc, tab_dec, tab_speed = st.tabs(["Manage Keys", "Encrypt File", "Decrypt File", "Compare Speed (RC5 vs RSA)"])
    
    with tab_keys:
        st.subheader("Generate New Keys")
        if st.button("Generate RSA Key Pair (2048 bits)", use_container_width=True):
            with st.spinner("Generating keys..."):
                priv_pem, pub_pem = generate_rsa_keys(2048)
                st.session_state['rsa_priv'] = priv_pem
                st.session_state['rsa_pub'] = pub_pem
                st.success("Keys generated successfully!")
        
        col1, col2 = st.columns(2)
        if 'rsa_priv' in st.session_state and 'rsa_pub' in st.session_state:
            with col1:
                st.download_button("Download Private Key (PEM)", st.session_state['rsa_priv'], "private_key.pem")
            with col2:
                st.download_button("Download Public Key (PEM)", st.session_state['rsa_pub'], "public_key.pem")

    with tab_enc:
        st.subheader("Encrypt File using RSA")
    
        pub_file = st.file_uploader("Upload Public Key (.pem)", type=['pem'], key="rsa_pub_upload")
        data_to_encrypt = st.file_uploader("Choose file to encrypt", key="rsa_enc_file")
        
        if st.button("Encrypt File", type="primary", use_container_width=True):
            if pub_file and data_to_encrypt:
                pub_key_bytes = pub_file.read()
                file_bytes = data_to_encrypt.read()
                
                try:
                    start_time = time.time()
                    encrypted_data = rsa_encrypt_file(file_bytes, pub_key_bytes)
                    end_time = time.time()
                    
                    st.success(f"File encrypted in {end_time - start_time:.4f} seconds!")
                    st.download_button(
                        "Download Encrypted File",
                        data=encrypted_data,
                        file_name=f"rsa_enc_{data_to_encrypt.name}",
                        mime="application/octet-stream"
                    )
                except Exception as e:
                    st.error(f"Encryption failed: {e}")
            else:
                st.warning("Please upload both the public key and a file to encrypt.")

    with tab_dec:
        st.subheader("Decrypt File using RSA")
        
        priv_file = st.file_uploader("Upload Private Key (.pem)", type=['pem'], key="rsa_priv_upload")
        data_to_decrypt = st.file_uploader("Choose file to decrypt", key="rsa_dec_file")
        
        if st.button("Decrypt File", type="primary", use_container_width=True):
            if priv_file and data_to_decrypt:
                priv_key_bytes = priv_file.read()
                enc_file_bytes = data_to_decrypt.read()
                
                try:
                    start_time = time.time()
                    decrypted_data = rsa_decrypt_file(enc_file_bytes, priv_key_bytes)
                    end_time = time.time()
                    
                    st.success(f"File decrypted in {end_time - start_time:.4f} seconds!")
                    st.download_button(
                        "Download Decrypted File",
                        data=decrypted_data,
                        file_name=f"rsa_dec_{data_to_decrypt.name.replace('rsa_enc_', '')}",
                        mime="application/octet-stream"
                    )
                except Exception as e:
                    st.error(f"Decryption failed. Check key/file match. Error: {e}")
            else:
                st.warning("Please upload both the private key and the encrypted file.")
                
    with tab_speed:
        st.subheader("Speed Comparison: RSA vs RC5")
        data_size_kb = st.slider("Select data size (KB)", 10, 500, 100)
        
        if st.button("Run Benchmark"):
            test_data = os.urandom(data_size_kb * 1024)
            st.info(f"Generated {data_size_kb} KB of random data.")
            
            pass_hash_hex = get_md5_hash(b"benchmark_password")
            rc5_key = bytes.fromhex(pass_hash_hex)
            rc5_start = time.time()
            _ = rc5_cbc_pad_encrypt(test_data, rc5_key, 16, 20)
            rc5_time = time.time() - rc5_start
            
            priv_pem, pub_pem = generate_rsa_keys()
            rsa_start = time.time()
            _ = rsa_encrypt_file(test_data, pub_pem)
            rsa_time = time.time() - rsa_start
            
            col1, col2 = st.columns(2)
            col1.metric("RC5 Encryption Time", f"{rc5_time:.4f} s")
            col2.metric("RSA Encryption Time", f"{rsa_time:.4f} s")


def show_dsa():
    st.header("Lab №5: DSS (DSA Digital Signature)")
    
    tab_keys, tab_sign, tab_verify = st.tabs(["Manage Keys", "Sign Data", "Verify Signature"])
    
    with tab_keys:
        st.subheader("Generate New DSA Keys")
        if st.button("Generate DSA Key Pair (1024 bits)", use_container_width=True):
            with st.spinner("Generating DSA keys..."):
                priv_pem, pub_pem = generate_dsa_keys(1024)
                st.session_state['dsa_priv'] = priv_pem
                st.session_state['dsa_pub'] = pub_pem
                st.success("DSA Keys generated successfully!")
        
        col1, col2 = st.columns(2)
        if 'dsa_priv' in st.session_state and 'dsa_pub' in st.session_state:
            with col1:
                st.download_button("Download Private Key (PEM)", st.session_state['dsa_priv'], "dsa_private_key.pem")
            with col2:
                st.download_button("Download Public Key (PEM)", st.session_state['dsa_pub'], "dsa_public_key.pem")

    with tab_sign:
        st.subheader("Sign Data using DSA")
        priv_file = st.file_uploader("Upload Private Key (.pem)", type=['pem'], key="dsa_priv_sign")
        
        input_type = st.radio("Data to sign:", ["Text", "File"], horizontal=True, key="dsa_input_type")
        data_to_sign = b""
        
        if input_type == "Text":
            text_input = st.text_area("Input some symbols to sign:")
            data_to_sign = text_input.encode('utf-8')
        else:
            uploaded_file = st.file_uploader("Choose file to sign", key="dsa_file_sign")
            if uploaded_file is not None:
                data_to_sign = uploaded_file.read()

        if st.button("Sign Data", type="primary", use_container_width=True):
            if priv_file and data_to_sign:
                priv_key_bytes = priv_file.read()
                try:
                    signature_hex = dsa_sign(data_to_sign, priv_key_bytes)
                    st.success("Data signed successfully!")
                    st.text_area("Signature (Hex):", signature_hex, height=150)
                    
                    st.download_button(
                        "Download Signature (.hex)",
                        data=signature_hex,
                        file_name="signature.hex",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"Signing failed. Error: {e}")
            else:
                st.warning("Please upload the private key and provide data to sign.")

    with tab_verify:
        st.subheader("Verify DSA Signature")
        pub_file = st.file_uploader("Upload Public Key (.pem)", type=['pem'], key="dsa_pub_verify")
        
        verify_input_type = st.radio("Data to verify:", ["Text", "File"], horizontal=True, key="dsa_verify_type")
        data_to_verify = b""
        
        if verify_input_type == "Text":
            verify_text = st.text_area("Input data that was signed:")
            data_to_verify = verify_text.encode('utf-8')
        else:
            verify_file = st.file_uploader("Choose data file", key="dsa_file_verify")
            if verify_file is not None:
                data_to_verify = verify_file.read()

        sig_input_type = st.radio("Signature format:", ["Text (Hex)", "File (.hex)"], horizontal=True, key="sig_input_type")
        signature_hex_input = ""
        
        if sig_input_type == "Text (Hex)":
            signature_hex_input = st.text_area("Input Signature in Hex:")
        else:
            sig_file = st.file_uploader("Choose signature file", key="dsa_sig_file")
            if sig_file is not None:
                signature_hex_input = sig_file.read().decode('utf-8').strip()

        if st.button("Verify Signature", type="primary", use_container_width=True):
            if pub_file and data_to_verify and signature_hex_input:
                pub_key_bytes = pub_file.read()
                
                is_valid = dsa_verify(signature_hex_input, data_to_verify, pub_key_bytes)
                if is_valid:
                    st.success("Success! The signature is valid and data integrity is confirmed.")
                else:
                    st.error("Verification failed! The signature is invalid or data has been tampered with.")
            else:
                st.warning("Please provide public key, data, and signature to verify.")

def main():
    with st.sidebar:
        st.markdown("Student: Olesia Kostak")
        
        page = st.radio(
            "Navigation:",
            ["Lab №1: LCG",
             "Lab №2: MD5",
             "Lab №3: RC5",
             "Lab №4: RSA",
             "Lab №5: DSA"]  
        )
    if page == "Lab №1: LCG":
        show_lcg()
    if page == 'Lab №2: MD5':
        show_md5()
    if page == 'Lab №3: RC5':
        show_rc5()  
    if page == 'Lab №4: RSA':
        show_rsa()
    if page == 'Lab №5: DSA':
        show_dsa()

if __name__ == "__main__":
    main()