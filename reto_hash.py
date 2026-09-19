import hashlib, time
target = "ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f"
t0 = time.time()
for i in range(10**8):
    if hashlib.sha256(f"{i:08d}".encode()).hexdigest() == target:
        print(f"Clave encontrada: {i:08d} en {time.time()-t0:.2f}s")
        break
# print(f"Tiempo total: {time.time()-t0:.2f}s")