
Gott
====

#### Esse é um pacote para manipulação de funcões matematicas

#### Instalação:

`pip install gott`

#### Exemplo:

```
import gott
f = gott.newFunction('x^2 -2*x + 1')
print(f)
print(f(2))
df = f.derivada()
```