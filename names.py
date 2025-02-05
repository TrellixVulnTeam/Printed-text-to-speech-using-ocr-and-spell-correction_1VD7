import re
text = 'my name is chandrasekhar'
text = """ hi, balu, @@ my name is harsha. i am from vizag and my brother name is harshablaze.
 welcome to anits iam from nallajerla city gollagudem locality west godavari district :ap Andhra"""

input_file = open("text.txt",'r')
text = input_file.read()
text = text.replace('\n',' ')
text = text.replace("(",'')
text = text.replace(")","")
text = text.replace('"','')
text = text.replace("'",'')
raw_text = text
raw_text = raw_text.replace('\n',' ')
raw_text = re.sub('\s+', ' ', raw_text)
text = text.replace(',','')
text = re.sub('[^0-9a-zA-Z.]',' ',text)
text = re.sub('\s+',' ',text)
#print(text)

#taking existing dictionary words to avoid as native words
native = ''

with open('./input/479k-english-words/customdictionary.txt') as f:
    words = f.readlines()
native = [word.strip() for word in words]
with open('./input/479k-english-words/dictionary1.txt') as f:
    words = f.readlines()
native = native + [word.strip() for word in words]
with open('./input/479k-english-words/indian_names.txt') as f:
    words = f.readlines()
native += [word.strip() for word in words]
with open('./input/479k-english-words/indian_cities.txt') as f:
    words = f.readlines()
native += [word.strip() for word in words]
#with open('./input/479k-english-words/indian_states.txt') as f:
#    words = f.readlines()
#native.append([word.strip() for word in words])
with open('./input/479k-english-words/english_names.txt') as f:
    words = f.readlines()
native += [word.strip() for word in words]
f.close()
native = ' '.join(native)
#print(native)
native = re.sub('\s+', ' ', native)
native = native.split(' ')
native.sort()
#native.sort()
#print(native)
#detecting names
names = []
names1 = []
text1 = text.replace('.',' ')
names1 = re.findall(r'[A-Z][a-z]*[0-9]*',text1)
#print(names1)
names = re.findall(r"name is [a-z]*",text.lower())
names.extend(re.findall(r'hi [a-z]*',text.lower()))
names.extend(re.findall(r'from [a-z]*',text.lower()))
names.extend(re.findall(r'welcome to [a-z]*',text.lower()))
names.extend(re.findall(r'called [a-z]*',text.lower()))
names.extend(re.findall(r'left for [a-z]*',text.lower()))
names.extend(re.findall(r'going to [a-z]*',text.lower()))
names.extend(re.findall(r'called [a-z]*',text.lower()))
names.extend(re.findall(r'heading [a-z]*', text.lower()))
names.extend(re.findall(
    r'([a-z]* locality [a-z]*|[a-z]* city [a-z]*|[a-z]* town [a-z]*|[a-z]* village [a-z]*|[a-z]* district [a-z]*)', text.lower()))
names.extend(re.findall(r':\s*[a-z]*',raw_text.lower()))
names.extend(re.findall(r' [a-z]*[A-Z][a-z]*', text))
names.extend(re.findall('\\b(?:[a-zA-Z]\\.){2,}', text.lower()))
#print(raw_text)
# for email detection
names.extend(re.findall(r'[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$', raw_text))
# for website detection
names.extend(re.findall(r'(?:[a-zA-Z0-9-]+\.)+[A-Za-z]{2,6}$', raw_text))
#names.extend(re.findall(r'[a-z].[a-z&]{2,7}', text.lower()))
#print(names)
#convert list of names to a sentence
names.extend(names1)
detected_names = ''
for name in names:
    detected_names += name + ' '
#print(detected_names)

detected_names = detected_names.lower()
detected_names = re.sub('[^0-9a-zA-Z.@]', ' ', detected_names)
detected_names = re.sub('\s+', ' ', detected_names)
#print(detected_names)
#convert sentence to tokens
list1 = detected_names.split(' ')
#remove empty and repeated elements from list
while ('' in list1):
    list1.remove('')
list1 = list(set(list1))
list1.sort()
#print(list1)
#remove dictionary elements
final_names = ''
for name in list1:
    if name in native:
        list1.remove(name)
#print(list1)
print("names detected:")
inFile = open('./input/479k-english-words/customdictionary.txt','a+')
for word in list1:
    if word not in native:
        inFile.write('\n')
        inFile.write(word)
        print(word)
inFile.close()
f.close()
