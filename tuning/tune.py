from sentence_transformers import SentenceTransformer, InputExample, losses
from sentence_transformers.evaluation import BinaryClassificationEvaluator
from torch.utils.data import DataLoader
import pandas as pd

df = pd.read_csv("job_skill_pairs.csv")

train_samples = []
for i in range(len(df)):
    job_title = df.iloc[i]["job_title"]
    skills = df.iloc[i]["skills"]
    label = float(df.iloc[i]["label"])
    train_samples.append(InputExample(texts=[skills, job_title], label=label))

model = SentenceTransformer('all-MiniLM-L6-v2')

train_dataloader = DataLoader(train_samples, shuffle=True, batch_size=16)
train_loss = losses.CosineSimilarityLoss(model)

sentences1 = df["skills"].tolist()
sentences2 = df["job_title"].tolist()
labels = [float(x) for x in df["label"].tolist()]
evaluator = BinaryClassificationEvaluator(sentences1, sentences2, labels)

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    evaluator=evaluator,
    epochs=3,
    evaluation_steps=5,  
    warmup_steps=10,
    show_progress_bar=True,
    output_path="fine_tuned_model"
)
