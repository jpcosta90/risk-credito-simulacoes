# Converted from Untitled2.ipynb
# --- Cell 1 ---
chave_prob = {1 : 3.00,
              2:  2.40,
              3:  1.80,
              4:  0.95,
              5:  0.60,
              6:  0.25}   
    
chave_valr = {1 : 1.00,
             2:  1.50,
             3:  2.00,
             4:  3.00,
             5:  3.50,
             6:  4.00}
# --- Cell 2 ---
class cliente:
    def __init__(self, codigo):
        self.codigo = codigo
        self.porte = int(np.where(np.random.multinomial(1, [0.419, 0.156, 0.167, 0.146, 0.072, 0.041], size=1) == 1)[1][0] + 1)
        self.inad = max(0.06 + np.random.normal(0., 0.005),0.0003) * chave_prob[self.porte]
        self.mtlp = chave_valr[self.porte]
