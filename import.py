#!/env/python3
import os

os.system('git config --global user.name streich.mobile@gmail.com')
os.system('git config --global user.password 49445128b26fa4b9b1811e1f4dc9e4d9848270a5')

print("Pulling newest Revision of the Project")
os.system('git clone https://github.com/bakulf/mv')

