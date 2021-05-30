out2 = []

length = input("Nombre de listes: ")
length = int(length)

for i in range(length):
    x = (input("Enter something: "))
    split = x.split(",")
    out2.append(split)

partiel_sol=[]

for t1 in out2[0]:
    for t2 in out2[1]:
       elem2 = [t1,t2]
       partiel_sol.append(elem2)
       
length_in_list = len(partiel_sol[0])

final=[]
a=0
while a < length_in_list:
    for x in out2[2:]:
        for i in partiel_sol:
            final.append([i,x[a]])
    a = a+1

print ("Résultat: ",final)

