from app.embedding   import create_embedding

text = "Python course fee is 5000 BDT."

vector = create_embedding(text)

print("Vector Length:", len(vector))
print("First 5 Values:", vector[:5])