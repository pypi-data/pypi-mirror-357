import pandas as pd
import torch
import torch.nn.functional as F
from datasets import Dataset
import os
from cchenutils import read_id
from transformers import AutoTokenizer, AutoModel, Trainer, TrainingArguments


class PclGPTClassifier:

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("DUTIR-Wang/PclGPT-CN", trust_remote_code=True)
        self.model = AutoModel.from_pretrained("DUTIR-Wang/PclGPT-CN", trust_remote_code=True).half()
        self.pcl_ids = [self.tokenizer.encode(l, add_special_tokens=False)[0] for l in ['B', 'C', 'D']]

    def predict(self, text, batch_size=128):
        def tokenize(batch):
            return self.tokenizer(batch['text'], return_tensors='pt', padding=True)

        text = [("假定你是一名语言学家，检测居高临下言论。居高临下言论是优势地位群体针对弱势群体的优越言论，"
                 "语言攻击性较弱，但往往夹杂着讽刺，刻板印象，会对弱势群体造成伤害。"
                 "居高临下根据语气程度分为 A级：非居高临下（正常非歧视、非冷暴力言论），"
                 "B级：轻微居高临下（语气略带鼓励或怜悯），C级：中等居高临下（说话人较为客观陈述，但语气带有歧视），"
                 "D级：严重居高临下（说话人语气轻蔑，严重歧视弱势群体）。"
                 "接下来将给你一段文本，根据上述规则，你负责判断该文本属于（A/B/C/D级）的哪一级，并只回答选项。"
                 "-> 文本：({})").format(t) for t in text]
        dataset = Dataset.from_dict({'text': text}).map(tokenize, batched=True)

        trainer = Trainer(
            model=self.model,
            tokenizer=self.tokenizer,
            args=TrainingArguments(output_dir='./tmp', per_device_eval_batch_size=batch_size),
        )
        preds = trainer.predict(dataset)
        logits = preds.predictions  # shape: (n_samples, seq_len, vocab_size)
        next_token_logits = torch.tensor(logits[0][:, -1, :])  # last token in sequence
        probs = F.softmax(next_token_logits.float(), dim=-1)
        return probs[:, self.pcl_ids].cpu().numpy().tolist()


if __name__ == '__main__':
    batch_size = 16
    fp_src = '../filtered/comments.csv'
    fp_dst = 'D:/comments_pclgpt.csv'

    is_first_write = not os.path.exists(fp_dst)
    done_cids = read_id(fp_dst, ids='cid')
    clf = PclGPTClassifier()

    reader = pd.read_csv(fp_src, usecols=['cid', 'text'], dtype=str, chunksize=batch_size)
    for df in reader:
        df[['mild', 'moderate', 'severe']] = clf.predict(df.pop('text').to_list(), batch_size=batch_size)
        df.to_csv(fp_dst, mode='a', header=is_first_write, index=False)
        is_first_write = False
        done_cids |= set(df['cid'])
