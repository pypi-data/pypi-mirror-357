import torch
from torch import inference_mode
from transformers import (AutoTokenizer,
                         AutoModelForSequenceClassification)



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
   


