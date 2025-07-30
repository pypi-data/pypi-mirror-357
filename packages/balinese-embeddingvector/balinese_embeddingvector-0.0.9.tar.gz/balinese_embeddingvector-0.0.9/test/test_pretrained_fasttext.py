
from balinese_embeddingvector.pretrained.BaliFastText import BaliFastText


pretrained_model = BaliFastText(
    huggingface_repo_ID='satriabimantara/balinese_pretrained_wordembedding').load_pretrained_model()
print(pretrained_model.wv['Satua'])
print(pretrained_model.wv.most_similar('Lutung'))