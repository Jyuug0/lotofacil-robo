import pandas as pd
import random
import requests
from collections import Counter

# =========================
# 📥 LEITURA
# =========================
df = pd.read_excel("dados.xlsx")
numeros = df.iloc[:, 1:16].values

treino = numeros[:-50]
teste = numeros[-50:]

# =========================
# 📊 BASE
# =========================
flat = treino.flatten()
freq = Counter(flat)

atraso = {}
for n in range(1, 26):
    atraso[n] = 0
    for i in range(len(treino)-1, -1, -1):
        if n in treino[i]:
            break
        atraso[n] += 1

score = {}
for n in range(1, 26):
    score[n] = (freq[n]**1.2)*1.5 - (atraso[n]**0.85)*1.1

base = sorted(score, key=score.get, reverse=True)[:21]
ultimo = set(treino[-1])

# =========================
# 🎯 REGRAS
# =========================
def linhas(j):
    return [
        sum(1 for n in j if 1<=n<=5),
        sum(1 for n in j if 6<=n<=10),
        sum(1 for n in j if 11<=n<=15),
        sum(1 for n in j if 16<=n<=20),
        sum(1 for n in j if 21<=n<=25),
    ]

def sequencia(j):
    j = sorted(j)
    m=1; c=1
    for i in range(1,len(j)):
        if j[i]==j[i-1]+1:
            c+=1; m=max(m,c)
        else:
            c=1
    return m

def parecido(j, lista):
    for x in lista:
        if len(set(j)&set(x))>=12:
            return True
    return False

# =========================
# 🎲 GERAR JOGO
# =========================
def gerar():
    for _ in range(300):
        j = set(random.sample(base,15))

        if not (8 <= len(j&ultimo) <= 12):
            continue
        if not (5 <= sum(n%2==0 for n in j) <= 10):
            continue
        if not (6 <= sum(n<=13 for n in j) <= 10):
            continue
        if any(x>5 for x in linhas(j)):
            continue
        if sequencia(j)>4:
            continue
        if not (170 <= sum(j) <= 230):
            continue

        return sorted(j)

    return sorted(random.sample(base,15))

# =========================
# 📊 AVALIAR
# =========================
def avaliar(j, dados):
    s=0
    for c in dados:
        a=len(set(j)&set(c))
        if a==14: s+=10
        elif a==15: s+=50
    return s

# =========================
# 🧬 EVOLUIR
# =========================
def evoluir():
    pop=[gerar() for _ in range(400)]

    for _ in range(8):
        pop.sort(key=lambda j: avaliar(j, treino), reverse=True)
        elite=pop[:80]

        nova=[]
        hist=[]

        for j in elite:
            if not parecido(j,hist):
                nova.append(j)
                hist.append(j)

        while len(nova)<400:
            p1,p2=random.sample(elite,2)
            filho=list(set(p1[:7]+p2[7:]))

            while len(filho)<15:
                filho.append(random.choice(base))

            if random.random()<0.3:
                filho[random.randint(0,len(filho)-1)] = random.choice(base)

            filho=sorted(set(filho))

            while len(filho)<15:
                filho.append(random.choice(base))

            filho=sorted(filho)

            if parecido(filho,hist):
                continue

            hist.append(filho)
            nova.append(filho)

        pop=nova

    return pop

# =========================
# 🚀 EXECUÇÃO
# =========================
print("🔄 Gerando jogos...")

final=[]

for _ in range(63):
    while True:
        j=random.choice(evoluir())
        if not parecido(j, final):
            final.append(j)
            break

# =========================
# 📁 EXPORTAR
# =========================
df_out = pd.DataFrame(final)
df_out.columns = [f"N{i}" for i in range(1,16)]
df_out.insert(0, "Jogo", range(1,64))

nome="resultado.xlsx"
df_out.to_excel(nome,index=False)

print("Arquivo gerado:", nome)

# =========================
# 📲 TELEGRAM
# =========================
TOKEN = "SEU_TOKEN_AQUI"
CHAT_ID = "SEU_CHAT_ID_AQUI"

def enviar():
    url=f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    with open(nome,"rb") as f:
        requests.post(url,data={"chat_id":CHAT_ID},files={"document":f})

enviar()
