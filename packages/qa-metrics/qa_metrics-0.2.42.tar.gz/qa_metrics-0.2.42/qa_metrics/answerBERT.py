import torch
from torch import inference_mode
from transformers import (AutoTokenizer,
                         AutoModelForSequenceClassification)
from typing import List, Optional
from torch.amp import autocast


# ────────────────────────────────────────────────────────────────
def _load_answer_bert(ckpt="zli12321/answerableBert", device=None):
   """Utility: load tokenizer+model once per actor."""
   device = device or torch.device(
       "cuda" if torch.cuda.is_available() else "cpu")
   tok   = AutoTokenizer.from_pretrained(ckpt)
   mdl   = (AutoModelForSequenceClassification
            .from_pretrained(ckpt)
            .to(device)
            .eval())
   return tok, mdl, device


class AnswerBertActor:
   """
   Ray wrapper that behaves like the old TransformerModelActor.
   """
   def __init__(self,
                ckpt_dir: str = "zli12321/answerableBert",
                max_len: int = 2048,
                device='cuda'):
       self.tok, self.model, self.device = _load_answer_bert(ckpt_dir, device=device)
       self.max_len = max_len


   # ---------- private helper ---------------------------------
   def _encode(self, text):
       return self.tok(text,
                       truncation=True,
                       padding="max_length",
                       max_length=self.max_len,
                       return_tensors="pt").to(self.device)


   # ---------- public API -------------------------------------
   @inference_mode()
   def compute_score(self, label: int, extracted_answer: str):
       """
       Mimics RewardBert.compute_score() signature.


       Returns (normalized_score, final_score) where
       • final_score = 1  if predicted label == provided *label*
       •              = 0  otherwise
       • normalized_score is P(predicted label == 1)


       Adjust this logic to whatever ‘score’ scheme you need.
       """
       logits = self.model(**self._encode(extracted_answer)).logits.squeeze(0)
       # prob   = torch.softmax(logits, dim=-1)     # [p0, p1]
       pred   = int(logits.argmax())
       # final  = 1 if pred == label else 0
       # norm   = float(prob[1])                    # P(label==1)
       # return norm, final
       return pred
   
   @inference_mode()
   def batch_predict(
       self,
       extracted_answers: List[str],
       batch_size: Optional[int] = 128
   ) -> List[int]:
       """
       Predict labels for a list of answers, batching efficiently:
         1) tokenize & move to GPU once
         2) do mixed-precision inference
         3) slice in true sub-batches if needed
       """
       n = len(extracted_answers)
       if n == 0:
           return []


       # pick a sensible batch size
       if batch_size is None or batch_size >= n:
           batch_size = n
       else:
           batch_size = min(batch_size, n)


       # 1) tokenize all inputs at once, send to device
       encodings = self.tok(
           extracted_answers,
           truncation=True,
           padding="max_length",
           max_length=self.max_len,
           return_tensors="pt"
       ).to(self.device)


       input_ids      = encodings["input_ids"]
       attention_mask = encodings["attention_mask"]
       token_type_ids = encodings.get("token_type_ids", None)


       # 2) if one-shot fits, do it and return
       if batch_size == n:
           with autocast("cuda", dtype=torch.float16):
               logits = self.model(**encodings).logits  # (n, num_labels)
           return logits.argmax(dim=-1).tolist()


       # 3) otherwise slice into sub-batches
       all_preds: List[int] = []
       for start in range(0, n, batch_size):
           end = start + batch_size
           batch_inputs = {
               "input_ids":      input_ids[start:end],
               "attention_mask": attention_mask[start:end],
           }
           if token_type_ids is not None:
               batch_inputs["token_type_ids"] = token_type_ids[start:end]


           with autocast("cuda", dtype=torch.float16):
               logits = self.model(**batch_inputs).logits  # (B, num_labels)
           preds = logits.argmax(dim=-1).tolist()
           all_preds.extend(preds)


       return all_preds




