:: The list of ciphers can be obtained by looking at the Client Hello message in
:: Wireshark, then converting it using the cipherlist array at

@echo off
"%~dp0curl.exe" ^
    --ciphers "TLS_AES_128_GCM_SHA256,TLS_CHACHA20_POLY1305_SHA256,TLS_AES_256_GCM_SHA384,TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256,TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256,TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA,TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA,TLS_RSA_WITH_AES_128_GCM_SHA256,TLS_RSA_WITH_AES_256_GCM_SHA384,TLS_RSA_WITH_AES_128_CBC_SHA,TLS_RSA_WITH_AES_256_CBC_SHA" ^
    --curves X25519:P-256:P-384:P-521:ffdhe2048:ffdhe3072 ^
    --signature-hashes ecdsa_secp256r1_sha256,ecdsa_secp384r1_sha384,ecdsa_secp521r1_sha512,rsa_pss_rsae_sha256,rsa_pss_rsae_sha384,rsa_pss_rsae_sha512,rsa_pkcs1_sha256,rsa_pkcs1_sha384,rsa_pkcs1_sha512,ecdsa_sha1,rsa_pkcs1_sha1 ^
    -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0" ^
    -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" ^
    -H "Accept-Language: en-US,en;q=0.5" ^
    -H "Accept-Encoding: gzip, deflate, br, zstd" ^
    -H "Sec-GPC: 1" ^
    -H "Upgrade-Insecure-Requests: 1" ^
    -H "Sec-Fetch-Dest: document" ^
    -H "Sec-Fetch-Mode: navigate" ^
    -H "Sec-Fetch-Site: none" ^
    -H "Sec-Fetch-User: ?1" ^
    -H "Priority: u=0, i" ^
    -H "TE: Trailers" ^
    --http2 ^
    --http2-settings "1:65536;2:0;4:131072;5:16384" ^
    --http2-pseudo-headers-order "mpas" ^
    --http2-window-update 12517377 ^
    --http2-stream-weight 42 ^
    --http2-stream-exclusive 0 ^
    --compressed ^
    --ech grease ^
    --tls-extension-order "0-23-65281-10-11-16-5-34-51-43-13-28-65037" ^
    --tls-delegated-credentials "ecdsa_secp256r1_sha256:ecdsa_secp384r1_sha384:ecdsa_secp521r1_sha512:ecdsa_sha1" ^
    --tls-record-size-limit 16385 ^
    --tls-key-shares-limit 3 ^
    --cert-compression zlib,brotli,zstd ^
    --tls-signed-cert-timestamps ^
    %*
