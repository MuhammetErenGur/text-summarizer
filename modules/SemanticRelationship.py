from transformers import BertTokenizer,BertModel
import torch
import threading


tokenizer = BertTokenizer.from_pretrained("bert-large-uncased")
model = BertModel.from_pretrained("bert-large-uncased")


def create_embeddings(text_index,embeddings,texts):
    text = texts[text_index]
    encoded_text = tokenizer(text, return_tensors='pt')
    with torch.no_grad():
        model_output = model(**encoded_text)
        embeddings[text_index] = model_output.last_hidden_state.mean(dim=1)



def create_threads(threadList,sentenceList,embeddings):
    for i in range(len(sentenceList)):
        thread = threading.Thread(target=create_embeddings, args=(i,embeddings,sentenceList,))
        thread.start()
        threadList.append(thread)
    for thread in threadList:
        thread.join()

def get_cos_similarity(embeddings,texts):
    simmilarity_list=[]
    for i in range(len(texts)):
        for j in range(i+1, len(texts)):
            cos_sim = torch.nn.functional.cosine_similarity(embeddings[i], embeddings[j], dim=1)
            simmilarity_list.append((i+1,j+1,round(cos_sim.item(),3)))
    return simmilarity_list

